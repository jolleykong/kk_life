注意：8.0以后版本配置复制时需要加参数

 

--8.0 rep时会出现 requires secure connection的提示，无法建立连接

```
Last_IO_Error: error connecting to master 'rep@192.168.188.81:3308' - retry-time: 60 retries: 1 message:

Authentication plugin 'caching_sha2_password' reported error: Authentication requires secure connection.

```


```
change master to 后加 get_master_public_key=1;
```


密码与本机公钥参与加密。