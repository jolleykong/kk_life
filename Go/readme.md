start go on March 16, 2022



```
解决vscode无法顺利安装golang插件

go env -w GO111MODULE=on 
go env -w GOPROXY=https://goproxy.io,direct 

终端执行后， 重启vscode ，再点击install all就好了。
```