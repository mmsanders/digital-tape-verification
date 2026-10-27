"""338 scoped public projection checks. Originals were independently audited privately.
No Product imports, process execution, path substitution or timestamp normalization.
"""
import copy,json,re
from pathlib import Path
def check(e):
    assert e['head']=='d384624ae375ab77368eb01afc146d3d907c6e1e'
    assert e['manifest_sha256']=='2587631c4bdabf8ef6595b80ad788bb941a27544f8aebd7ed25f19ef607247a8'
    assert len(e['original_hashes'])==17
    assert e['original_hashes']['raw/C01-C02/console.json']=='83891e2c235bd048b8fdcb454ff2ecda94ae63dc5f6393f634bf4e6de63d739d'
    assert e['original_hashes']['raw/C01-C02/command.json']=='00a31508f1c03c1d9d0627e291da5bf1f200de75b9dc34812ad65583fddc3a6c'
    assert e['helper_sha256']=='64fc71733133f5310ad2c3d3a59815c4c6d465f719180fa9b15dca4f640845cc'
    assert e['runner_sha256']=='513796f599e1489f41fd61a7728d5538d98c7f97236ec50599a5f1ad4d9fea76'
    assert e['runner_console_window'] is True and e['runner_pid']>0
    assert e['named_test']=='bridge::diagnostics_component::c01_c02_console_association'
    assert (e['matched_tests'],e['passed'],e['filtered'])==(1,1,47)
    pins=e['compiled_pins']
    assert pins=={'DT_INGEST_SHA256':'3895f3f356c91b8a9fe870c33694da64bf2765df308bef118d657c1be4bb9a20','DT_INGEST_VERSION':'0.1.1 INGEST-1 arithmetic-profile INGEST1-AP4','DT_TAPECTL_SHA256':'44ef26869ba2d01a8a183660a2c7a050d0e7e9ff37c40b727131512739ea6ded','DT_TAPECTL_VERSION':'tapectl-wp15-s2+f9306c2c5a42'}
    for name,flags,want in [('C01',0x08000000,False),('C02',0,True)]:
        c=e['contrast'][name]
        assert c['flag']==flags and c['console_window'] is want
        assert c['pid']==c['receipt_pid']>0 and c['pid']!=e['runner_pid']
        assert type(c['os_start_ns']) is int and c['os_start_ns']==c['receipt_os_start_ns'] and 2**53<c['os_start_ns']<2**64
        assert c['child_argv_sha256']==c['receipt_argv_sha256'] and c['child_cwd_sha256']==c['receipt_cwd_sha256'] and c['exit']==0
        assert re.fullmatch('[0-9a-f]{32}',c['nonce'])
    assert e['contrast']['C01']['pid']!=e['contrast']['C02']['pid']
    assert e['contrast']['C01']['nonce']!=e['contrast']['C02']['nonce']
    assert e['contrast']['C01']['env_sha256']==e['contrast']['C02']['env_sha256']
    assert e['setup_stop']==dict(raw_records=0,test_execution_records=0,listing_tests=48)
def controls():
    e=json.loads((Path(__file__).parent/'EVIDENCE.json').read_text());check(e)
    mutations=[('runner',lambda x:x.update(runner_console_window=False)),('C01',lambda x:x['contrast']['C01'].update(console_window=True)),('C02',lambda x:x['contrast']['C02'].update(console_window=False)),('flag',lambda x:x['contrast']['C01'].update(flag=0)),('PID',lambda x:x['contrast']['C02'].update(receipt_pid=1)),('time',lambda x:x['contrast']['C01'].update(receipt_os_start_ns=1)),('argv',lambda x:x['contrast']['C01'].update(receipt_argv_sha256='0'*64)),('source',lambda x:x.update(head='0'*40)),('zeroTests',lambda x:x.update(matched_tests=0)),('pins',lambda x:x['compiled_pins'].update(DT_TAPECTL_SHA256='0'*64)),('helper',lambda x:x.update(helper_sha256='0'*64))]
    for name,mutate in mutations:
        b=copy.deepcopy(e);mutate(b)
        try:check(b)
        except AssertionError:continue
        raise AssertionError('negative survived:'+name)
    print('PASS authenticated scoped projection +11 causal negatives; actual originals audited separately; ZERO Product/process execution')
if __name__=='__main__':controls()
