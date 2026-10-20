"""Carry prior independently accepted numeric predicates by unchanged bytes only."""
import argparse,gzip,hashlib,json,zipfile
from pathlib import Path
def sha(b):return hashlib.sha256(b).hexdigest()
def run(packet,accepted,out):
 b=accepted.read_bytes();assert sha(b)=='f06195bf142d58a3cab035f2f0e26dfa11b93b9acb245d5fb7b8cb577b1b1c26'
 raw=gzip.decompress(b);assert sha(raw)=='8d4fb1f5f91eecc1c2d735eb21ae5b816ef76db4e5ae9df35a1fcb558d2a94a7'
 prior=json.loads(raw);equal=[];different=[];missing=[]
 with zipfile.ZipFile(packet) as z:
  idx=json.loads(z.read('INDEX.json'))
  for key,p in prior['math_case_results'].items():
   if not key.startswith('linux:'):continue
   id=key[len('linux:'):]
   if id not in idx['cases']:missing.append(id);continue
   r=json.loads(z.read(idx['cases'][id]))
   if 'wav' not in r:missing.append(id);continue
   wav=z.read(r['wav']);manifest=z.read(r['manifest'])
   # Only declared tool-version metadata changes; no waveform or tolerance normalization.
   old_version=b'"tool_version":"0.1.0"'
   new_version=('"tool_version":"'+idx['tool_version']+'"').encode()
   assert manifest.count(new_version)==1
   normalized=manifest.replace(new_version,old_version)
   before=[sha(z.read(f)) for f in r['before']]
   checks={'pcm':sha(wav[44:])==p['pcm'],'before':before==p['before'],'manifest_except_tool_version':sha(normalized)==p['manifest']}
   if all(checks.values()):equal.append(id)
   else:different.append({'id':id,'checks':checks})
 result={'accepted_result_compressed_sha256':sha(b),'accepted_result_uncompressed_sha256':sha(raw),
  'accepted_candidate':prior['candidate'],'new_candidate':idx['candidate_sha'],
  'equal_math_cases':len(equal),'different_math_cases':different,'missing_math_cases':missing,
  'method':'Exact pre-gain float/PCM/manifest identity; only literal declared tool_version field changed; no full numerical recomputation',
  'binding_census_sha256':sha(json.dumps(sorted(equal),separators=(',',':')).encode())}
 out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('packet',type=Path);p.add_argument('accepted',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args();run(a.packet,a.accepted,a.out)
