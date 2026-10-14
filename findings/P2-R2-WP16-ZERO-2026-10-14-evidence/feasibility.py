"""Small independent R3 observations, not a complete INGEST-1 acceptance package."""
from pathlib import Path
import json, math, platform, sys
import numpy as np
import scipy
from scipy import signal
import model, numerics

rows=[]
for rate in (48000,64000,88200,96000,176400,192000):
    for profile in numerics.FILTERS:
        for f in (20,997,18000,22050,min(23000,rate/2-100),rate/2-100):
            x=np.cos(2*np.pi*f*np.arange(rate)/rate)[:,None]
            y=numerics.resample(x,rate,profile)[:,0]
            trim=numerics.FILTERS[profile]['width']*3
            z=y[trim:-trim];t=np.arange(trim,len(y)-trim)/44100
            alias=abs(((f+22050)%44100)-22050)
            coeff=np.linalg.lstsq(np.c_[np.cos(2*np.pi*alias*t),np.sin(2*np.pi*alias*t)],z,rcond=None)[0]
            db=float(20*np.log10(np.linalg.norm(coeff)))
            rows.append({'input_rate':rate,'profile':profile,'input_hz':f,'measured_gain_db':db,'transient_excluded_output_frames_each_end':trim,'output_frames':len(y),'kind':'passband' if f<=18000 else 'alias'})
meters=[]
for db in (-18,-23,-36,-60,-80):
    x=numerics.tone(44100,88200,1000,10**(db/20))
    meters.append({'vector':'stereo_1k','input_peak_dbfs':db,'lufs':numerics.loudness(x),'reconstructed_dbtp':numerics.peak(x)})
tp=numerics.tone(44100,44100,11025,.7,np.pi/4)
meters.append({'vector':'quarter_rate_phase45','sample_peak_dbfs':float(20*np.log10(np.max(np.abs(tp)))),'true_peak_16x_dbtp':numerics.peak(tp),'reference_64x_dbtp':numerics.peak(tp,64)})
special=[]
crest=numerics.tone(44100,44100,a=.003);crest[22050,:]=.88
for name,x in [('ordinary',numerics.tone(44100,44100)),('short',numerics.tone(44100,4410)),('silence',np.zeros((44100,2))),('gated_out',numerics.tone(44100,44100,a=1e-6)),('crest',crest)]:
    pcm,r=numerics.reference_source(x,44100,'ref_fir_a')
    special.append({'vector':name,'input_lufs':numerics.loudness(x),'input_dbtp':numerics.peak(x),'output_frames':len(pcm)//4,'output_sha256':model.digest(pcm),'applied_gain_db':r['gain'],'output_lufs':r['lufs'],'output_dbtp':r['peak'],'status':r['status']})
report={'runtime':{'python':sys.version,'platform':platform.platform(),'numpy':np.__version__,'scipy':scipy.__version__},'filters':numerics.FILTERS,'filter_vectors':rows,'meter_vectors':meters,'special_sources':special,'limits':['Feasibility vectors only, not full standard meter qualification or Product acceptance','No Product ingest implementation inspected or executed','Declared FIR transients excluded only in steady-state measurements; endpoint oracle authoring still pending']}
out=Path(sys.argv[1]);out.write_text(json.dumps(report,indent=2)+'\n')
print('Recorded',len(rows),'filter vectors,',len(meters),'meter observations and',len(special),'source families')
