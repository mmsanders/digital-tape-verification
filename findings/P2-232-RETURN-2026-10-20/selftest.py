"""Causal inventory controls for transport replay; no executable is launched."""
import copy
from replay import check_inventory, sha
data={'a':b'actual raw bytes','b':b'other bytes'}
inv={n:dict(bytes=len(b),sha256=sha(b)) for n,b in data.items()}
check_inventory(data,inv)
mutations=[{'a':data['a']},{**data,'extra':b''},{**data,'a':b'actual RAW bytes'},{**data,'a':data['a']+b'!'}]
for d in mutations:
 try: check_inventory(d,inv)
 except AssertionError: pass
 else: raise AssertionError('corrupt/incomplete transport escaped')
print('PASS inventory positive and 4 detecting loss/extra/byte/length controls; no execution')
