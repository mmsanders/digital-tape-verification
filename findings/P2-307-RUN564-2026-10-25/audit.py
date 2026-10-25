"""307 original run record audit; reads files only, no Product/native calls."""
import argparse,datetime as dt,hashlib,json,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--product',type=Path,required=True);p.add_argument('--workspace',type=Path,required=True);p.add_argument('--actual',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
HEAD='04562178e6d8f8fe7f470bf10c17da41b31e607f'
BASE='docs/REVIEW/software564/run-1/'
get=lambda path:subprocess.check_output(['git','-C',str(a.product),'show',HEAD+':'+BASE+path])
sha=lambda b:hashlib.sha256(b).hexdigest()
expected={'launch.private.json':(17009,'4d0697bc66c9d599d7e1e86d0f58b4123dfd2a0b42a1d2d299abfff190ab3da2'),
          'context.private.json':(829,'765bc22d5a673d5326a04f100b9608ad68664e158f6ff22dbc120a5915b6e19b')}
inventory={}
for name,(size,pin) in expected.items():
    b=get(name);assert len(b)==size and sha(b)==pin
    assert b==(a.actual/'run-1'/name).read_bytes()
    inventory[name]=dict(bytes=size,sha256=pin,original_matches_git=True)
r,c=json.loads(get('launch.private.json')),json.loads(get('context.private.json'))
assert r['context']==c
assert r['method_manifest_sha256']=='d28082644506472050220fa7080ec59df726114b10050552dcf9a8e797c96c8e'
assert r['source']=='266bdcaa760f702d6f685300cc9ca6e4491b6438'
assert r['build_sha256']=='0faf28103f4e76d75c392a22d7c8dbe7c33ac9732a7ff62a6a76738a358969f2'
assert r['pins']=={'digital-tape.exe':'ee4c84acb03655c4fb1344db1548ab283054eabe9caea9c2482b0181b39fa250','ingest.exe':'3895f3f356c91b8a9fe870c33694da64bf2765df308bef118d657c1be4bb9a20','tapectl.exe':'82798af2899e9364b9c9bfaa2021daf6cc51ccd0c6562598d50e0a86944bb7a9'}
artifact=a.actual/'Digital-Tape'
for name,pin in r['pins'].items(): assert sha((artifact/name).read_bytes())==pin
assert sha((artifact/'BUILD.json').read_bytes())==r['build_sha256']
app=str(artifact/'digital-tape.exe');assert r['cwd']==str(artifact) and r['argv']==r['requested_argv']==[app]
assert r['pid']==21552 and r['process_start_ticks']==639284927220048923
assert r['parent_pid']==c['parent_pid']==22192
assert r['recorder_effective_admin'] is False and c['effective_admin'] is False and c['token_elevated'] is False
assert c['python_executable']==r['python_path']==r'C:\Program Files\Inkscape\bin\python.exe'
assert c['python'].startswith('3.10.8 ') and c['architecture']=='AMD64' and c['CurrentBuildNumber']=='26200'
assert r['python_sha256']==sha(Path(r['python_path']).read_bytes())=='fbaff2f38852ac61c5767a91d5efbd4d893fb8ca985a9fdc76cf6d88fb93a745'
assert r['tool_route']==c['tool_route']=='approved-claude-code-exact-command'
prep=json.loads(get('method-307/PREPARED.json'))
assert prep==json.loads((a.actual/'method-307/PREPARED.json').read_bytes())
for name,pin in prep['files'].items():
    b=(a.workspace/'method307-runreview'/name).read_bytes()
    assert sha(b)==pin and b==(a.actual/'method-307'/name).read_bytes()
samples=r['samples'];assert len(samples)==4
stable=samples[1:]
assert [s['elapsed_ms'] for s in stable]==[865,1397,1943]
assert [s['seq'] for s in stable]==[1,2,3]
for s in stable:
    assert s['pid']==r['pid'] and s['start_ticks']==r['process_start_ticks'] and s['handle']==1246546
    assert s['title']=='Digital Tape' and s['visible'] is True and s['responding'] is True and s['top_level'] is True
    assert s['owner_handle']==0 and s['ambiguous'] is False
    owned=[x for x in s['observed_owned_windows'] if x['title']=='Digital Tape' and x['visible'] and x['top_level'] and x['owner_handle']==0];assert len(owned)==1
    for key in ['pid','handle','title','visible','responding','top_level','owner_handle']:assert owned[0][key]==s[key]
intervals=[stable[i+1]['elapsed_ms']-stable[i]['elapsed_ms'] for i in range(2)]
assert all(250<=i<=1500 for i in intervals) and stable[-1]['elapsed_ms']-stable[0]['elapsed_ms']>=1000
assert r['ready_elapsed_ms']==1943 and r['close_elapsed_ms']==2096 and r['close_elapsed_ms']<=20000
fresh=r['preclose_owned_windows'];assert len(fresh)==1
for key in ['pid','handle','title','visible','responding','top_level','owner_handle']:assert fresh[0][key]==stable[-1][key]
assert all(r[k] is True for k in ['native_window_ready','close_posted','graceful_exit','capture_complete'])
assert r['forced_owned_cleanup'] is False and r['exit']==0 and 'error' not in r
date=lambda s:dt.datetime.fromisoformat(s.replace('Z','+00:00'))
assert date(r['start_utc'])>date('2026-10-25T02:36:08Z')
assert date(r['start_utc'])<date(r['launch_utc'])<date(r['close_requested_utc'])<date(r['end_utc'])
close_upper=(date(r['end_utc'])-date(r['close_requested_utc'])).total_seconds()
assert 0<close_upper<10
for name in ['stdout.bin','stderr.bin']:
    b=(a.actual/'run-1'/name).read_bytes();assert b==b'' and sha(b)==r[name+'_sha256']
    inventory[name]=dict(bytes=0,sha256=sha(b),original_present=True,git_tracking='empty original omitted from Product tree; bytes/hash independently read')
assert sorted(x.name for x in (a.actual/'run-1').iterdir())==sorted(inventory)
assert r['page_readiness'].startswith('UNEXECUTED') and r['ui_interaction']=='UNEXECUTED' and r['selected_webview2_runtime'].startswith('UNAVAILABLE')
result=dict(run_commit=HEAD,pid=r['pid'],process_start_ticks=r['process_start_ticks'],handle=1246546,
            ready_elapsed_ms=1943,stable_span_ms=1078,stable_intervals_ms=intervals,close_posted_elapsed_ms=2096,
            close_to_final_receipt_upper_seconds=close_upper,exit=0,forced_owned_cleanup=False,inventory=inventory,
            native_measurement_predicates='PASS; unchanged offline judge also passed',build_archive='PASS carried exact315 disposition',
            other_owned_window_samples='Additional untitled visible and IME windows retained; no single-visual-window or page claim',
            approval_record='Producer-attested chat approval in auto mode; required one-time tool-prompt grant transcript NOT established by run receipts',
            overall='Fully admission-compliant qualification HELD on approval-record nonconformance; preserve measured facts, NO rerun/retry admitted',
            native_ui=False,reviewer_product_execution=False)
a.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print('PASS raw measurement/source/helper/context/window/quit/inventory audit; approval-prompt provenance remains NOT ESTABLISHED')
