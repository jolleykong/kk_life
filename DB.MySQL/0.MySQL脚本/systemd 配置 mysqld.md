通过systemctl管理mysqld服务
1. 背景
  CentOS 7.x 之前的版本，系统启动时，第一支呼叫的程序是 init ，然后 init 去唤起所有的系统所需要的服务，无论是本地服务还是网络服务。所有的服务启动脚本都放置于 /etc/init.d 下面，基本上都是使用 bash shell script 所写成的脚本程序。

  从CentOS 7.x 以后，Red Hat 放弃了 init 启动脚本的方法，改用systemd 这个启动服务管理机制。

2. systemctl管理服务的好处
   - 平行处理所有服务，加速开机流程
     旧的init 启动脚本是【一项一项任务依序启动】的模式，因此不相依的服务也是一个一个的等待。但目前我们的硬件主机系统与操作系统几乎都支持多核心结构了，systemd可以让所有的服务同时启动，系统启动的速度变快了。
   - 一经要求就相应的 on-demand 启动方式
     System 全部就是仅有一直systemd 服务 搭配systemctl 指令来处理，无需其它的指令来支持。不想之前的启动方式还要init，chkconfig，service…等指令。此外，systemd 由于常驻内存，因此任何要求（on-demand）都可以立即处理后续的daemon启动的任务。
   - 服务相依性的自我检查
     由于systemd可以自定义服务相依性的检查，因此如果 B 服务是架构在 A服务上面的，那当你在没有启动 A 服务的情况下仅手动启动 B 服务时，systemd 会自动帮你启动A服务。这样可以免去管理员一项一项去分析的麻烦。

3. Systemd启动脚配置文件所在目录
   目录说明
   - /lib/system/system/
     使用CentOS官方提供的软件安装后，默认的启动脚本配置文件都放在这里，这里的数据尽量不要修改。要修改时，请到 /etc/system/system低下修改较佳。
   - /etc/system/system/
     管理员依据主机系统的需求所建立的执行脚本，其实这个目录有点像之前的/etc/rc.d/rc5.d/Sxx 之类的功能。执行优先顺序要比/run/system/system/ 高。
   - /run/system/system/
     系统执行过程中所产生的服务脚本。

4. MySQL服务
   在之前的安装中，我们一般都是 通过 support-files/mysql.server （单实例）、support-files/mysqld_multi.server （多实例）来配置服务。其实现管理mysql服务的脚本就是 在mysql.server、 mysqld_multi.server文件中。

   脚本复杂并且修改比较困难。例如，我需要配置多实例，但不想修改既有的my.cnf 配置文件，如果新实例的文件名字命名为my3307.cnf，此时再用老的方法，去修改 mysql.server 就比较麻烦。而如果用 system就比较简单。

例如 ，定义一个测试服务为：mysql3307.service

```
[Unit]
Description=MySQL Server
After=network.target

[Install]
WantedBy=multi-user.target

[Service]
Type=forking
TimeoutSec=0
PermissionsStartOnly=true
ExecStart=/data/mysql57/bin/mysqld --defaults-file=/etc/my3307.cnf --daemonize
LimitNOFILE = 65535
Restart=on-failure
RestartSec=3
RestartPreventExitStatus=1
PrivateTmp=false
```

此服务的其它的一些操作命令;

systemctl enable mysql3307.service  ---设置开启自启动

systemctl start mysql3307.service     ----开启此服务

systemctl stop mysql3307.service    -----关闭此服务

systemctl status mysql3307.service -----查看服务状态

注意

（1）/data/mysql57/bin/mysqld 路径为 可执行文档所在路径；/etc/my3307.cnf 配置未见；

（2）Restart=on-failure 是决定 服务Failure 时，是否自动拉起；RestartSec=3 尝试拉起间隔