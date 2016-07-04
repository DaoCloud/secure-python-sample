# 使用安全镜像功能混淆加密打包动态语言程序
动态语言程序，通常需要源代码才能运行。

为了保护源码，我们通常会对源码进行混淆加密或者打包成二进制，这样拿到程序的人员无法简单地了解程序运行原理和代码逻辑。

我们使用常规镜像功能（一个 Dockerfile）来构建 Docker 镜像，通常无法避免地将程序源码 ADD 或者 COPY 到镜像中。例如使用指令`ADD . app` 将源码加载到镜像的 app 目录中，这一层 layer 将永远在这个镜像中，即使在之后我们使用指令`RUN rm -r app` 删除镜像中源码， 我们仍可以从 layer 中提取到源代码。

使用安全镜像功能将编译、提取和打包过程完全分离，我们可以获得一个轻量、源码加密的安全镜像。
以下，我们以 python 程序为例讲解如何使用安全镜像功能混淆、加密、打包动态语言程序。

示例程序在 [GitHub](https://github.com/DaoCloud/secure-python-sample)  上。

## daocloud.yml

```yaml
version: 2.0

test:
  image: daocloud/ci-python:2.7
  
  services:
    - mysql
  
  env:
    - MYSQL_USERNAME="root"
    - MYSQL_PASSWORD=""
    - MYSQL_INSTANCE_NAME="test"
  
  script:
    - pip install -r requirements.txt
    - nosetests test.py --with-xunit --xunit-file=$TEST_RESULT
    - coverage run --branch test.py
    - coverage xml -o $TEST_COVERAGE test.py
    - cat $TEST_RESULT
    - cat $TEST_COVERAGE

build:
  lite_image:
    compile:
      dockerfile_path: Dockerfile.compile
      build_dir: /
      cache: true
    extract:
      - /usr/bin/application
    package:
      dockerfile_path: Dockerfile.package
      build_dir: /
      cache: true
```

这个是我们在 DaoCloud 代码构建时的配置，其中的 build 这一节是我们真正关心的。
## 编译
```yaml
compile:
      dockerfile_path: Dockerfile.compile
      build_dir: /
      cache: true
```

编译是我们镜像构建的第一步，我们将使用源码根目录的 [Dockerfile.compile](https://github.com/DaoCloud/secure-python-sample/blob/master/Dockerfile.compile)，构建位置在源代码根目录。

```Dockerfile
FROM python:2.7.8
MAINTAINER Sakeven Jiang <sakeven.jiang@daocloud.io>

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY . /usr/src/app

RUN pip install -r requirements.txt
RUN pyinstaller --onefile -y application.py  && \
    mv dist/application /usr/bin/application

EXPOSE 3000

CMD [ "application"]
```

这个 Dockerfile 主要的工作是，下载依赖（`pip install -r requirements.txt`），使用 pyinstaller 打包成二进制（`pyinstaller --onefile -y application.py `），我们得到一个二进制程序 `dist/application`。我们还可以使用 pyinstaller 来加密这个程序，读者可以自行阅读相关资料。

在这个镜像中 application 最终被放置在 `/usr/bin/` 目录下。请记住这个程序现在是 `/usr/bin/application `，我们等会用到。

## 提取
```yaml
extract:
      - /usr/bin/application
```

上一步中我们得到一个二进制程序，名为`/usr/bin/application`。

现在我们要显式地说明，我们要提取这个文件。

这个提取出来的文件将会放在代码根目录的`/usr/bin/application`。

## 打包
```yaml
package:
      dockerfile_path: Dockerfile.package
      build_dir: /
      cache: true
```

这是我们构建安全镜像的最后一步，我们将使用 [Dockerfile.package](https://github.com/DaoCloud/secure-python-sample/blob/master/Dockerfile.package) 来构建我们的最终镜像。

```Dockerfile
FROM ubuntu:14.04
MAINTAINER Sakeven Jiang <sakeven.jiang@daocloud.io>

COPY usr/bin/application /usr/bin/application

EXPOSE 3000

CMD ["application"]
```


Dockerfile.package 的工作很简单，仅仅是将我们刚才提取出来的二进制程序拷贝到最终镜像里（`COPY usr/bin/application /usr/bin/application`）。 So easy，我们的安全镜像就这么构建好了，它不会泄露你的源码，而且体积也变小了。
