<img src="doc/README.assets/1.png" style="zoom:50%;" />

### 导航

-   [新手使用](doc/get-start-cn.md)
-   [详细指南](doc/user-guide-cn.md)

### 说明

`wing`是一个代码同步管理工具，具有以下特性：

-   支持`Winddows` 、`Linux` 、`MacOS`
-   支持代码同步和本地映射
-   扩展了针对工作空间的`git`命令 
-   保留了原`git`命令
-   增加了更多常用开发工具

### 快速开始

>新手操作看 [这里](doc/get-start-cn.md)

##### 安装

```shell
$ python setup.py install
```

##### 配置环境变量

**Windows：**

将`C:\Users\${user name}\bin`添加至系统环境变量。

**Linux/MacOS：**

将`~/bin`配置为可执行全局目录。

##### 创建工作空间

添加工作空间对应的代码`git`库服务地址，如：

```shell
# 本地索引模式
# wing -space add {space name} {git host} [manifest]
# such as:
$ wing -space add test git@github.com/iofomo
```

##### 获取代码

```shell
$ mkdir test
$ cd test

# wing init {space name} {branch/tag} {manifest file}
# such as:
$ wing init test master admin.xml
```

在当前目录下自动创建一个空的模板索引文件（`.wing/manifests/admin.xml`），需要添加要同步的代码库映射关系。

### 许可协议

本项目基于`MIT`许可协议，详情查看 [许可协议](doc/LICENSE) 文档。

>   本项目和所有的`tinyui`工具都是MIT许可证下的开源工具，这意味着你可以完全访问源代码，并可以根据自己的需求进行修改。
