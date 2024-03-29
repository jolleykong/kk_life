已剪辑自: https://mp.weixin.qq.com/s/TKqG5eQ4gSwNn6M5UaKaRw

## 导读

除了MySQL自身的账号密码安全管理，系统层面、应用层面的安全策略你注意到了吗？

数据是企业核心资产，数据对企业而言是最重要的工作之一。稍有不慎，极有可能发生数据无意泄露，甚至被黑客恶意窃取的风险。每年业界都会传出几起大事件，某知名或不知名的公司被脱裤（拖库的谐音，意思是整个数据库被黑客盗取）之类的。

从数据安全上也可以分为外网安全及内部操作安全，下面分别讨论一下。

## 内部操作安全策略

### 1. 是否回收DBA全部权限

试想，如果DBA没权限了，日常DB运维的活，以及紧急故障处理，该怎么实施呢？因此，建议在没有成熟的自动化运维平台前，不应该粗暴的回收DBA的太多权限，否则可能会导致工作效率降低的，甚至DBA有一种不被信任的负面情绪。

### 2. MySQL层安全策略

- 业务帐号最多只可以通过内网远程登录，而不能通过公网远程连接。
- 增加运维平台账号，该账号允许从专用的管理平台服务器远程连接。当然了，要对管理平台部署所在服务器做好安全措施以及必要的安全审计策略。
- 建议启用数据库审计功能。这需要使用MySQL企业版，或者Percona/MariaDB分支版本，MySQL社区版本不支持该功能。
- 启用 safe-update 选项，避免没有 WHERE 条件的全表数据被修改；
- 在应用中尽量不直接DELETE删除数据，而是设置一个标志位就好了。需要真正删除时，交由DBA先备份后再物理删除，避免误操作删除全部数据。
- 还可以采用触发器来做一些辅助功能，比如防止黑客恶意篡改数据。

### 3. MySQL账号权限规则

- 业务帐号，权限最小化，坚决不允许DROP、TRUNCATE权限。
- 业务账号默认只授予普通的DML所需权限，也就是select、update、insert、delete、execute等几个权限，其余不给。
- MySQL初始化后，先行删除无用账号，删除匿名test数据库

mysql> delete from mysql.user where user!='root' or host!='localhost'; flush privileges;
 
 mysql> drop database test;

- 创建备份专用账号，只有SELECT权限，且只允许本机可登入。
- 设置MySQL账号的密码安全策略，包括长度、复杂性。

### 4. 关于数据备份

记住，**做好数据全量备份是系统崩溃无法修复时的最后一概救命稻草**。
 备份数据还可以用来做数据审计或是用于数据仓库的数据源拉取之用。
 一般来说，备份策略是这样的：**每天一次全备，并且定期对****binlog****做增备，或者直接利用****binlog server****机制将****binlog****传输到其他远程主机上**。有了全备+binlog，就可以按需恢复到任何时间点。
 特别提醒：当采用xtrabackup的流式备份时，考虑采用加密传输，避免备份数据被恶意截取。

##   

## 外网安全策略

事实上，操作系统安及应用安全要比数据库自身的安全策略更重要。同理，应用程序及其所在的服务器端的系统安全也很重要，很多数据安全事件，都是通过代码漏洞入侵到应用服务器，再去探测数据库，最后成功拖库。

### 1. 操作系统安全建议

- 运行MySQL的Linux必须只运行在内部网络，不允许直接对公网暴露，实在有需要从公网连接的话，再通过跳板机做端口转发，并且如上面所述，要严格限制数据库账号权限级别。
- 系统账号都改成基于ssh key认证，不允许远程密码登入，且ssh key的算法、长度有要求以确保相对安全。这样就没有密码丢失的风险，除非个人的私钥被盗。
- 进一步的话，甚至可以对全部服务器启用PAM认证，做到账号的统一管理，也更方便、安全。
- 关闭不必要的系统服务，只开必须的进程，例如 mysqld、sshd、networking、crond、syslogd 等服务，其它的都关闭。
- 禁止root账号远程登录。
- 禁止用root账号启动mysqld等普通业务服务进程。
- sshd服务的端口号建议修改成10000以上。
- 在不影响性能的前提下，尽可能启用对MySQL服务端口的防火墙策略（高并发时，采用iptables可能影响性能，建议改用ip route策略）。
- GRUB必须设置密码，物理服务器的Idrac/imm/ilo等账号默认密码也要修改。
- 每个需要登入系统的员工，都使用每个人私有帐号，而不是使用公共账号。
- 应该启用系统层的操作审计，记录所有ssh日志，或利bash记录相应的操作命令并发送到远程服务器，然后进行相应的安全审计，及时发现不安全操作。
- 正确设置MySQL及其他数据库服务相关目录权限，不要全是755，一般750就够了。
- 可以考虑部署堡垒机，所有连接远程服务器都需要先通过堡垒机，堡垒机上就可以实现所有操作记录以及审计功能了。
- 脚本加密对安全性提升其实没太大帮助。对有经验的黑客来说，只要有系统登入权限，就可以通过提权等方式轻松获得root。

### 2. 应用安全建议

- 禁用web server的autoindex配置。
- 从制度层面，杜绝员工将代码上传到外部github上，因为很可能存在内部IP、账号密码泄露的风险，真的要上传必须先经过安全审核。
- 尽量不要在公网上使用开源的cms、blog、论坛等系统，除非做过代码安全审计，或者事先做好安全策略。这类系统一般都是黑客重点研究对象，很容易被搞；
- 在web server层，可以用一些安全模块，比如nginx的WAF模块；
- 在app server层，可以做好代码安全审计、安全扫描，防止XSS攻击、CSRF攻击、SQL注入、文件上传攻击、绕过cookie检测等安全漏洞；
- 应用程序中涉及账号密码的地方例如JDBC连接串配置，尽量把明文密码采用加密方式存储，再利用内部私有的解密工具进行反解密后再使用。或者可以让应用程序先用中间账号连接proxy层，再由proxy连接MySQL，避免应用层直连MySQL；

最后我们想说，**任何高明的安全策略，都不如内部员工的安全意识来的重要**。以前发生过一起案例，公司内有位员工的PC不慎中毒，结果导致内网数据被盗。

安全无小事，每个人都应铭记于心。在数据安全面前，可以适当牺牲一些便利性，当然也不能太过，否则可能得不偿失。


 