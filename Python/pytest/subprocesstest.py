import subprocess
import time
p1 = subprocess.Popen(["top"])
# print(p1.pid)
flag = True
while flag:
    stat = p1.poll()
    if stat == None:
        _pid = p1.pid
        print(_pid)
        pass
    else:
        print(f'检测到 {_pid} 进程异常，守护进程进行进程拉起。')
        p1 = subprocess.Popen(["top"])
    time.sleep(10)
    # ,stdout=subprocess.DEVNULL