"""Pure synthetic causal controls, ZERO Windows/native/profile/workload execution."""
import copy,json
from model import fixture,judge,mapped

def run():
    good=fixture();assert judge(good).startswith('MODEL_CONTROL_PASS')
    positives=['explicit-parent-child']
    same=copy.deepcopy(good);same['edges'].pop(0);same['leaves'][0]['irp']=same['requests'][0]['irp'];judge(same);positives.append('identical-request')
    chain=copy.deepcopy(good);chain['edges'].append(dict(parent=2,child=3,time=17));chain['leaves'][0]['irp']=3;judge(chain);positives.append('explicit-two-edge-chain')
    split=copy.deepcopy(good);first=split['leaves'][0];first['bytes']//=2
    split['edges'].append(dict(parent=1,child=3,time=17));split['leaves'].append(dict(first,irp=3,offset=first['offset']+first['bytes']));judge(split);positives.append('two-disjoint-leaves')
    # Interval crossing must use every measured run, with no invented constant delta.
    mapping=copy.deepcopy(good['before']);mapping['runs']=[[0,64,100],[64,512,200]]
    assert mapped(mapping,0,512*1024)==[(0,1458176,1720320),(0,1867776,2129920)]
    positives.append('crossing-two-measured-runs')
    cases={
      'native-input-is-not-a-model':lambda m:m.update(scope='ACTUAL_NATIVE'),
      'admin-inherited-workload':lambda m:m['token'].update(integrity='High',elevated=True,origin='admin-terminal'),
      'token-unknown':lambda m:m['token'].update(integrity=None),
      'profile-missing-splitio':lambda m:m['profile']['keywords'].remove('SplitIO'),
      'extra-provider':lambda m:m['profile'].update(providers=2),
      'undeclared-buffers':lambda m:m['profile'].update(buffers=0),
      'unknown-event-layout':lambda m:m['unknown_schema'].append('unqualified-guid/opcode/version'),
      'OS-x64-not-header-proof':lambda m:m.update(pointer_header=4),
      'empty-before-allocation':lambda m:m['file'].update(allocation=0,prepared_before_baseline=False),
      'sparse-file':lambda m:m['file'].update(sparse=True),
      'compressed-file':lambda m:m['file'].update(compressed=True),
      'reparse-output':lambda m:m['file'].update(reparse=True),
      'existing-output':lambda m:m['file'].update(fresh_output=False),
      'fileid-substituted':lambda m:m['file'].update(id_after='FOREIGN'),
      'cleanup-foreign-id':lambda m:m['file'].update(cleanup_id='FOREIGN'),
      'unaligned-address':lambda m:m['file'].update(buffer_address=0x100001),
      'unknown-physical-alignment':lambda m:m['file'].update(alignment=0),
      'one-extent-dynamic-still-unsupported':lambda m:(m['before'].update(kind='dynamic'),m['after'].update(kind='dynamic')),
      'multiple-volume-extents':lambda m:(m['before'].update(extent_count=2),m['after'].update(extent_count=2)),
      'after-mapping-drift':lambda m:m['after'].update(disk_start=2*1048576),
      'historical-not-current-coordinate':lambda m:m['after'].update(base_sectors=8),
      'missing-lineage':lambda m:m['edges'].pop(0),
      'same-size-wrong-request':lambda m:m['leaves'][0].update(irp=999),
      'wrong-disk':lambda m:m['leaves'][0].update(disk=1),
      'same-disk-other-stream':lambda m:m['leaves'][0].update(file_key=999),
      'duplicate-counterpart':lambda m:m['leaves'].append(dict(m['leaves'][0])),
      'uncompleted-extra-descendant':lambda m:m['edges'].append(dict(parent=1,child=999,time=17)),
      'cycle-or-reused-child':lambda m:m['edges'].append(dict(parent=2,child=1,time=17)),
      'reused-live-request':lambda m:m['requests'][1].update(irp=1,start=10,end=25),
      'child-before-lineage':lambda m:m['leaves'][0].update(time=14),
      'completion-only-no-original':lambda m:m['leaves'].pop(0),
      'unknown-coordinate-base':lambda m:(m['before'].update(base_sectors=None),m['after'].update(base_sectors=None)),
      'extent-gap':lambda m:(m['before'].update(runs=[[1,512,100]]),m['after'].update(runs=[[1,512,100]])),
      'offset-one-byte-wrong':lambda m:m['leaves'][0].update(offset=m['leaves'][0]['offset']+1),
      'short-write':lambda m:m['requests'][0].update(returned=511),
      'failed-write-status':lambda m:m['requests'][0].update(status=1),
      'short-read':lambda m:m['read'].update(returned=4095),
      'failed-read':lambda m:m['read'].update(status=1),
      'missing-completion':lambda m:m['read'].update(returned=None),
      'boolean-is-not-native-status':lambda m:m['requests'][0].update(status=False),
      'post-exit-read':lambda m:m['read'].update(end=101),
      'lost-event':lambda m:m['window'].update(events_lost=1),
      'lost-buffer':lambda m:m['window'].update(buffers_lost=1),
      'late-start':lambda m:m['window'].update(start=2),
      'early-stop':lambda m:m['window'].update(stop=90),
      'not-drained':lambda m:m['window'].update(drained=99),
      'over-60s':lambda m:m['window'].update(stop=60001)}
    results=[]
    for name,mutate in cases.items():
        m=copy.deepcopy(good);mutate(m)
        try:judge(m)
        except ValueError as e:results.append(dict(case=name,result=str(e)))
        else:raise AssertionError('negative survived: '+name)
    return dict(scope='SYNTHETIC ONLY; no native decoder or execution admission',positives=positives,negatives=results)

if __name__=='__main__':print(json.dumps(run(),indent=2))
