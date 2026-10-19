"""Exact-source OS-query fixtures; no native-device or Product execution claim.

Compare complete/empty listings and a positively identified partition with real
errno-style failures at the query boundary, including missing stack metadata.
The independently issued rule is unchanged: unknown ownership cannot become safe.
"""
import argparse, hashlib, importlib.util, json, subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
HEAD = '0918e7d02030868f4f8f21059c6a190cbe7a0f62'
SHA = 'da371434f4ee2d49410c75f19dca242a5af1a354a6f4a98bc84638c98cd6995e'
PRELUDE = r'''
#define _GNU_SOURCE
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <dirent.h>
#include <limits.h>
#include <errno.h>
struct mnt { char disk[64]; char name[64]; int system; };
static struct mnt g_mnt[256];
static int g_nmnt, g_mnt_unknown, g_os_unresolved;
static int mode, sent;
static int fixture_access(const char *p, int flags) {
  (void)flags;
  if (strstr(p,"dm-0/partition")) {errno=ENOENT;return -1;}
  return 0;
}
static DIR *fixture_opendir(const char *p) {
  if (strstr(p,"dm-0/slaves")) {
    if (mode==1 || mode==2 || mode==5) {
      errno=mode==1 ? EACCES : mode==2 ? EIO : ENOENT;
      return NULL;
    }
    return (DIR*)1;
  }
  /* A known partition legitimately has no slaves directory. */
  errno=ENOENT;return NULL;
}
static struct dirent *fixture_readdir(DIR *d) {
  static struct dirent ent;
  if(d==(DIR*)1) {
    if(mode==3 || (mode==4 && sent)) {errno=EIO;return NULL;}
    if(mode==6) {return NULL;} /* successfully empty whole-device listing */
    if(!sent++) {strcpy(ent.d_name,"loop0p1");return &ent;}
  }
  return NULL;
}
static int fixture_closedir(DIR *d) {(void)d;return 0;}
static char *fixture_realpath(const char *p, char *out) {
  (void)p;strcpy(out,"/sys/devices/virtual/block/loop0/loop0p1");return out;
}
#define access fixture_access
#define opendir fixture_opendir
#define readdir fixture_readdir
#define closedir fixture_closedir
#define realpath fixture_realpath
#define F_OK 0
#define DISC_FAULT(x) 0
'''
MAIN = r'''
int main(void) {
  for (mode=0;mode<=7;mode++) {
    g_nmnt=g_mnt_unknown=g_os_unresolved=sent=0;
    add_use(mode==7 ? "loop0p1" : "dm-0",0);
    printf("%d %d %d %d %s\n",mode,g_mnt_unknown,g_os_unresolved,g_nmnt,g_nmnt?g_mnt[0].disk:"none");
  }
  return 0;
}
'''

def run(product, out):
    out.mkdir(parents=True, exist_ok=True)
    raw = (product/'host/port/discover_linux.c').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SHA
    path = HERE.parent/'P2-208-R2-2026-10-19/reproduce.py'
    s = importlib.util.spec_from_file_location('old_extractor', path)
    old = importlib.util.module_from_spec(s); s.loader.exec_module(old)
    code = PRELUDE+'\n'+'\n'.join(old.function(raw.decode(), n) for n in ['parent_disk','record_use','resolve_use','add_use'])+MAIN
    c = out/'fixture.c'; c.write_text(code)
    subprocess.run(['cc','-std=c99','-Wall','-Wextra',str(c),'-o',str(out/'fixture')], check=True, capture_output=True)
    stdout = subprocess.check_output([str(out/'fixture')], text=True)
    expected = ['0 0 0 1 loop0','1 1 0 0 none','2 1 0 0 none','3 1 0 0 none',
                '4 1 0 1 loop0','5 0 0 1 dm-0','6 0 0 1 dm-0','7 0 0 1 loop0']
    assert stdout.splitlines() == expected, stdout
    result = dict(source=HEAD, source_sha256=SHA, fixture_sha256=hashlib.sha256(code.encode()).hexdigest(),
                  scope='compiled exact-source OS-query fixtures; no native race/device execution',
                  raw_stdout=stdout,
                  controls=['complete dm slave attribution PASS','EACCES unknown PASS','EIO unknown PASS',
                            'readdir EIO before first entry PASS','readdir EIO after entry PASS',
                            'whole-device slaves ENOENT incorrectly becomes known leaf',
                            'successful empty listing retained','known partition ENOENT retains parent'],
                  disposition='overall S2 PASS withheld: ENOENT alone does not positively establish a non-stacked whole device')
    (out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__ == '__main__':
    p=argparse.ArgumentParser();p.add_argument('--product',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();run(a.product,a.out)
