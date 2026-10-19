"""Narrow source-extracted control, not native device execution or Product fix.
Compile the exact candidate's four attribution functions with harmless OS-query
fixtures: known dm slave metadata, then failure to open that metadata directory.
No real /sys or device access occurs. A failed query must not become no slaves.
"""
import argparse, hashlib, json, subprocess
from pathlib import Path

def function(src, name):
    start=src.index('static ',src.rfind('\nstatic ',0,src.index(name+'('))+1)
    brace=src.index('{',start); depth=1; end=brace+1
    while depth:
        if src[end]=='{':depth+=1
        if src[end]=='}':depth-=1
        end+=1
    return src[start:end]

PRELUDE=r'''
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
static int denied, sent;
static int fixture_access(const char *p, int mode) {
  (void)mode;
  if (strstr(p,"dm-0/partition")) {errno=ENOENT;return -1;}
  return 0;
}
static DIR *fixture_opendir(const char *p) {
  if (strstr(p,"dm-0/slaves")) {
    if (denied) {errno=EACCES;return NULL;}
    return (DIR*)1;
  }
  return (DIR*)2;
}
static struct dirent *fixture_readdir(DIR *d) {
  static struct dirent ent;
  if(d==(DIR*)1 && !sent++) {strcpy(ent.d_name,"loop0p1");return &ent;}
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
MAIN=r'''
int main(void) {
  for (denied=0;denied<=1;denied++) {
    g_nmnt=g_mnt_unknown=g_os_unresolved=sent=0;
    add_use("dm-0",0);
    printf("%d %d %d %d %s\n",denied,g_mnt_unknown,g_os_unresolved,g_nmnt,g_nmnt?g_mnt[0].disk:"none");
  }
  return 0;
}
'''

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--product',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    path=a.product/'host/port/discover_linux.c';raw=path.read_bytes();src=raw.decode()
    pin=json.loads((Path(__file__).parent/'SOURCE.json').read_text())
    assert hashlib.sha256(raw).hexdigest()==pin['sha256']
    code=PRELUDE+'\n'+'\n'.join(function(src,n) for n in ['parent_disk','record_use','resolve_use','add_use'])+MAIN
    c=a.out/'fixture.c';c.write_text(code);binary=a.out/'fixture'
    subprocess.run(['cc','-std=c99','-Wall','-Wextra',str(c),'-o',str(binary)],check=True,capture_output=True)
    r=subprocess.run([str(binary)],check=True,capture_output=True,text=True)
    lines=r.stdout.splitlines();assert lines==['0 0 0 1 loop0','1 0 0 1 dm-0'],lines
    result={'scope':'compiled source-extracted OS-query fixture; no native disk execution',
            'source':pin,'raw_stdout':r.stdout,
            'known_slave_neighbour':'loop0 attribution retained',
            'denied_slaves_query':'defect reproduced: failure becomes dm-0 leaf, mount_unknown remains0',
            'disposition':'correction required; unresolved metadata must remain unknown'}
    (a.out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
