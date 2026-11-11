"""Guard for Python offline tools under test, not a Product interface."""
import os,runpy,sys,types
from pathlib import Path
script=Path(sys.argv[1]).resolve();root=Path(sys.argv[2]).resolve();out=Path(sys.argv[3]).resolve();allow_git=sys.argv[4]=='git';args=sys.argv[5:];sys.argv=[str(script),*args];sys.path.insert(0,str(script.parent))
fake=types.ModuleType('serial')
def fail(event):
 print('AUDIT_VIOLATION '+event,file=sys.stderr);raise RuntimeError('offline boundary')
def noport(*a,**k):fail('serial-port')
fake.Serial=noport;fake.SerialException=RuntimeError;sys.modules['serial']=fake
calls=0
def audit(event,args):
 global calls
 if event.startswith('socket.') or event in ('os.system','os.remove','os.rmdir','os.rename','os.link','os.symlink'):fail(event)
 if event=='subprocess.Popen':
  command=args[1];parts=list(command) if isinstance(command,(list,tuple)) else []
  if not allow_git or not parts or Path(str(parts[0])).name.lower() not in ('git','git.exe'):fail(event)
  parts=[str(p) for p in parts[1:]]
  if parts and parts[0]=='-C':parts=parts[2:]
  if not parts or parts[0] not in ('rev-parse','status') or '-c' in parts or any(p.startswith('--exec-path') for p in parts):fail('git-command')
  calls+=1
  if calls>2:fail('extra-git-command')
 if event=='open' and not isinstance(args[0],int):
  path=Path(args[0]).resolve();mode=args[1];flags=args[2] or 0;write=bool(flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC)) or isinstance(mode,str) and any(c in mode for c in 'wax+')
  ok=path==out and bool(flags&os.O_EXCL) if write else path==script or root in path.parents or Path(sys.base_prefix) in path.parents or path.suffix in ('.py','.pyc','.pyd','.dll','.so')
  if not ok:fail('file '+str(path))
sys.addaudithook(audit);runpy.run_path(str(script),run_name='__main__')
