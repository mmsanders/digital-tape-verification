"""Independent feasibility observations only; not an ingest tool or acceptance oracle."""
import hashlib, json, math, platform, struct, subprocess, sys, tempfile, wave, zipfile
from pathlib import Path
out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
logs = []; results = {}
def run(args):
    p = subprocess.run(args, capture_output=True)
    logs.append({'argv': args, 'returncode': p.returncode, 'stdout': p.stdout.decode(errors='replace'), 'stderr': p.stderr.decode(errors='replace')})
    if p.returncode: raise RuntimeError(args)
    return p.stdout
run(['ffmpeg', '-version']); run(['ffprobe', '-version'])
results['runtime'] = {'python': sys.version, 'platform': platform.platform()}
with tempfile.TemporaryDirectory() as tmp:
    d = Path(tmp)
    def wav(name, n, rate=48000, kind='tone'):
        vals = []
        for i in range(n):
            v = 0 if kind == 'silence' else (29000 if kind == 'crest' and i == n//2 else round((100 if kind == 'crest' else 4000)*math.sin(2*math.pi*997*i/rate)))
            vals.extend([v,v])
        data = struct.pack('<'+'h'*len(vals), *vals)
        with wave.open(str(d/name), 'wb') as w:
            w.setparams((2,2,rate,n,'NONE','not compressed')); w.writeframes(data)
        results[name] = {'frames':n,'rate':rate,'sha256':hashlib.sha256((d/name).read_bytes()).hexdigest()}
    for name,n,kind in [('tone.wav',48000,'tone'),('short.wav',4800,'tone'),('silence.wav',96000,'silence'),('crest.wav',96000,'crest')]:
        wav(name,n,kind=kind)
        run(['ffmpeg','-hide_banner','-nostats','-i',str(d/name),'-af','loudnorm=I=-16:TP=-1:LRA=50:print_format=json','-f','null','-'])
    wav('a.wav',6001); wav('b.wav',6001)
    with wave.open(str(d/'a.wav'),'rb') as w: a=w.readframes(w.getnframes())
    with wave.open(str(d/'b.wav'),'rb') as w: b=w.readframes(w.getnframes())
    with wave.open(str(d/'ab.wav'),'wb') as w: w.setparams((2,2,48000,12002,'NONE','not compressed')); w.writeframes(a+b)
    def pcm(name, filt):
        return run(['ffmpeg','-hide_banner','-nostats','-i',str(d/name),'-af',filt,'-f','s16le','-acodec','pcm_s16le','-'])
    # Binary stdout is preserved as size/hash; replace its text in the command log.
    def observe(name, filt):
        data=pcm(name,filt); raw_name=f'observation-{len(logs):02d}.s16le'; (d/raw_name).write_bytes(data); logs[-1]['stdout']={'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'archive_member':raw_name}; return data
    filt='aresample=44100:resampler=swr:dither_method=none'
    x=observe('a.wav',filt); y=observe('b.wav',filt); z=observe('ab.wav',filt)
    results['resample']={'alone_frames':[len(x)//4,len(y)//4],'stateful_frames':len(z)//4,'same_bytes':x+y==z}
    for engine in ['swr','soxr']:
        data=observe('tone.wav',f'aresample=44100:resampler={engine}:dither_method=triangular')
        results[engine]={'frames':len(data)//4,'sha256':hashlib.sha256(data).hexdigest()}
    quiet=observe('silence.wav','aresample=44100:osf=s16:dither_method=triangular')
    # Integer input may bypass dither; force float before the final reduction.
    quiet_float=observe('silence.wav','aformat=sample_fmts=flt,aresample=44100:osf=s16:dither_method=triangular')
    results['silence_quantization']={'integer_nonzero_bytes':sum(v!=0 for v in quiet),'float_nonzero_bytes':sum(v!=0 for v in quiet_float),'frames':len(quiet_float)//4}
    for ext,codec in [('mp3','libmp3lame'),('m4a','aac'),('aac','aac')]:
        target=d/f'tone.{ext}'
        run(['ffmpeg','-hide_banner','-nostats','-i',str(d/'tone.wav'),'-c:a',codec,'-b:a','192k',str(target)])
        run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(target)])
        data=observe(target.name,'anull')
        results[ext]={'decoded_frames':len(data)//4,'source_frames':48000,'encoded_sha256':hashlib.sha256(target.read_bytes()).hexdigest()}
    with zipfile.ZipFile(out/'reference-bytes.zip','w',compression=zipfile.ZIP_DEFLATED) as z:
        for f in sorted(d.iterdir()):
            info=zipfile.ZipInfo(f.name, (2026,10,14,0,0,0)); info.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(info,f.read_bytes())
(out/'commands.json').write_text(json.dumps(logs,indent=2)+'\n')
(out/'observations.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results,indent=2))
