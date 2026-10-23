"""Pure expectations for declared557 ordinary-file port. Not filesystem/process proof."""
import copy
import hashlib

SIZE=20972032
h=hashlib.sha256()
for _ in range(SIZE//512):h.update(bytes(512))
ZERO=h.hexdigest()

def qualify(r):
    twins=r['twins'];assert len(twins)==2 and twins[0]['identity']!=twins[1]['identity']
    for t in twins:
        assert t['ordinary_owned'] and not t['reparse'] and not t['sparse']
        assert t['bytes']==SIZE and t['allocated_bytes']>=SIZE and t['initial_sha256']==ZERO
        assert t['open_mode']=='existing' and not t['truncate']
    assert not r['calls_hport_os_create'] and not r['sparse_ioctl'] and not r['device_branch']
    assert r['same_uuid_epoch_input_fault'] and r['source_sentinel_unchanged']
    assert r['retained_session_closed_by_owner_only'] and not r['fault_closes_retained_handle']
    assert r['fault_rule_shared_with_reference']
    return True

def controls():
    t=dict(identity='A',ordinary_owned=True,reparse=False,sparse=False,bytes=SIZE,allocated_bytes=SIZE,initial_sha256=ZERO,open_mode='existing',truncate=False)
    other=copy.deepcopy(t);other['identity']='B'
    r=dict(twins=[t,other],calls_hport_os_create=False,sparse_ioctl=False,device_branch=False,same_uuid_epoch_input_fault=True,
           source_sentinel_unchanged=True,retained_session_closed_by_owner_only=True,fault_closes_retained_handle=False,fault_rule_shared_with_reference=True)
    qualify(r)
    bad=[]
    for k,v in [('sparse',True),('reparse',True),('bytes',20*1024*1024),('truncate',True),('open_mode','create')]:
        x=copy.deepcopy(r);x['twins'][0][k]=v;bad.append(x)
    for k in ['calls_hport_os_create','sparse_ioctl','device_branch','fault_closes_retained_handle']:
        x=copy.deepcopy(r);x[k]=True;bad.append(x)
    x=copy.deepcopy(r);x['twins'][1]['identity']='A';bad.append(x)
    x=copy.deepcopy(r);x['fault_rule_shared_with_reference']=False;bad.append(x)
    for x in bad:
        try:qualify(x)
        except AssertionError:continue
        raise AssertionError('invalid ordinary-file admission survived')
    print('PASS pure ordinary-existing/twin/fault causal controls; ZERO file/Product/native execution')

if __name__=='__main__':controls()
