```
 yum remove docker \
                  docker-client \
                  docker-client-latest \
                  docker-common \
                  docker-latest \
                  docker-latest-logrotate \
                  docker-logrotate \
                  docker-engine
```

```
yum install -y yum-utils
yum-config-manager \
    --add-repo \
    https://download.docker.com/linux/centos/docker-ce.repo
    
    
```

```
yum install docker-ce docker-ce-cli containerd.io
```

#                  [     Docker国内镜像源        ](https://www.cnblogs.com/zhangrui153169/p/12699077.html)             

#  

创建或修改 /etc/docker/daemon.json 文件

```
# vi /etc/docker/daemon.json
{
    "registry-mirrors": ["https://registry.docker-cn.com"]
}
systemctl restart docker.service
```

Docker中国区官方镜像
https://registry.docker-cn.com

网易
http://hub-mirror.c.163.com

ustc 
https://docker.mirrors.ustc.edu.cn

中国科技大学
https://docker.mirrors.ustc.edu.cn