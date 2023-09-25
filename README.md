# WING操作指南

### 说明

**`wing`工程：**即wing管理的多个`git`代码组本地的目录结构，这里称`工作空间`。

**`git`工程：**即对应的`Android`/`iOS`/`Java`工程的`git`库目录。

### 原理

`wing`采用`Python`开发语言实现，真正的功能对应于一个`wing`代码库，其管理多个`git`库代码的本地批处理工具，工作原理如下：

![](README.assets/20200907143405.png)

**`wing`的优点：**

1）不改变远程`git`库，本地可通过目录重命名隐射。

2）统一开发环境，即开发组内所有人员（含后台编译、打包、发布服务），所有目录结构均保持一致。

3）可扩展公共的业务脚本，如：`Extend commands`。

4）方便的一键操作代码组所有`git`库。

5）规范开发过程中模块依赖和输入输出，提升开发效率。

### 目录结构

​       通常`WING`工程开发目录结构布局如下：

![](README.assets/20200907151950-6990376.png)

对应的本地目录为：

![20230227160909](README.assets/20230227160909.jpg)

### 输入/输出

#### wing

在分支开发，测试稳定后，合并至主干`master`分支，其他人通过`wing sync`命令同步至最新版本，即可使用。 <span style="color:blue;">【通常管理员维护】</span>

#### doc

该目录为本工程的内部开发组的文档存放目录，如：产品线或本项目设计和开发文档等。可以通过命令`wing -refresh`生成文档索引。[详情](#jump-refresh)

#### out

该目录为各功能编译后输出结果文件目录，自动创建，输出的内容存放保持工程目录结构一致。通常通过命令`wing -build`编译生成。

### 依赖

#### Android

1）同一工程内模块依赖

```groovy
implementation project(':cmpt-utils')
```

2）依赖当前`WING`工程的其他`git`库模块，采用本地输出文件依赖

```groovy
repositories {
    flatDir {
        // 添加本地 out 目录
        dirs '../../../out', 'libs'
    }
}

dependencies {
    implementation fileTree(dir: 'libs', include: ['*.jar'])

    debugImplementation (name: 'cmpt/common/debug/cmpt-utils', ext: 'aar') // 依赖 out 目录编译模块
    releaseImplementation (name: 'cmpt/common/release/cmpt-utils', ext: 'aar') // 依赖 out 目录编译模块
}
```

3）依赖其他`WING`工程中`git`模块的，则统一采用`maven/cocopods`依赖

```groovy
dependencies {
    implementation fileTree(dir: 'libs', include: ['*.jar'])
  	implementation 'com.iofomo.android:cmpt-utils:1.0.0' // 依赖 maven 发布版本
}
```

#### build

各`git`模块编译结果均输出至`WING`的`out`目录（即：`${space path}/out`），模块之间依赖的文件也均从该`out`目录下获取。

至少提供：`Jenkins`（发布测试编译）和`local`（本地开发调试编译）两种编译脚本的支持。

编译的基本参数为：`out`（结果输出目录），`branch`（工程分支）， （`Jenkins`编译序号）。

### 命令

#### 获取代码

**下载`wing`**

下载代码库中的`wing.py`文件到本地。



同步指定代码组的所有代码。

**Windows平台**

```shell
# 下面以代码组名称为：project-a，用户名为：zhangsan，代码组分支为：master，为例
# 如Android平台开发人员同步代码为：
$ python wing.py init project-a zhangsan master android.xml

# 如iOS平台开发人员同步代码为：
$ python wing.py init project-a zhangsan master ios.xml

# 如服务端后台(若管理员未单独配置前端的web.xml则通用此索引)平台开发人员同步代码为：
$ python wing.py init project-a zhangsan master server.xml

# 如PC平台开发人员同步代码为：
$ python wing.py init project-a zhangsan master pc.xml

# 如测试开发人员同步代码为：
$ python wing.py init project-a zhangsan master test.xml
```

**MacOS/Linux平台**

```shell
# 下面以代码组名称为：project-a，用户名为：zhangsan，代码组分支为：master，为例
# 如Android平台开发人员同步代码为：
$ wing init project-a zhangsan master android.xml

# 如iOS平台开发人员同步代码为：
$ wing init project-a zhangsan master ios.xml

# 如服务端后台(若管理员未单独配置前端的web.xml则通用此索引)平台开发人员同步代码为：
$ wing init project-a zhangsan master server.xml

# 如PC(Windows/Linux/MacOS客户端开发)平台开发人员同步代码为：
$ wing init project-a zhangsan master pc.xml

# 如测试开发人员同步代码为：
$ wing init project-a zhangsan master test.xml
```

#### 同步代码

同步代码组各git库代码：

```shell
# 安全同步，同步失败不做处理，当前分支和索引不一致不同步
$ wing sync
# 强制同步（谨慎使用，Jenkins默认启用），失败则同步终止，当前分支和索引不一致则终止
$ wing sync -f -i
```

#### 编译

在某一工程目录下任意位置，执行如下命令（该工程已实现编译入口：`mk.py`），可以编译该工程：

```shell
# 编译调试和发布版本，编译结果输出目录：/xxx/out/xxx/debug/和/xxx/out/xxx/release/
$ wing -build
# 编译调试版本，编译结果输出目录：/xxx/out/xxx/debug/
$ wing -build d
# 编译发布版本，编译结果输出目录：/xxx/out/xxx/release/
$ wing -build r
```

在代码组根目录执行`wing -build`，则编译整个代码组。

#### 创建

创建开发工程（在wing工程目录下任意位置，执行如下命令，可以一键创建开发工程）

```shell
# 创建Python脚本文件：
$ wing -create pf demo
# 创建Python的Gui工程：
$ wing -create pg demo

# 创建java开发工程（一般用作开发jar的程序或提供给服务端的SDK）
$ wing -create jar demo

# 创建Android的平台工程
$ wing -create ap demo
# 创建Android的平台工程(该工程包含native模块)
$ wing -create anp demo

# 创建iOS平台的工程
$ wing -create ip demo
```

#### 清理

在git工程目录下任意位置，执行如下命令，可以将该工程已下载的缓存文件清除：

```shell
# 清理该工程gradle/xcode下载的依赖模块的缓存
$ wing -clean gradle
# 清理该工程下除了“develop”，“master”和当前分支外的所有本地分支，清除git缓存
$ wing -clean git
# 清理该工程下，python文件编译缓存（*.pyc/*.pym/*.pyo）
$ wing -clean py
```

<span style="color:red;">【慎用】</span>在wing工程目录下执行如下命令，则会遍历该wing工程目录下所有工程的缓存文件清除（Jenkins编译默认启用）

```shell
# 遍历wing工程目录下的所有子Android/iOS工程，清除gradle/xcode下载的依赖模块的缓存
$ wing -clean gradle
# 遍历wing工程目录下的所有git工程，清除除了“develop”，“master”和当前分支外的所有本地分支，清除git缓存
$ wing -clean git
# 遍历wing工程目录下的所有Python工程，清除编译缓存（*.pyc/*.pym/*.pyo等）
$ wing -clean py
```

#### ADB

获取顶层信息，确保手机连接正常，获取顶层的Activity和Window应用信息

```shell
$ wing -adb top
# 输出结果为：
# Top Window:
#   package: com.demo
# Top Activity:
#   package: com.demo, Intent { flg=0x20000000 cmp=com.demo/.MainActivity (has extras) }
```

获取指定包名的应用安装包文件（系统预装的应用apk无dex），导出到当前目录下

```shell
# 格式为：wing -adb pull {package name}，如：
$ wing -adb pull com.demo
# 输出结果为：
# from: /data/app/~~4URZVO6GlkmlcEGS_F2xeQ==/com.demo-3QR4NmIK-9g99w4rBrPiog==/base.apk
#   to: com.demo.apk
```

#### 刷新

<span id="jump-refresh">刷新命令</span>则会扫描当前工程目录，更新本地工作空间的开发配置文件等

```shell
$ wing -refresh
```

**脚本：**遍历代码组目录下所有的 "*.sh" 和 "gradlew" 文件，确保其具有可执行权限

**DOC：**扫描工程下所有文档文件，在跟目录下生成 <span style='color:blue;'>doc.md</span> 文档索引文件

>该文档为当前代码组文档索引文件，扫描代码组所有git的目录下的doc目录文档文件：
>
>1）文档名称和标题（md格式解析文档首行标题，其他格式解析文件名）
>2）文档git最近更新记录
>3）最近三天修改的文档标记为“【新】”

![screenshot-20230312-225209](README.assets/screenshot-20230312-225209.png)

#### 工程解析

解析代码组当前目录的各`git`库工程属性信息

```shell
$ wing -project
```

执行成功后，并输出结果：`${SPACE PATH}/out/project.json`。

#### 密钥

查看安装包（`apk/ipa`）和证书（`keystore`）的签名信息

```shell
#【Android】查看安装包文件的签名信息
$ wing -key list com.demo.apk
#【Android】查看签名证书的信息，无密码，需要两次回车，即输入密码时忽略
$ wing -key list debug.keystore
#【Android】查看签名证书的信息，带密码
$ wing -key list debug.keystore 123456

#【iOS】查看安装包文件的签名信息（解析Payload/Demo.app/embedded.mobileprovision）
$ wing -key list demo.ipa
#【iOS】查看p12的签名信息
$ wing -key list debug.p12 xxxxxx 123456
#【iOS】查看签名文件信息
$ wing -key list embedded.mobileprovision
```

### Git命令

#### 查看分支

```shell
$ wing -branch
# 输出结果为：
.wing/wing                                      master
.wing/manifests                                 master
doc                                             master
platform/doc                                    master
ios/common                                      release_v1.0 ≠ master(remote)
android/client                                  master
android/common                                  master
server/web                                      master
server/service                                  master
pc/tools                                        master
```

#### 切换分支

>切换代码分支，会进行如下操作：
>
>-   遍历代码组（manifest索引文件）的所有git工程
>-   从远程同步工程的分支
>-   切换到目标分支
>-   同步新分支的代码为最新

```shell
$ wing -switch release_v3.5.0
```

#### 创建分支

基于某一原分支创建新分支。

```shell
# 命令格式为：
$ wing -newbranch [branch name] [new branch name]
# 如：
$ wing -newbranch develop release_v1.0
```

#### 创建标签

基于某一分支创建新`TAG`。

```shell
# 命令格式为：
$ wing -newtag [branch name] [new tag name]
# 如：
$ wing -newtag develop tag_v1.0
```

#### 提交代码

>在`WING`工程的<span style="color:blue;">任何Git工程</span>目录下执行此命令，则会提交当前Git工程代码至远程服务器

```shell
# 提交代码至当前分支所在的远程分支，之后需要在Gerrit上进行Code-Review确认后才能入库
# git branch -vv
# git push origin HEAD:refs/for/${origin branch name}
$ wing -push

# 直接提交服务器，无需Code-Review
# git branch -vv
# git push origin HEAD:refs/heads/${origin branch name}
$ wing -push f
```

><span style="color:red;">【慎用】</span>在`WING`工程根目录下执行此命令，则会遍历当前所有代码组，提交未`push`至远程服务的代码

```shell
# 遍历代码组所有Git库，提交代码至当前分支所在的远程分支，之后需要在Gerrit上进行Code-Review确认
# git status
# git branch -vv
# git push origin HEAD:refs/for/${origin branch name}
$ wing -push

# 遍历代码组所有Git库，直接提交服务器，无需Code-Review
# git status
# git branch -vv
# git push origin HEAD:refs/heads/${origin branch name}
$ wing -push f
```
