"""Paper-method counterexample probe; never physical data or card acceptance."""
import importlib.util,json,sys
from pathlib import Path
p=Path(sys.argv[1]);s=importlib.util.spec_from_file_location('reviewed_atomicity_judge',p);m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m)
positive=dict(bus_mode='spi',busy_line='MISO',payload_complete=True,data_response_accepted=True,busy_entry_us=100,busy_sampled_us=149,cut_us=150)
assert m.qualifies(positive)[0]
late=dict(positive,busy_deassert_us=149);assert not m.qualifies(late)[0]
stale=dict(positive,busy_sampled_us=120,cut_us=1000000)
result=dict(scope='synthetic method probe, no physical observations',positive=m.qualifies(positive),known_late=m.qualifies(late),
            stale_busy_sample=m.qualifies(stale),finding='qualifies accepts arbitrarily stale pre-cut busy sample when deassertion is absent; physical edge/protocol proof must be supplied by the rig method')
assert result['stale_busy_sample'][0]
plan=dict(plan_version=3,run_id='synthetic-review374',sku='SYNTHETIC',revision='R',card_cid='synthetic-cid',block=1000,
          neighbour_offsets=list(m.NEIGHBOUR_OFFSETS),trials=[dict(iteration=i,cut_offset_fraction=0.5)for i in range(1,1002)])
plan['plan_digest']=m.plan_digest(plan)
neighbours={k:bytes([i+1]).hex()*512 for i,k in enumerate(m.NEIGHBOUR_OFFSETS)}
def row(n):
    return dict(positive,iteration=n,run_id=plan['run_id'],sku=plan['sku'],revision=plan['revision'],card_cid=plan['card_cid'],
                plan_digest=plan['plan_digest'],precondition_ok=True,precondition_readback_hex=m.pattern(n-1).hex(),
                readback_hex=m.pattern(n).hex(),neighbours=neighbours,neighbour_baseline=neighbours)
good=[row(i)for i in range(1,1001)];miss=row(1001);miss['busy_deassert_us']=149
miss['readback_hex']=(m.pattern(1000)[:256]+m.pattern(1001)[256:]).hex()
assert m.classify(bytes.fromhex(miss['readback_hex']),1001)=='TORN'
observed=m.judge([plan],good+[miss])
assert observed['verdict']=='PASS' and observed['torn_iterations']==[]
result['late_cut_torn_row']=dict(qualifying=observed['qualifying'],production_minimum_unchanged=m.REQUIRED_QUALIFYING,
                               classification='TORN',judge_verdict=observed['verdict'],reported_torn=observed['torn_iterations'],
                               finding='non-qualifying rows bypass target/neighbor classification; qualifying-count exclusion must not hide observed corruption')
print(json.dumps(result,indent=2))
