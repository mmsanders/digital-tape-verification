using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Text;
public class App283Window {
  public long handle, owner_handle;
  public uint pid;
  public string title;
  public bool visible, responding, top_level;
}
public static class App283Native {
  private delegate bool EnumProc(IntPtr h, IntPtr p);
  [DllImport("user32.dll")] private static extern bool EnumWindows(EnumProc callback, IntPtr p);
  [DllImport("user32.dll")] private static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] private static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] private static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] private static extern bool IsHungAppWindow(IntPtr h);
  [DllImport("user32.dll")] private static extern IntPtr GetAncestor(IntPtr h, uint flags);
  [DllImport("user32.dll")] private static extern IntPtr GetWindow(IntPtr h, uint flags);
  [DllImport("user32.dll", SetLastError=true)] private static extern bool PostMessage(IntPtr h, uint msg, IntPtr w, IntPtr l);
  public static App283Window[] Snapshot(uint ownedPid) {
    var rows = new List<App283Window>();
    EnumProc cb = (h,p) => {
      uint pid; GetWindowThreadProcessId(h,out pid);
      if(pid != ownedPid) return true;
      var text=new StringBuilder(1024); GetWindowText(h,text,text.Capacity);
      rows.Add(new App283Window {handle=h.ToInt64(),pid=pid,title=text.ToString(),
        visible=IsWindowVisible(h),responding=!IsHungAppWindow(h),
        top_level=GetAncestor(h,2)==h,owner_handle=GetWindow(h,4).ToInt64()});
      return true;
    };
    if(!EnumWindows(cb,IntPtr.Zero)) throw new InvalidOperationException("Window enumeration failed");
    GC.KeepAlive(cb);
    return rows.ToArray();
  }
  public static bool Close(long handle, uint ownedPid) {
    uint pid; GetWindowThreadProcessId(new IntPtr(handle),out pid);
    return pid==ownedPid && PostMessage(new IntPtr(handle),0x0010,IntPtr.Zero,IntPtr.Zero);
  }
}
