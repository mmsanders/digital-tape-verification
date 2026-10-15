"""Evaluate candidate observation packets against the frozen complete census.
This emits a gate report, never an automatic shipping/physical acceptance.
"""
import argparse,json
from pathlib import Path
import numpy as np
import asset,audit,cases,formats,fixtures,model


def inside(root,name):
    p=(root/name).resolve();assert p.is_relative_to(root.resolve()),'escaping evidence path';return p

def check(root,source_root):
    root=Path(root);source_root=Path(source_root)
    index=json.loads((root/'INDEX.json').read_text());facts=json.loads((source_root/'SOURCES.json').read_text())
    assert asset.sha_file(source_root/'SOURCES.json')==json.loads((Path(__file__).parent/'ASSET.json').read_text())['sources_sha256']
    catalog=cases.expand(facts);assert not any(c.get('ruling_required') for c in catalog),'P2V16-002 unresolved; checkpoint not importable'
    observations=index['cases'];assert set(observations)=={c['id'] for c in catalog},'missing/extra cases; no waived matrix members'
    for key in ('candidate_sha','binary_sha256','tool_version','profile','platform','architecture','config_sha256'):assert index[key]
    assert (index['platform'],index['architecture']) in [('windows11','x64'),('macos','arm64'),('linux','x64')]
    results=[]
    for case in catalog:
        record=json.loads(inside(root,observations[case['id']]).read_text());code=record['exit'];expected=case['expected_exit']
        assert expected is None or code==expected or isinstance(expected,list) and code in expected,(case['id'],'exit')
        assert record['argv'] and record['stdout_file'] and record['stderr_file'] and record['config_sha256']==index['config_sha256']
        stdout=inside(root,record['stdout_file']).read_text();stderr=inside(root,record['stderr_file']).read_text()
        native=json.loads(inside(root,record['native_record']).read_text());assert native['exit']==code
        if case.get('scenario')=='informational':
            assert not native['dest_after'] and not native['owned_stage_after'] and not any(e['op'] in ('stage_create','output_open','device_open') for e in native['events'])
            assert stdout.strip()
            if case['id']=='cli/version':assert index['tool_version'] in stdout and index['profile'] in stdout
        else:
            audit.transaction(native)
        if code!=0 or case.get('scenario')=='informational':
            if code==2:
                assert stderr.strip(),case['id']+' unnamed refusal'
                if case['id'].startswith('asset/'):
                    assert case['folders'][0][0]['name'] in stderr,'source name missing'
                if case['id'].startswith('zero/') or case['id'] in ('asset/zero-192-n1.wav','asset/zero-192-n2.wav'):
                    assert 'too short' in stderr.lower() and any(e['name'] in stderr for folder in case['folders'] for e in folder if e['asset'].startswith('zero-'))
                if case['id'] in ('capacity/one-over','capacity/gap-one-over'):assert '1' in stderr and '00:01' in stderr,'exact overage diagnostic'
            results.append({'id':case['id'],'gates':'exit/native predicates checked'});continue
        pcm=model.pcm_from_wav(inside(root,record['wav']).read_bytes());raw=inside(root,record['manifest']).read_bytes()
        ordered=[];names=[]
        for folder in case['folders']:
            group=sorted(folder,key=lambda f:model.name_key(f['name']));names.append([f['name'] for f in group]);ordered.extend(group)
        source_facts=[]
        for entry in ordered:
            f=dict(facts[entry['asset']]);assert asset.sha_file(source_root/f['path'])==f['sha256'];f['source_sha256']=f['sha256'];source_facts.append(f)
        # Alternative raw decoder origins require an independent mapping review.
        # A Software-supplied arbitrary override is not admitted by this checker.
        manifest=audit.manifest(raw,pcm,source_facts,names,case['seconds'])
        assert manifest['tool_version']==index['tool_version'] and manifest['build_profile']==index['profile']
        assert len(record['before'])==len(ordered)
        for pos,(entry,f,s) in enumerate(zip(ordered,source_facts,manifest['sources'])):
            before=np.fromfile(inside(root,record['before'][pos]),dtype='<f8').reshape(-1,2)
            original=None
            if f['input_rate']==44100 and not f.get('lossy'):
                if f['container']=='wave':original,_=formats.generated_pcm((source_root/f['path']).read_bytes())
                else:
                    original=fixtures.signal(44100,256,f['input_channels']);original=np.rint(original*2**(f['bits']-1))/2**(f['bits']-1)
                if f['input_channels']==1:original=np.repeat(original,2,axis=1)
            start=s['start_frame']*4;chunk=pcm[start:start+s['output_frames']*4]
            audit.audio(before,chunk,s,original=original,mono=f['input_channels']==1,exact=entry['asset'].startswith('dither-'))
            if f.get('family')=='src-quality':audit.quality(before,f['input_rate'],f['frequency'],f['amplitude'],f['window_output_frames'])
        audit.joined(pcm)
        # Summary labels and counts must be visible; raw wording remains free.
        for word in ('peak','unmeasurable','gapless'):assert word in stdout.lower(),case['id']+' exception summary absent'
        results.append({'id':case['id'],'gates':'manifest/audio/quality/native predicates checked'})
    return {'candidate_sha':index['candidate_sha'],'profile':index['profile'],'platform':index['platform'],'cases':results,'status':'CHECKED; raw native/profile/decoder/qualification/relation review still mandatory'}

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('packet');ap.add_argument('--sources',required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    report=check(a.packet,a.sources);a.out.write_text(json.dumps(report,indent=2)+'\n');print(report['status'])
