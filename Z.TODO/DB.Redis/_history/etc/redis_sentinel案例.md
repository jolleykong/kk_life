# sentinel案例

redis就两台，配置了主从。sentinel有3台

| 10.0.0.5 | 6379 | 主   | 启动sentinel |
| -------- | ---- | ---- | ------------ |
| 10.0.0.6 | 6379 | 从   | 启动sentinel |
| 10.0.0.7 |      |      | 启动sentinel |



## 配置文件

3台sentinel都是一样在配置：
```
# mkdir /data/redis_sentinels/
# cd /data/redis_sentinels/
```
新增配置文件
```
# vim sentinel.conf  

port 26379
logfile "/data/redis_sentinels/26379.log"
pidfile "/data/redis_sentinels/26379.pid"
dir "/data/redis_sentinels"
sentinel monitor cluster6379 10.0.0.5 6379 2   
sentinel down-after-milliseconds cluster6379 6000
sentinel failover-timeout cluster6379 300000
sentinel auth-pass cluster6379 123456
protected-mode no
daemonize yes
```
参数解释：
```
port 26379                        #哨兵监听端口
daemonize yes                 #后台运行
protected-mode no 　　#保护模式如果开启只接受回环地址的ipv4和ipv6地址链接，拒绝外部链接，而且正常应该配置多个哨兵，避免一个哨兵出现独裁情况，如果配置多个哨兵那如果开启也会拒绝其他sentinel的连接。导致哨兵配置无法生效。
logfile "/data/redis_sentinels/26379.log"  　　  #指明日志文件
pidfile "/data/redis_sentinels/26379.pid"             #pid路径
dir "/data/redis/sentinel"
sentinel monitor cluster6379 10.0.0.5 6379 2 　            　#哨兵监控master。2表示当有2个哨兵检测到主库有问题才切换。一般3个哨兵建议位置为2
sentinel down-after-milliseconds cluster6379 6000　　    #主库宕机6s后切换，master或者slave多少时间（默认30秒）不能使用标记为down状态。
sentinel failover-timeout cluster6379 300000 　　#若哨兵在配置值内未能完成故障转移操作，则任务本次故障转移失败。
sentinel auth-pass cluster6379 123456  　　#如果redis配置了密码，那这里必须配置认证，否则不能自动切换。我设置的redis密码为123456
```

## 启动
```
redis-sentinel sentinel.conf 
```

## 检查
```
redis-cli -p 26379
127.0.0.1:26379> info Sentinel
# Sentinel
sentinel_masters:1
sentinel_tilt:0
sentinel_running_scripts:0
sentinel_scripts_queue_length:0
sentinel_simulate_failure_flags:0
master0:name=cluster6379,status=ok,address=10.0.0.5:6379,slaves=1,sentinels=3
```
看到sentinels哨兵为3个，slaves为1个，因为我就一个redis从

## 模拟哨兵是否正常切换
- 模拟主库宕机，主库上操作：
    ```
    redis-cli -a 123456
    > shutdown
    ```

- 从上检查是否提升为主，从库操作：
    ```
    redis-cli -a 123456
    10.0.0.6:6379> info replication
    # Replication
    role:master
    connected_slaves:0
    ```
    可以看到从提升为主了