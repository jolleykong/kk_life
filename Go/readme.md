start go on March 16, 2022



```
解决vscode无法顺利安装golang插件

go env -w GO111MODULE=on 
go env -w GOPROXY=https://goproxy.io,direct 

终端执行后， 重启vscode ，再点击install all就好了。

# 配置 GOPROXY 环境变量
export GOPROXY=https://proxy.golang.com.cn,direct
# 还可以设置不走 proxy 的私有仓库或组，多个用逗号相隔（可选）
export GOPRIVATE=git.mycompany.com,github.com/my/private

```