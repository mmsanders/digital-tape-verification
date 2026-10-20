"""ADR190 supplement; explicit native request linkage is required, never inferred."""
import copy,json
def judge(record):
    reasons=[]
    base=record['base']
    if not base.get('complete_capture') or not base.get('binary_geometry_process_bound'):reasons.append('incomplete base binding')
    if base.get('lost_events')!=0 or base.get('lost_buffers')!=0:reasons.append('trace loss')
    if not base.get('last_sector_complete_success'):reasons.append('missing successful complete last-sector return')
    if base.get('target_writes',0) or base.get('target_flushes',0):reasons.append('target write/flush')
    if base.get('other_failures'):reasons.append('other base checker failure')
    events=record['remaining']; audit=[]
    for f in events:
        if f['layer']=='disk':continue
        if f['op']!='write':reasons.append('post-exit target/unknown/non-write event cannot be exempted');continue
        key=f.get('key');request=f.get('request')
        if not key or not request:reasons.append('missing/zero file key or request');continue
        if record.get('ambiguous_keys') or record.get('key_reuse'):reasons.append('conflicting/reused key lifetime');continue
        candidates=[d for d in events if d['layer']=='disk' and d['op']=='write' and d.get('key')==key and d.get('bytes')==f.get('bytes')]
        matches=[d for d in candidates if d.get('request')==request]
        if len(matches)!=1:reasons.append('no unique native request match; key/length/time alone insufficient');continue
        d=matches[0]
        if d.get('disk') is None or d['disk']==record['target_disk']:reasons.append('counterpart is target or unknown disk');continue
        if not d.get('request') or d.get('conflicting_identity'):reasons.append('unbound/conflicting DiskIo request');continue
        if f.get('offset') is None or d.get('offset') is None or not f.get('same_offset_coordinate') or f['offset']!=d['offset']:
            reasons.append('offset spaces not independently bound/agreed');continue
        if not f['time']<=d['time'] or d['time']-f['time']>record['request_window']:
            reasons.append('request time mismatch');continue
        audit.append({'file_record':f['n'],'disk_record':d['n'],'disk':d['disk'],'key':key,'request':request,'bytes':f['bytes'],'offset':f['offset']})
    owned=[x for a in audit for x in (a['file_record'],a['disk_record'])]
    if len(owned)!=len(set(owned)):reasons.append('multiply matched exclusion')
    if set(owned)!={e['n'] for e in events}:reasons.append('unproved remaining event')
    return {'verdict':'HELD' if reasons else 'PASS','reasons':sorted(set(reasons)),'excluded':audit,
            'scope':'separate ADR190 supplement; old checker verdict unchanged'}

def baseline():
    return {'base':{'complete_capture':True,'binary_geometry_process_bound':True,'lost_events':0,'lost_buffers':0,'last_sector_complete_success':True,'target_writes':0,'target_flushes':0,'other_failures':False},
        'target_disk':1,'request_window':100,'key_reuse':False,'ambiguous_keys':False,
        'remaining':[{'n':10,'layer':'file','op':'write','key':22,'request':33,'bytes':512,'offset':4096,'same_offset_coordinate':True,'time':10},
                     {'n':11,'layer':'disk','op':'write','key':22,'request':33,'bytes':512,'offset':4096,'disk':0,'time':11}]}

def controls():
    rows=[];b=baseline();assert judge(b)['verdict']=='PASS';rows.append({'case':'positively-linked-other-disk','verdict':'PASS'})
    mutations={
      'target-disk':lambda x:x['remaining'][1].update(disk=1),
      'missing-disk':lambda x:x['remaining'][1].update(disk=None),
      'missing-key':lambda x:x['remaining'][0].update(key=0),
      'different-key':lambda x:x['remaining'][1].update(key=23),
      'different-length':lambda x:x['remaining'][1].update(bytes=511),
      'different-request':lambda x:x['remaining'][1].update(request=34),
      'duplicate-counterpart':lambda x:x['remaining'].append(dict(x['remaining'][1],n=12)),
      'reused-key':lambda x:x.update(key_reuse=True),
      'ambiguous-lifetime':lambda x:x.update(ambiguous_keys=True),
      'same-target-different-stream':lambda x:x['remaining'][1].update(disk=1,stream='other-name'),
      'post-exit-target-read':lambda x:x['remaining'].append({'n':13,'layer':'file','op':'read','disk':1}),
      'post-exit-target-write':lambda x:x['base'].update(target_writes=1),
      'missing-completion-or-short-return':lambda x:x['base'].update(last_sector_complete_success=False),
      'lost-events':lambda x:x['base'].update(lost_events=1),
      'lost-buffers':lambda x:x['base'].update(lost_buffers=1),
      'different-offset':lambda x:x['remaining'][1].update(offset=8192),
      'unknown-coordinate-mapping':lambda x:x['remaining'][0].update(same_offset_coordinate=False),
      'reversed-time':lambda x:x['remaining'][1].update(time=9),
      'unknown-native-identity':lambda x:x['remaining'][1].update(conflicting_identity=True),
      'other-old-checker-failure':lambda x:x['base'].update(other_failures=True)}
    for name,mutate in mutations.items():
        bad=copy.deepcopy(b);mutate(bad);r=judge(bad);assert r['verdict']!='PASS',name;rows.append({'case':name,'verdict':r['verdict']})
    return rows
if __name__=='__main__':print(json.dumps(controls(),indent=2))
