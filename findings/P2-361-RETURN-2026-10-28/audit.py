"""361 actual-return offline audit only. No subprocess, native API, app or child execution."""
import datetime as dt,hashlib,importlib.util,json,os,re
from pathlib import Path
HERE=Path(__file__).resolve().parent
TESTS=Path(r'C:\Users\mrtro\Documents\ChatGPT\Digital-Tape Verification 2\verification277-local\tests')
KIT=Path(r'C:\Users\mrtro\DigitalTape-618-kit')
PUB='2ee4b6701e313a37191482a342254eb902c6fc7f'
def sha(b):return hashlib.sha256(b).hexdigest()
def raw(p):
    assert p.is_file() and not p.is_symlink()
    for q in (p,*p.parents):assert not getattr(q.lstat(),'st_file_attributes',0)&0x400
    return p.read_bytes()
def obj(p):return json.loads(raw(p).decode('utf-8-sig'))
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def stamp(s):return dt.datetime.fromisoformat(s.replace('Z','+00:00'))
method=load('v361_prepare',TESTS/'windows_poller_session_r2/prepare.py')
expected,pre=method.prepared(PUB)
assert pre==obj(KIT/'method361/PREPARED.json')
for n,b in expected.items():assert raw(KIT/'method361'/n)==b,n
f=obj(KIT/'receipts/native618-1/launch.private.json');ctx=obj(KIT/'receipts/native618-1/context.private.json');consent=obj(KIT/'consent618.json')
assert consent==f['consent'] and sha(raw(KIT/'consent618.json'))==f['consent_sha256']
assert consent['method_publication']==PUB and consent['command_sha256']==pre['command_sha256'] and consent['method_sha256']==pre['method_sha256']
assert consent['permission_mode']=='auto' and consent['per_command_prompt'] is False
assert stamp(consent['publication_utc'])<stamp(consent['manual_resumption_utc'])<stamp(f['start_utc'])
transcript=Path(r'C:\Users\mrtro\.claude\projects\C--Users-mrtro-claude\c8e97079-3a8a-403d-ac16-fc9a10f175c7.jsonl')
lines=raw(transcript).splitlines();records=[json.loads(b) for b in lines]
def one(uuid):return next((i,r) for i,r in enumerate(records) if r.get('uuid')==uuid)
qi,q=one('b49405f6-6ed4-406c-a03d-43b0d966191f');ni,n=one('ea6696bf-6aff-4414-a135-e089152f91be');yi,y=one('94f54d91-0d1b-4958-bca0-32aa386d9194')
assert qi<ni<yi and n['type']==y['type']=='user'
assert n['message']['content']=='Not yet' and y['message']['content']==consent['human_message_text']=='Oops, I meant to click yes! Please proceed'
assert y['timestamp']==consent['manual_resumption_utc']
question=next(b for b in q['message']['content'] if b.get('type')=='tool_use')['input']
assert question['ask']=='Resume #618 and run the one session?'
assert '2ee4b670' in json.dumps(question) and 'c0ba92f7' in json.dumps(question)
assert not any(r.get('type')=='user' and isinstance(r.get('message',{}).get('content'),str) for r in records[ni+1:yi])
# Inspect only this qualified session's invocation window, not unrelated chat history.
native_calls=[];tool_rows=[]
for i,r in enumerate(records[yi:],yi):
    t=r.get('timestamp','')
    if t and t>'2026-10-28T18:30:00Z':break
    for b in r.get('message',{}).get('content',[]) if isinstance(r.get('message',{}).get('content'),list) else []:
        if b.get('type')!='tool_use':continue
        cmd=b.get('input',{}).get('command','')
        if b.get('name')=='PowerShell':
            assert not re.search(r'(?im)^\s*(?:&\s+)?Set-ExecutionPolicy\b',cmd)
            if pre['command'] in cmd.splitlines():
                native_calls.append(dict(uuid=r['uuid'],record_sha256=sha(lines[i]),tool_use_id=b['id'],timeout=b['input'].get('timeout')))
            if 'Get-ExecutionPolicy -List' in cmd or 'PSExecutionPolicyPreference=[' in cmd:tool_rows.append((i,b['id']))
assert len(native_calls)==1
preflight_i,preflight=one('7e6a7e6a-52ff-4b8b-88ea-126402214b1d')
pf=next(b['content'] for b in preflight['message']['content'] if b.get('type')=='tool_result')
for text in ['Caption : Microsoft Windows 11 Home','S-1-16-8192','Group used for deny only','Process=Bypass','MachinePolicy=Undefined','UserPolicy=Undefined','CurrentUser=Undefined','LocalMachine=Undefined','Procs: 0','control exists: False','jobs entries: 0','receipts entries: 0']:
    assert text in pf,text
policy_i,policy=one('2bdd7919-2722-4ede-892f-308b2d6e5a7a')
assert 'PSExecutionPolicyPreference=[Bypass]' in next(b['content'] for b in policy['message']['content'] if b.get('type')=='tool_result')
# No active process/OS queries here: audit the preserved recorded context.
assert not ctx['token_elevated'] and not ctx['effective_admin'] and ctx==f['context']
assert ctx['parent_pid']==f['parent_pid'] and ctx['CurrentBuildNumber']=='26200' and ctx['DisplayVersion']=='25H2'
assert 'S-1-16-8192' in f['integrity_groups'] and not f['recorder_effective_admin']
assert ctx['python_executable']==json.loads(expected['METHOD.json'])['python']
assert f['method_publication']==PUB and f['method_sha256']==pre['method_sha256']
assert f['argv']==f['requested_argv']==[str(KIT/'Digital-Tape/digital-tape.exe'),'--diagnostic-receipts']
assert f['cwd']==str(KIT/'Digital-Tape') and ctx['cwd']==f['cwd']
parent=f['parent_identity'];assert parent['pid']==f['pid']==14180 and parent['start_ticks']==f['process_start_ticks']
ns=(f['process_start_ticks']-621355968000000000)*100
assert parent['os_start_ns']==ns and parent['image_path']==f['argv'][0]
assert parent['image_sha256']==json.loads(expected['METHOD.json'])['app_sha256']
assert stamp(f['launch_utc'])<stamp(parent['observed_utc'])<stamp(f['close_requested_utc'])<stamp(f['end_utc'])
assert 0<=f['ready_elapsed_ms']<=20000 and 0<=f['close_elapsed_ms']-f['ready_elapsed_ms']<=15000
assert 0<=f['normal_close_wait_ms']<=10000 and 0<=f['normal_close_elapsed_ms']<=10000
assert f['close_elapsed_ms']<=f['final_elapsed_ms']<=60000 and f['cleanup_elapsed_ms']==0
assert f['close_posted'] and f['graceful_exit'] and not f['forced_owned_cleanup'] and f['exit']==0 and f['capture_complete'] and f['diagnostic_copy_complete']
assert not any(f.get(k) for k in ['error','capture_error','collection_error','retention_error','cleanup_error'])
tail=f['samples'][-3:]
for s in tail:
    assert s['pid']==f['pid'] and s['start_ticks']==f['process_start_ticks'] and s['handle']>0 and s['title']=='Digital Tape'
    assert s['visible'] and s['responding'] and s['top_level'] and s['owner_handle']==0 and not s['ambiguous']
    assert len([w for w in s['observed_owned_windows'] if w['title']=='Digital Tape' and w['visible'] and w['top_level'] and w['owner_handle']==0])==1
for a,b in zip(tail,tail[1:]):assert b['seq']==a['seq']+1 and 250<=b['elapsed_ms']-a['elapsed_ms']<=1500 and b['handle']==a['handle']
assert tail[-1]['elapsed_ms']-tail[0]['elapsed_ms']>=1000 and tail[-1]['elapsed_ms']==f['ready_elapsed_ms']
assert f['preclose_owned_windows'][0]['handle']==tail[-1]['handle'] and f['preclose_owned_windows'][0]['pid']==f['pid']
assert f['close_reason']=='two-terminals' and f['live_samples'][-1]['terminal_count']==2
assert f['live_samples'][-1]['elapsed_ms']<=f['close_elapsed_ms'] and f['terminal_polls_observed']==2
oracle=load('v361_frozen_cards',TESTS/'windows_cards_receipts_r1/receipts.py')
diag=KIT/'receipts/native618-1/diagnostic'
files={p.relative_to(diag).as_posix():raw(p) for p in diag.rglob('*') if p.is_file()}
binding=dict(app_path=parent['image_path'],app_sha256=parent['image_sha256'],exe=str(KIT/'Digital-Tape/tapectl.exe'),sha256=json.loads(expected['METHOD.json'])['tapectl_sha256'],version_label=json.loads(expected['METHOD.json'])['tapectl_label'],private_root=r'C:\Users\mrtro\AppData\Local\org.digitaltape.app')
# Current ordinary file hashes bind originals; no archive/source reacceptance.
for key,path in [('app_sha256','app_path'),('sha256','exe')]:assert sha(raw(Path(binding[path])))==binding[key]
oracle_result=oracle.validate(files,binding,expect_complete=True)
rows=[oracle.parse(x) for x in files['records.jsonl'].splitlines()]
assert rows[0]['data']['app_pid']==f['pid'] and rows[0]['data']['app_os_start_ns']==ns and rows[0]['data']['source_commit']==f['source']
assert len(rows)==22 and rows[-1]['kind']=='session-end' and rows[-1]['data']==dict(complete=True,reason=None)
sid=rows[0]['session'];assert len(files)==8
# Current live source-tree comparison is unavailable: the read tool reported
# control missing and denied jobs listing. Do not retry/access through a new route.
assert set(x['name'] for x in f['diagnostic_manifest'])==set(files)
for entry in f['diagnostic_manifest']:assert len(files[entry['name']])==entry['bytes'] and sha(files[entry['name']])==entry['sha256']
assert f['post_jobs_status']=='empty' and f['post_jobs']==[]
for n in ['stdout.bin','stderr.bin']:assert raw(KIT/'receipts/native618-1'/n)==b'' and f[n+'_sha256']==sha(b'')
def manifest(path,before=False):
    out={}
    for line in raw(path).decode('utf-8-sig').splitlines():
        h,rest=line.split('  ',1);name=rest.rsplit('  ',1)[0] if before else rest
        assert re.fullmatch('[0-9a-f]{64}',h) and name not in out;out[name]=h
    return out
before=manifest(KIT/'MANIFEST.before.sha256',True);after=manifest(KIT/'MANIFEST.after.sha256')
assert len(before)==8 and len(after)==30 and all(after[n]==h for n,h in before.items())
# Rehash the new run/method originals, not accepted unchanged archive corpus.
for n,h in after.items():
    if n not in before:assert sha(raw(KIT/n))==h,n
inv={}
for p in [KIT/'MANIFEST.before.sha256',KIT/'MANIFEST.after.sha256',KIT/'consent618.json',KIT/'method361/PREPARED.json',*sorted((KIT/'receipts/native618-1').rglob('*'))]:
    if p.is_file():inv[p.relative_to(KIT).as_posix()]=dict(bytes=p.stat().st_size,sha256=sha(raw(p)))
runs=[]
for launch in (r['data'] for r in rows if r['kind']=='cards-launch'):
    rid=launch['run_id'];events={r['kind']:r['data'] for r in rows if r['data'].get('run_id')==rid and r['kind']!='cards-blob'}
    blobs={r['data']['role']:r['data'] for r in rows if r['kind']=='cards-blob' and r['data']['run_id']==rid}
    assert events['cards-terminal']['exit']==0 and events['cards-terminal']['end']=='exited' and events['cards-publication']['result']=='published' and events['cards-cleanup']['result']=='removed'
    offered,unprobed=oracle.discovery.stdout(files[blobs['stdout']['leaf']].decode('utf-8'))
    assert offered==[] and unprobed==0
    runs.append(dict(run_id=rid,ticket=launch['ticket'],pid_first_party=launch['pid'],terminal=events['cards-terminal']['end'],exit=0,publication='published',cleanup='removed',report_sha256=blobs['report']['sha256'],stdout_sha256=blobs['stdout']['sha256'],offered=0,unprobed=0))
result=dict(scope='361 StageB independent OFFLINE review of one actual session; no new execution',publication=PUB,software_return=6477282342,method_exact=True,manual_resumption='contextually bound human correction after Not yet; no fictional hash recitation/prompt',consent_question_record_sha256=sha(lines[qi]),consent_not_yet_record_sha256=sha(lines[ni]),consent_resume_record_sha256=sha(lines[yi]),native_invocation=native_calls[0],parent=dict(pid=f['pid'],os_start_ns=ns,ready_ms=f['ready_elapsed_ms'],close_ms=f['close_elapsed_ms'],after_ready_to_close_ms=f['close_elapsed_ms']-f['ready_elapsed_ms'],normal_close_ms=f['normal_close_elapsed_ms'],final_ms=f['final_elapsed_ms'],exit=0,forced_cleanup=False,blank_title_visible_top_level_also_enumerated=True),oracle=oracle_result,session=sid,records=len(rows),retained_leaf_count=len(files),retained_hashes_match_launcher_manifest=True,live_source_and_jobs_comparison='NOT ESTABLISHED in Verification context: diagnostic path missing and jobs listing denied; no retry or deletion inference; recorded after-state remains attributed',runs_source_bound_first_party=runs,manifests=dict(before_entries=8,after_entries=30,original_hash_entries_unchanged=True),inventory=inv,unsupported=['visible page/gesture/one-window-only','independent child/G1/no-device/no-write absence','current live-source/after-jobs independent confirmation','native A6/INGEST/S3/fullAPP/own-host/G2;7/12 unchanged'],native_executions_by_verification=0)
result['preflight_record_sha256']=sha(lines[preflight_i])
result['inherited_policy_record_sha256']=sha(lines[policy_i])
(HERE/'AUDIT.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='inventory'},indent=2))
