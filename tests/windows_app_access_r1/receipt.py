"""Receipt qualification only. No native/UI API or Product process."""
import copy

def qualify(r,app):
    assert r['spawned'] and r['pid']>0
    assert r['requested_argv']==r['argv']==[app]
    assert r['ui']=='UNEXECUTED','supervisor cannot assert UI success'
    assert not r.get('normal_quit',False),'UI/window evidence, not process helper, judges normal quit'
    return True

def controls():
    good=dict(spawned=True,pid=7,requested_argv=['owned.exe'],argv=['owned.exe'],ui='UNEXECUTED',forced_cleanup=True,exit=1)
    qualify(good,'owned.exe') # complete forced-cleanup receipt, never normal quit
    for k,v in [('argv',[]),('pid',0),('argv',['other.exe']),('ui','PASS'),('normal_quit',True)]:
        bad=copy.deepcopy(good);bad[k]=v
        try:qualify(bad,'owned.exe')
        except AssertionError:continue
        raise AssertionError('invalid receipt control survived')
    print('PASS argv/PID/claim-boundary controls; ZERO Product/UI execution')

if __name__=='__main__':controls()
