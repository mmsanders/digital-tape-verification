"""Harmless raw-row neighbours for retained review; no private packet required."""
import copy,json
from pathlib import Path
from review import probe_checks
from native_receipts import windows_proof
def run():
 src=r'C:\fixture\.DEST.ingest-stage-abc';dest=r'C:\fixture\DEST'
 def row(op,path='',detail='',pid='1',name='ingest.exe',i=0):return {'Index':str(i),'Operation':op,'Path':path,'Detail':detail,'PID':pid,'Process Name':name,'Result':'SUCCESS'}
 rows=[row('CreateFile',src,'Disposition: Create, Options: Directory')]
 for name in ('audio.wav','manifest.json'):
  path=src+'\\'+name
  rows += [row('CreateFile',path,'Disposition: Create, Generic Write'),row('FlushBuffersFile',path),row('CloseFile',path)]
 rows.append(row('SetRenameInformationFile',src,'ReplaceIfExists: False, FileName: '+dest,i=7))
 n={'argv':['ingest.exe','--out',dest],'events':[{'op':'publish_dir_noreplace'}]}
 assert len(windows_proof(rows,n))==1
 results={'native-positive':'PASS'}
 bad=copy.deepcopy(rows);bad[-1]['Detail']=bad[-1]['Detail'].replace('False','True')
 for name,test in [('replacement',bad),('missing-flush',[r for r in rows if r['Operation']!='FlushBuffersFile'])]:
  try:windows_proof(test,n)
  except AssertionError:results[name]='REJECTED'
  else:raise AssertionError(name)
 probe=[row('Process Start',name='probe-parent.exe'),row('Process Start',pid='2',name='probe-child.exe'),
        row('CreateFile',r'C:\fixture\probe.txt'),row('CreateFile',r'C:\fixture\probe.txt'),
        row('CreateFile',r'C:\fixture\created.txt'),row('CreateFile',r'\Device\Harddisk0\DR0'),
        row('Process Exit',detail='Exit Status: 0'),row('Process Exit',detail='Exit Status: 0',pid='2')]
 assert probe_checks(probe);results['probe-positive']='PASS'
 bads={'missing-child':[r for r in probe if r['Process Name']!='probe-child.exe'],
       'one-probe-open':[r for i,r in enumerate(probe) if i!=2],
       'missing-creation':[r for r in probe if not r['Path'].endswith('created.txt')],
       'missing-forbidden-open':[r for r in probe if 'Harddisk0' not in r['Path']],
       'missing-completion':[r for r in probe if r['Operation']!='Process Exit']}
 for name,test in bads.items():
  try:probe_checks(test)
  except AssertionError:results[name]='REJECTED'
  else:raise AssertionError(name)
 r=json.loads((Path(__file__).parent/'RESULT.json').read_text())
 c=json.loads((Path(__file__).parent/'CARRY.json').read_text())
 assert r['counts']['global_csv_rows']==sum(r['counts'][k] for k in ['raw_csv_case_comparison_rows','selftest_rows','independently_partitioned_shipping_rows'])==595954
 assert r['counts']['native_traces']==1931 and r['counts']['publications']==1645 and r['counts']['flush_close_pairs']==3290
 assert c['equal_math_cases']==1640 and not c['different_math_cases'] and not c['missing_math_cases']
 assert len(r['observer_controls'])==4 and all(v['missing_rows']>0 for v in r['observer_controls'].values())
 print(json.dumps(results,indent=2));print('Bounded private-run result checks PASS; no private packet or numerical campaign in CI')
if __name__=='__main__':run()
