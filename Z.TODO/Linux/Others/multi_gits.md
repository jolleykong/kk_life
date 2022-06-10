```
[core]
        repositoryformatversion = 0
        filemode = false
        bare = false
        logallrefupdates = true
        symlinks = false
        ignorecase = true
[remote "origin"]
        url = https://github.com/jolleykong/kk_mysql.git
        fetch = +refs/heads/*:refs/remotes/origin/*
        url = https://gitee.com/kkong/kk_mysql.git
[branch "master"]
        remote = origin
        merge = refs/heads/master
[remote "gitee"]
        url = https://gitee.com/kkong/kk_mysql.git
        fetch = +refs/heads/*:refs/remotes/gitee/*
        tagopt = --no-tags
[oh-my-zsh]
        hide-dirty = 1
        hide-status = 1
[gui]
        wmstate = normal
        geometry = 2008x1063+305+381 451 486
```

```
git删除历史版本，保留当前状态。

有时候，我们误提交了某些隐私文件，使用git rm xxx删除后，其实版本库中是有历史记录的，想要删除这些记录，但是又不想删除仓库，重建来提交。那么就想办法删除历史记录了。
我们当然不能直接删除.git文件夹，这将导致git存储库出现不可预知的问题。
要删除所有提交历史记录，但将代码保持在当前状态，可以按照以下方式安全地执行此操作：

创建并切换到latest_branch分支

    git checkout --orphan latest_branch

添加所有文件

    git add -A

提交更改

    git commit -am "删除历史版本记录，初始化仓库"

删除分支

    git branch -D master

将当前分支重命名

    git branch -m master

强制更新存储库

    git push -f origin master


```




``` 2022
[core]
	repositoryformatversion = 0
	filemode = false
	bare = false
	logallrefupdates = true
	symlinks = false
	ignorecase = true

[core]
        repositoryformatversion = 0
        filemode = false
        bare = false
        logallrefupdates = true
        symlinks = false
        ignorecase = true
[remote "origin"]
        url = https://gitee.com/kkong/kk_mysql.git
        fetch = +refs/heads/*:refs/remotes/gitee/*
        url = https://github.com/jolleykong/kk_mysql.git
[branch "master"]
        remote = origin
        merge = refs/heads/master
[remote "github"]
        url = https://github.com/jolleykong/kk_mysql.git
        fetch = +refs/heads/*:refs/remotes/github/*
        tagopt = --no-tags
[remote "gitee"]
        url = https://gitee.com/kkong/kk_mysql.git
        fetch = +refs/heads/*:refs/remotes/gitee/*
        tagopt = --no-tags
[oh-my-zsh]
        hide-dirty = 1
        hide-status = 1
[gui]
        wmstate = normal
        geometry = 2008x1063+305+381 451 486
```