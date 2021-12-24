# Redis布署规范
## 安装
## 基本目录
```
/usr/local/redis/
├── bin
│   ├── redis-benchmark
│   ├── redis-check-aof
│   ├── redis-check-dump
│   ├── redis-cli
│   ├── redis-sentinel
│   └── redis-server
└── tools
├── redis-faina.py
└── redis-tool.sh
```

## 数据、配置目录存放：
```
/data/redis${port}
.................${port}.rdb
.................${port}.aof
.................${port}.conf
.................${port}.log
.................${port}.pid
```

## 自动化安装
- 将需要升级的redis实例端口添加到port.txt文本文件中，执行自动安装脚本

  ```
  ./redis-2.8.17/redis_install.sh $memszie
  ```
- 创建：

  ```
  /data/redis${prort}/
  /data/redis${port}/${port}.conf
  ```
- 启动

  ```
  /usr/local/redis/tools/redis-tool.sh $port start
  ```
- 关闭

  ```
  /usr/local/redis/tools/redis-tool.sh $port stop
  ```
- 其它脚本说明

  - 存放位置：/usr/local/redis/tools/

- 配置keepalived.conf

  ```
  vim /etc/keepalived/keepalived.conf
  
  vrrp_script chk_redis1
  {
       script "/etc/keepalived/scripts/redis_check_v2.sh 127.0.0.1 $port"
       interval 5
  }
  vrrp_instance $port {
      state BACKUP
      interface bond0
      virtual_router_id 224
      priority  90
      nopreempt
      preempt_delay 10
      advert_int 1
      authentication {
          auth_type PASS
          auth_pass fetion
      }
      virtual_ipaddress {
    192.168.199.76
      }
      track_script {
           chk_redis1
      }
      notify_master "/etc/keepalived/scripts/notify_master_v2.sh 127.0.0.1 对端IP $port"
      notify_backup " /etc/keepalived/scripts/notify_backup_v2.sh 127.0.0.1 master_ip $port"
      notify  /etc/keepalived/scripts/notify_v2.sh
  }
  ```
- 修改开机启动

  ```
  vim /etc/init.d/redis-server
  
  #!/bin/bash
  #chkconfig: 35 90 10
  #description: Redis-Server
  redis_start() {
  rm -f /data/redis$port/$port.rdb
  /usr/local/redis/bin/redis-server /data/redis$port/$port.conf
  sleep 2
  service keepalived start
  ps -ef | grep redis57
  }
  redis_stop() {
  /usr/local/redis/bin/redis-cli -p $port SHUTDOWN NOSAVE
  service keepalived stop
  echo "wait 10sec..."
  sleep 10 #wait for switch
  ps -ef | grep redis$port
  }
  redis_restart() {
   redis_stop
   redis_start
  }
  redis_usage() {
    echo -e "Usage: $0 {start,stop,restart}"
    exit 1
  }
  case "$1" in
    start)   redis_start ;;
    stop)    redis_stop  ;;
    restart) redis_restart ;;
    *)       redis_usage ;;
  esac
  ```