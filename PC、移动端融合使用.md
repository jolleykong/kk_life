## PC、移动端融合使用

- 使用工具

  | 工具          | 用处                                                         |
  | ------------- | ------------------------------------------------------------ |
  | typora        | PC端markdown书写及文件管理                                   |
  | git           | 版本管理                                                     |
  | github/gitee  | 笔记托管                                                     |
  | Termux        | android端终端工具，安装git&进行笔记同步                      |
  | Markor        | android端markdown工具，支持文件管理，对md特性支持较为完善。支持搜索，支持搜藏，免费。【推荐】 |
  | Epsilon Notes | android端markdown工具，支持文件管理，对md特性支持最完善，部分高级功能需要付费版本。 |

  

- 融合思路

  - PC端通过typora编辑、管理笔记

  - PC端通过git对笔记进行版本管理、push

  - 托管上采用私有库方式，使用multi方式，同时push到gitee和github

    > [multi git repo](.\Linux\Others\multi_gits.md)

  - android 端安装Termux.apk、Markor.apk

  - termux安装后，安装git并开启存储权限

    ```
    pkg in git -y
    termux-setup-storage
    ```

  - 在termux家目录中会生成storage目录，里面包含到sdcard的软连接，因此可以创建一个恰当的软连接到sdcard，以便简单的路径下进行git clone。

  - 进入目录，执行git clone

  - 打开markor，进入到git clone的目录，可以使用了。

  - 更新仓库， 进入termux，执行git更新。也可以将git操作封装成脚本。