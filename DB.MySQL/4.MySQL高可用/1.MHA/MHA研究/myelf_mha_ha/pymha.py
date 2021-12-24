import os
import time

mha_check_result = ()


while True :
    cmdout=os.popen('masterha_check_status --conf=/data/mha/app1/app1.conf ')
    lines=cmdout.readlines()
    mha_check_result = "".join(lines).strip()
    # print(mha_check_result)

    if 'ok' in mha_check_result.lower():
        print('OK in')
        ok_result = os.popen("python3 pycheck_vip.py")
        for result in ok_result.readlines() :
            print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())) + " EVENT " + result.strip())

        # 执行vip有效性检查，并输出检查结果
        # 输出集群检查结果及配置文件？
    elif 'stop' in mha_check_result.lower():
        print('maybe stopped.')
        # 找到失败的节点
        # 思路，manager停止就意味着发生了failover，那么去执行检查，结果的最后5行内会有报错信息，如：
            # [error][/usr/share/perl5/vendor_perl/MHA/ServerManager.pm, ln492]  Server 192.168.188.53(192.168.188.53:3307) is dead, but must be alive! Check server settings.
        # 通过这种方式拿到server地址，然后执行ssh操作，拉起节点，change to new_master，然后拉起manager【这块不太严谨】
        #masterha_check_repl --global_conf=/data/mha/app1/default.conf --conf=/data/mha/app1/app1.conf
        # os.popen("masterha_check_repl --global_conf=" + defaultconf + " --conf=" + appconf)


        # 执行manager拉起
        
        # 初期实现目标：拉起mysql，change master to new_master
        # 远期实现目标：从备份拉起mysql，change master to new_master
    else :
        print(mha_check_result.lower())
        print('I am SB.')

    time.sleep(10)

