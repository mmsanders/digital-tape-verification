"""Own effective token and OS facts only; no Product launch/provider/device probe."""
import argparse
import ctypes
from ctypes import wintypes as w
import json
import os
from pathlib import Path
import platform
import sys
import time

ROUTE='approved-exec-command-require-escalated'


def current(route):
    assert sys.platform=='win32' and route==ROUTE
    import winreg
    adv=ctypes.WinDLL('advapi32',use_last_error=True)
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    kernel.GetCurrentProcess.restype=w.HANDLE
    kernel.CloseHandle.argtypes=[w.HANDLE]
    adv.OpenProcessToken.argtypes=[w.HANDLE,w.DWORD,ctypes.POINTER(w.HANDLE)]
    adv.GetTokenInformation.argtypes=[w.HANDLE,ctypes.c_int,w.LPVOID,w.DWORD,ctypes.POINTER(w.DWORD)]
    adv.CreateWellKnownSid.argtypes=[ctypes.c_int,w.LPVOID,w.LPVOID,ctypes.POINTER(w.DWORD)]
    adv.CheckTokenMembership.argtypes=[w.HANDLE,w.LPVOID,ctypes.POINTER(w.BOOL)]
    token=w.HANDLE();elev=w.DWORD();used=w.DWORD()
    if not adv.OpenProcessToken(kernel.GetCurrentProcess(),8,ctypes.byref(token)): raise ctypes.WinError(ctypes.get_last_error())
    try:
        if not adv.GetTokenInformation(token,20,ctypes.byref(elev),ctypes.sizeof(elev),ctypes.byref(used)): raise ctypes.WinError(ctypes.get_last_error())
    finally: kernel.CloseHandle(token)
    sid=ctypes.create_string_buffer(68);size=w.DWORD(68);member=w.BOOL()
    if not adv.CreateWellKnownSid(26,None,sid,ctypes.byref(size)): raise ctypes.WinError(ctypes.get_last_error())
    if not adv.CheckTokenMembership(None,sid,ctypes.byref(member)): raise ctypes.WinError(ctypes.get_last_error())
    facts=dict(time_utc_ns=time.time_ns(),pid=os.getpid(),parent_pid=os.getppid(),cwd=os.getcwd(),
               os=platform.platform(),architecture=platform.machine(),python=sys.version,
               token_elevated=bool(elev.value),effective_admin=bool(member.value),
               tool_route=route,sandbox_mode='require_escalated (caller approval record required)',
               approval='caller attests tool approved this exact invocation; script cannot independently verify tool decision')
    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,r'SOFTWARE\Microsoft\Windows NT\CurrentVersion',0,winreg.KEY_READ|winreg.KEY_WOW64_64KEY) as key:
        for name in ['ProductName','EditionID','DisplayVersion','CurrentBuildNumber','UBR']:
            try: facts[name]=winreg.QueryValueEx(key,name)[0]
            except OSError as e: facts[name]={'unavailable':str(e)}
    return facts


def admit(facts):
    assert not facts['token_elevated'] and not facts['effective_admin'], 'STOP: ordinary non-admin effective token required'
    assert facts['tool_route']==ROUTE


def ordinary(p,directory=False):
    p=p.absolute();s=str(p)
    assert not s.startswith(('\\\\','//','/dev/')) and ':' not in s[2:]
    for q in (p,*p.parents):
        st=q.lstat();assert not q.is_symlink() and not getattr(st,'st_file_attributes',0)&0x400
    assert p.is_dir() if directory else p.is_file()


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--route',required=True,choices=[ROUTE]);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    ordinary(a.output.parent,True);assert not a.output.exists()
    facts=current(a.route)
    a.output.write_text(json.dumps(facts,indent=2)+'\n')
    admit(facts)
