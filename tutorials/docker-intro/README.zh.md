> 📄 English: [README.md](README.md)

![](https://europe-west1-atp-views-tracker.cloudfunctions.net/working-analytics?notebook=tutorials--docker-intro--readme)

# Docker 入门
## 概览

Docker 是一款核心的 CI/CD 工具，也是容器化的行业标准。它在 DevOps、MLOps 以及在生产环境中部署代码和应用的开发者中被广泛使用。Docker 的学习曲线较为陡峭，本教程旨在帮助你理解 Docker 是什么，以及在开发工作流中使用它的好处。在本教程中，我们将深入 Docker 的基础。我们会先概览 Docker，然后深入基本概念和操作，例如构建镜像并将其作为容器运行。


## 为什么 Docker 对 AI Agent 开发很重要

如果你正在为生产环境构建 AI Agent，Docker 不只是“锦上添花”——它必不可少。现代 AI Agent 依赖复杂的依赖生态：特定的 Python 版本、机器学习库、向量数据库、API 客户端，通常还有 GPU 驱动。没有容器化，在你的开发环境中完美运行的东西，可能会因为版本冲突、缺少依赖或环境差异而在生产环境中彻底崩溃。Docker 确保你的 AI Agent 无论在你的笔记本、云服务器还是 Kubernetes 集群上都能一致地运行。更重要的是，当你的 Agent 从原型扩展到生产时，Docker 能实现无缝部署、自动扩缩容和可靠更新——把你实验性的 AI 代码变成稳健、生产就绪、企业可以信赖的应用。


> 俗话说一图胜千言，下面这张来自 [reddit](https://europe-west1-atp-views-tracker.cloudfunctions.net/working-analytics?notebook=tutorials--docker-intro--readme&click=reddit-it-works-on-my-machine&target=https%3A%2F%2Fwww.reddit.com%2Fr%2FProgrammerHumor%2Fcomments%2Fcw58z7%2Fit_works_on_my_machine%2F&text=reddit) 的图片不言自明地说明了 Docker 的动机：


<br>
<br /><figure>
 <img src="assets/docker-meme.jpg" width="70%" align="center"/></a>
<figcaption> Docker 梗图（来源：reddit）</figcaption>
</figure>

<br>
<br />


## 范围

本教程将涵盖以下主题：
- 什么是 Docker？
- Dockerfile
- 构建镜像
- 运行容器
- 挂载卷（volume）
- 容器化 AI Agent

## 前置条件

这是一个入门级教程，不需要任何先验知识。不过，建议你对命令行命令有一些基本了解。

要运行本教程中的示例，你需要：
- 在电脑上安装 Docker Desktop（或等效工具）
- 一个 Docker Hub 账户

### 安装 Docker Desktop

Docker 是为在 Linux 操作系统上运行而构建的，因此它无法在 macOS 和 Windows 等其他操作系统上原生运行。Docker Desktop 提供了必要的虚拟环境，让你可以在 Linux 之外的操作系统上运行 Docker 容器。此外，它还提供了一个用于管理已分配资源和容器的 GUI 界面。

要安装 Docker Desktop，请前往 [Docker 网站](https://europe-west1-atp-views-tracker.cloudfunctions.net/working-analytics?notebook=tutorials--docker-intro--readme&click=docker-docker-desktop&target=https%3A%2F%2Fwww.docker.com%2Fproducts%2Fdocker-desktop&text=Docker%20website) 并按照你操作系统的说明操作：

<br>
<br /><figure>
 <img src="assets/docker-desktop.png" width="100%" align="center"/></a>
<figcaption> Docker Desktop</figcaption>
</figure>

<br>
<br />

安装完 Docker Desktop 后，它应该会自动启动。如果没有自动启动，请点击屏幕右上角的图标（在 macOS 上）。

你可以在终端里输入 `docker --version` 来验证 Docker 是否正在运行：
```shell
>docker --version                                                          
Docker version 28.0.4, build b8034c0
```


### 设置 Docker Hub 账户

Docker Hub 是一个公共仓库，允许你存储、共享和运行你的容器（就像 GitHub 让你存储和维护代码一样）。要设置 Docker Hub 账户，请前往 [Docker Hub](https://europe-west1-atp-views-tracker.cloudfunctions.net/working-analytics?notebook=tutorials--docker-intro--readme&click=docker&target=https%3A%2F%2Fhub.docker.com%2F&text=Docker%20Hub) 并按照说明操作。


<br>
<br /><figure>
 <img src="assets/docker-hub.png" width="100%" align="center"/></a>
<figcaption> Docker Hub</figcaption>
</figure>

<br>
<br />


## 什么是 Docker？

Docker 是一款 CI/CD 工具，可实现代码的无缝开发和在不同环境（即本地到远程等）之间的部署。通过创建操作系统级的虚拟化，一个应用及其依赖可以被打包到一个虚拟容器中，并在不同环境之间迁移。

在你的开发环境中使用 Docker 的主要优点是：

- **可复现性** - Docker 让你能把代码及其依赖无缝打包到单个容器中，并以高度一致性执行、测试、共享和部署代码
- **协作** - 当一个开发者团队在某个项目上共同工作时，Docker 解决了依赖的混乱问题。拥有统一的环境能在开发阶段节省大量时间。例如，如果某个开发者遇到某个错误，其他开发者很容易复现该错误并帮助调试
- **部署** - Docker 简化了代码从开发环境到生产环境的交付


## 可复现性问题

Docker 是为解决一个常见的 DevOps 问题而构建的——在代码迁移到不同环境（例如开发者的本地环境和生产环境）时缺乏可复现性。可复现性不仅限于 DevOps，它在数据科学和 AI 中也起着关键作用。

>我们可以把可复现性定义为：无论代码在哪个用户或机器上运行，运行相同代码都能产生完全相同结果的能力。

我第一次听到“可复现性”这个词是在本科阶段，当时我学到可复现性的起点和终点就是设置一个随机数种子（seed number）来锁定随机数。我最喜欢的种子数是 12345。当我开始做数据科学家后，我意识到可复现性远不止设置种子数。以下是可能影响代码可复现性的主要因素：

- **版本控制** — 首先也是最重要的，复现相同结果始于追踪代码变更的能力
- **随机化** — 通过设置种子数来控制随机数的生成
- **软件版本** — 你的 Python 或 R（或任何其他编程语言）及其依赖（例如库）的版本会影响代码的结果。例如，用 pandas v1.0 构建的代码，由于函数被弃用，可能在 v2.0 上无法运行
- **操作系统（OS）** — 大多数编程语言，尤其是 R 和 Python，会使用不同的编译器（例如 C、C++ 等）以及其他内置的 OS 组件。OS 的类型及其版本可能会影响代码的结果
- **硬件** — 最后但同样重要的是，硬件（或基础设施）的类型可能会影响你的结果（ARM/Intel/Apple 处理器等）

在常规的数据科学工作流中，可复现性依赖于若干因素。可复现性最基本、最平凡的元素之一是代码版本化。使用未版本化的代码，就无法追踪代码的变更，或验证同一代码能在不同环境上运行，这正是 Git 诞生的原因。

另一个关键因素是包版本化。随着时间的推移，包及其依赖往往会变化和演进，获得新特性、修复 bug、替换和弃用旧函数。在某些情况下，使用特定包版本运行你的代码可能无法工作，或无法产生与更旧或更新版本包相同的结果。例如，用 Pandas 1.x 写的代码可能无法在 Pandas 2.x 上运行，反之亦然。

类似地，编程语言往往会随时间变化，用较旧版本构建的代码可能无法在较新版本上工作或不再受支持。此外，不同的操作系统使用不同的软件架构，或在后端运行不同类型的编译器（c、c++ 等）。这种差异可能会影响你代码的可复现性。

最后，CPU 架构的类型（ARM、Intel、Apple Silicon 等）可能会影响底层软件。某些包或软件可能需要单独的构建，或可能不受支持，这最终会影响你代码的可复现性。

下面是图 1，它说明了在不同环境之间迁移时影响代码可复现性的因素。


<br>
<br /><figure>
 <img src="assets/reproducibility without Docker.png" width="100%" align="center"/></a>
<figcaption> 图 1：没有 Docker（和 Git）时的可复现性</figcaption>
</figure>

<br>
<br />

只要使用得当，Git 为代码的版本化和监控提供了一种解决方案，确保无论代码在哪个用户或机器上运行，都能被正确复现。Docker 及类似方案通过在一个容器内创建隔离环境来解决环境不匹配的问题，该容器可以随代码一起被迁移到任何远程机器，例如台式机、笔记本或服务器，从而实现流程的无缝复现。

在 Apple Silicon 和 Intel 机器等不同硬件架构上开发软件时，环境中可能存在潜在差异。Docker 可以通过为每种 CPU 架构创建专用镜像来部分解决这个问题。然而，这种方法可能耗时且昂贵，因为需要额外的测试来确保所有容器具有完全相同的特性。

图 2 展示了一个使用 Docker 和 Git 的通用工作流。我们用 Git 和 GitHub/Gitlab/Bitbucket（或任何类似服务）来做代码版本控制。Docker 用于搭建一个容器化环境，用于代码开发和测试。然后我们把代码连同容器一起迁移到任何支持容器的远程环境（即 GitHub Actions、AWS、GCP 等）。

<br>
<br /><figure>
 <img src="assets/reproducibility with Docker.png" width="100%" align="center"/></a>
<figcaption> 图 2：使用 Docker 和 Git 的可复现性</figcaption>
</figure>

<br>
<br />

虽然这个工作流提供了高度的可复现性，但它并不覆盖你因不同硬件设置而可能遇到的可复现性问题。有多种方法可以解决这个问题，例如为每种硬件架构构建专用环境（更多详情见[这里](https://europe-west1-atp-views-tracker.cloudfunctions.net/working-analytics?notebook=tutorials--docker-intro--readme&click=docker-docs&target=https%3A%2F%2Fdocs.docker.com%2Fbuild%2Fbuilding%2Fmulti-platform%2F&text=here)）。

注意：使用虚拟环境（VE）并不是 Docker 的替代品。事实上，二者配合得很好。虽然 VE 不属于本教程的范围，但你可以在以下[文章](https://europe-west1-atp-views-tracker.cloudfunctions.net/working-analytics?notebook=tutorials--docker-intro--readme&click=medium-running-python-r-with-docker-vs-virtual-environment-4a62ed36&target=https%3A%2F%2Fmedium.com%2F%40rami.krispin%2Frunning-python-r-with-docker-vs-virtual-environment-4a62ed36900f&text=article)中了解 VE 与 Docker 之间区别的更多信息。


## Docker 工作流

本节重点介绍基本的 Docker 工作流和要求，它们将让你能够构建镜像并在容器内运行它。基本的 Docker 工作流包括以下步骤：
- 使用 Dockerfile 定义环境要求
- 从 Dockerfile 构建镜像
- 将镜像作为容器运行
- 在容器中开发和测试代码
- 在容器中交付代码

> 人们经常混淆“镜像（image）”和“容器（container）”这两个术语。镜像是指由构建过程创建的产物，包含环境规格说明。容器是指将镜像作为实例运行的过程。


图 3 说明了构建镜像并将其作为容器运行的过程。

<br>
<br /><figure>
 <img src="assets/dockerfile to container.png" width="100%" align="center"/></a>
<figcaption> 图 3：Docker 工作流</figcaption>
</figure>

<br>
<br />


该工作流的主要组件是：

- **Dockerfile** - 镜像的配方（recipe）或蓝图，让我们能够添加组件并根据开发环境要求自定义依赖
- **Docker CLI** - 构建镜像并将其作为容器化环境运行的核心命令


在接下来的章节中，我们将更详细地拆解该流程的每一步。

## Dockerfile

`Dockerfile` 为 Docker 引擎提供如何构建镜像的指令。你可以把它想象成镜像的配方。它使用以下结构，具有自己独特且直观的语法：

``` Dockerfile
COMMAND some instructions
```

例如，下面的 `Dockerfile` 导入官方 Python（3.10 版本）镜像作为基础镜像，然后使用 `apt-get update` 和 `apt-get install` 安装 `curl` 库：


`./examples/ex1/Dockerfile`
``` Dockerfile
FROM python:3.10

LABEL example=1

ENV PYTHON_VER=3.10

RUN apt-get update && apt-get install -y --no-install-recommends curl
```

简而言之，我们使用 `FROM` 命令来指定要从 Docker registry 导入的镜像（构建镜像前别忘了登录你正在使用的 Docker registry 服务！）。`LABEL` 命令用于设置标签或注释，`ENV` 命令用于设置环境变量。最后但同样重要的是，`RUN` 命令用于在命令行上运行命令，在本例中用于安装 `curl` 库。

现在让我们回顾一下 Dockerfile 的核心命令：
- `FROM` - 定义用于构建镜像的基础镜像。在大多数情况下，除非你从零开始构建镜像，否则你会使用某个带有预装 OS 和某些依赖的基础镜像。例如，在本教程中，我们将导入官方 [Python 镜像](https://europe-west1-atp-views-tracker.cloudfunctions.net/working-analytics?notebook=tutorials--docker-intro--readme&click=docker-python&target=https%3A%2F%2Fhub.docker.com%2F_%2Fpython&text=Python%20image) 作为我们的基础镜像
- `LABEL` - 允许向镜像的元数据中添加关于镜像的信息，例如作者、维护者、许可证等。
- `ENV` - 用于设置环境变量
- `ARG` - 允许在构建时设置参数
- `RUN` - 允许在构建时执行 CLI 命令（例如 `pip install ...`、`apt-get ...`、`apt-install...`、`wget...` 等），为基础镜像添加额外的组件
- `COPY` - 允许将对象（例如文件和文件夹）从你的本地系统复制到镜像中
- `WORKDIR` - 设置镜像内的工作目录
- `EXPOSE` - 定义镜像在运行时要暴露的端口号
- `CMD` - 设置镜像运行时要执行的默认命令
- `ENDPOINT` - 允许将容器配置为作为可执行文件运行

如果此刻你还没有完全理解其中某些命令的用例，不用担心。当我们从下一节开始构建镜像时，一切都会变得更加清晰。

## Docker 构建

`Dockerfile` 准备好后，下一步是使用命令行中的 `docker build` 命令来构建镜像。例如，让我们从这个仓库的根目录使用 `build` 命令来构建上面的 `Dockerfile`：

``` shell
docker build . -f ./examples/ex-1/Dockerfile -t rkrispin/vscode-python:ex1 
```

以下是我们在 `build` 命令中使用的参数：
- `-f` 标签定义了 `Dockerfile` 的路径。这个参数是可选的，只有在从与 `Dockerfile` 所在目录不同的目录调用 `build` 函数时才应使用
- `.` 符号将文件系统的上下文文件夹定义为 `Dockerfile` 所在的那个。虽然在本例中我们没有使用文件系统，但在其他情况下，它让我们能够在构建时将文件从本地文件夹调用并复制到镜像中
- `-t` 用于设置镜像的名称和标签（例如版本）。在本例中，镜像名称是 `rkrispin/vscode-python`，标签是 `ex1`。


你应该会看到类似下面的输出：

``` shell
[+] Building 94.2s (6/6) FINISHED                                                                                                                                                                                                  
 => [internal] load build definition from Dockerfile                                                                                                                                                                          0.0s
 => => transferring dockerfile: 162B                                                                                                                                                                                          0.0s
 => [internal] load .dockerignore                                                                                                                                                                                             0.0s
 => => transferring context: 2B                                                                                                                                                                                               0.0s
 => [internal] load metadata for docker.io/library/python:3.10                                                                                                                                                                6.0s
 => [1/2] FROM docker.io/library/python:3.10@sha256:a8462db480ec3a74499a297b1f8e074944283407b7a417f22f20d8e2e1619782                                                                                                         82.1s
 => => resolve docker.io/library/python:3.10@sha256:a8462db480ec3a74499a297b1f8e074944283407b7a417f22f20d8e2e1619782                                                                                                          0.0s
 => => sha256:a8462db480ec3a74499a297b1f8e074944283407b7a417f22f20d8e2e1619782 1.65kB / 1.65kB                                                                                                                                0.0s
 => => sha256:4a1aacea636cab6af8f99f037d1e56a4de97de6025da8eff90b3315591ae3617 2.01kB / 2.01kB                                                                                                                                0.0s
 => => sha256:23e11cf6844c334b2970fd265fb09cfe88ec250e1e80db7db973d69d757bdac4 7.53kB / 7.53kB                                                                                                                                0.0s
 => => sha256:bba7bb10d5baebcaad1d68ab3cbfd37390c646b2a688529b1d118a47991116f4 49.55MB / 49.55MB                                                                                                                             26.1s
 => => sha256:ec2b820b8e87758dde67c29b25d4cbf88377601a4355cc5d556a9beebc80da00 24.03MB / 24.03MB                                                                                                                             11.0s
 => => sha256:284f2345db055020282f6e80a646f1111fb2d5dfc6f7ee871f89bc50919a51bf 64.11MB / 64.11MB                                                                                                                             26.4s
 => => sha256:fea23129f080a6e28ebff8124f9dc585b412b1a358bba566802e5441d2667639 211.00MB / 211.00MB                                                                                                                           74.5s
 => => sha256:7c62c924b8a6474ab5462996f6663e07a515fab7f3fcdd605cae690a64aa01c7 6.39MB / 6.39MB                                                                                                                               28.2s
 => => extracting sha256:bba7bb10d5baebcaad1d68ab3cbfd37390c646b2a688529b1d118a47991116f4                                                                                                                                     1.6s
 => => sha256:c48db0ed1df2d2df2dccd680323097bafb5decd0b8a08f02684b1a81b339f39b 17.15MB / 17.15MB                                                                                                                             31.9s
 => => extracting sha256:ec2b820b8e87758dde67c29b25d4cbf88377601a4355cc5d556a9beebc80da00                                                                                                                                     0.6s
 => => sha256:f614a567a40341ac461c855d309737ebccf10a342d9643e94a2cf0e5ff29b6cd 243B / 243B                                                                                                                                   28.4s
 => => sha256:00c5a00c6bc24a1c23f2127a05cfddd90865628124100404f9bf56d68caf17f4 3.08MB / 3.08MB                                                                                                                               29.4s
 => => extracting sha256:284f2345db055020282f6e80a646f1111fb2d5dfc6f7ee871f89bc50919a51bf                                                                                                                                     2.5s
 => => extracting sha256:fea23129f080a6e28ebff8124f9dc585b412b1a358bba566802e5441d2667639                                                                                                                                     6.2s
 => => extracting sha256:7c62c924b8a6474ab5462996f6663e07a515fab7f3fcdd605cae690a64aa01c7                                                                                                                                     0.3s
 => => extracting sha256:c48db0ed1df2d2df2dccd680323097bafb5decd0b8a08f02684b1a81b339f39b                                                                                                                                     0.5s
 => => extracting sha256:f614a567a40341ac461c855d309737ebccf10a342d9643e94a2cf0e5ff29b6cd                                                                                                                                     0.0s
 => => extracting sha256:00c5a00c6bc24a1c23f2127a05cfddd90865628124100404f9bf56d68caf17f4                                                                                                                                     0.2s
 => [2/2] RUN apt-get update && apt-get install -y --no-install-recommends curl                                                                                                                                               5.9s
 => exporting to image                                                                                                                                                                                                        0.1s
 => => exporting layers                                                                                                                                                                                                       0.1s
 => => writing image sha256:a8e4c6d06c97e9a331a10128d1ea1fa83f3a525e67c7040c2410940312e946f5                                                                                                                                  0.0s
 => => naming to docker.io/rkrispin/vscode-python:ex1  

 ```

**注意：** 上面的构建输出描述了镜像的不同层。如果此刻它看起来听起来像天书，别担心。读完下一节（重点讲镜像层）之后，阅读这类输出会更容易。


你可以使用 `docker images` 命令来验证镜像是否已成功创建：

``` shell
>docker images
REPOSITORY                             TAG       IMAGE ID       CREATED        SIZE
rkrispin/vscode-python                 ex1       a8e4c6d06c97   43 hours ago   1.02GB
```

下一节将重点介绍镜像层和缓存过程。


### 镜像层

Docker 镜像的构建过程基于层（layer）。根据上下文，docker 引擎在构建时获取 `Dockerfile` 中的每一条命令，并将其转换为层或元数据。诸如 `FROM` 和 `RUN` 之类的 `Dockerfile` 命令会被转换为层，而诸如 `LABEL`、`ARG`、`ENV` 和 `CMD` 之类的命令会被转换为元数据。例如，我们在上面 `rkrispin/vscode-python` 镜像的构建输出中可以观察到，它有两个层：
- 第一层以 `[1/2] FROM...` 开头，对应 `Dockerfile` 中的 `FROM python:3.10` 这一行，它导入了 Python 3.10 官方镜像
- 第二层以 `[2/2] RUN apt-get...` 开头，对应 `Dockerfile` 中的 `RUN` 命令
<br>
<br /><figure>
<img src="assets/docker-layers.png" width="100%" align="center"/></a>
<figcaption> 图 4 - 相对于 Dockerfile 的构建输出示例</figcaption>
</figure>

<br>
<br />

`docker inspect` 命令以 JSON 格式返回镜像元数据详情。其中包括环境变量、标签、层和通用元数据。在下面的示例中，我们将使用 [jq](https://europe-west1-atp-views-tracker.cloudfunctions.net/working-analytics?notebook=tutorials--docker-intro--readme&click=github-jq&target=https%3A%2F%2Fjqlang.github.io%2Fjq%2F&text=jq) 从元数据 JSON 文件中提取层的信息：

``` shell
> docker inspect rkrispin/vscode-python:ex1 | jq '.[] | .RootFS'
{
  "Type": "layers",
  "Layers": [
    "sha256:332b199f36eb054386cd2931c0824c97c6603903ca252835cc296bacde2913e1",
    "sha256:2f98f42985b15cbe098d2979fa9273e562e79177b652f1208ae39f97ff0424d3",
    "sha256:964529c819bb33d3368962458c1603ca45b933487b03b4fb2754aa55cc467010",
    "sha256:e67fb4bad8f42cca08769ee21bbe15aca61ab97d4a46b181e05fefe3a03ee06d",
    "sha256:037f26f869124174b0d6b6d97b95a5f8bdff983131d5a1da6bc28ddbc73531a5",
    "sha256:737cec5220379f795b727e6c164e36e8e79a51ac66a85b3e91c3f25394d99224",
    "sha256:65f4e45c2715f03ed2547e1a5bdfac7baaa41883450d87d96f877fbe634f41a9",
    "sha256:baef981f26963b264913e79bd0a1472bae389441022d71f559e9d186600d2629",
    "sha256:88e1d36ff4812423afc93d5f6208f2783df314d5ecf6f961325c65e1dbf891da"
  ]
}

```

正如你可以从上面镜像层输出中看到的，`rkrispin/vscode-python:ex1` 镜像有九个层。每一层都由其哈希键（例如 `sha256:...`）表示，并在后端被缓存。虽然我们在构建输出中看到 docker 引擎从 `FROM` 和 `RUN` 命令触发了两个过程，但我们最终得到的是九个层，而不是两个。主要原因在于，导入基础镜像时，我们继承了被导入镜像的特性，包括其层。在本例中，我们使用 `FROM` 导入了官方 Python 镜像，它包含八个层，然后通过执行 `RUN` 命令添加了第 9 层。你可以通过拉取基础镜像并使用 inspect 命令查看其层来测试这一点：

``` shell
> docker pull python:3.10
3.10: Pulling from library/python
bba7bb10d5ba: Already exists 
ec2b820b8e87: Already exists 
284f2345db05: Already exists 
fea23129f080: Already exists 
7c62c924b8a6: Already exists 
c48db0ed1df2: Already exists 
f614a567a403: Already exists 
00c5a00c6bc2: Already exists 
Digest: sha256:a8462db480ec3a74499a297b1f8e074944283407b7a417f22f20d8e2e1619782
Status: Downloaded newer image for python:3.10
docker.io/library/python:3.10

> docker inspect python:3.10 | jq '.[] | .RootFS'
{
  "Type": "layers",
  "Layers": [
    "sha256:332b199f36eb054386cd2931c0824c97c6603903ca252835cc296bacde2913e1",
    "sha256:2f98f42985b15cbe098d2979fa9273e562e79177b652f1208ae39f97ff0424d3",
    "sha256:964529c819bb33d3368962458c1603ca45b933487b03b4fb2754aa55cc467010",
    "sha256:e67fb4bad8f42cca08769ee21bbe15aca61ab97d4a46b181e05fefe3a03ee06d",
    "sha256:037f26f869124174b0d6b6d97b95a5f8bdff983131d5a1da6bc28ddbc73531a5",
    "sha256:737cec5220379f795b727e6c164e36e8e79a51ac66a85b3e91c3f25394d99224",
    "sha256:65f4e45c2715f03ed2547e1a5bdfac7baaa41883450d87d96f877fbe634f41a9",
    "sha256:baef981f26963b264913e79bd0a1472bae389441022d71f559e9d186600d2629"
  ]
}
```

### 层缓存

Docker 的一个缺点是镜像构建时间。随着 Dockerfile 复杂度提高（例如大量依赖），构建时间会变长。有时，你的构建第一次不会如预期那样执行。要么缺少某些要求，要么构建过程中出现了问题。这正是使用缓存帮助减少镜像重建时间的地方。Docker 有智能机制，可以识别每一层是应该从零开始构建，还是可以复用缓存层以节省时间。例如，让我们在上一个示例中添加另一条命令来安装 `vim` 编辑器。一般来说，我们可以（也应该）把它加到我们用来安装 `curl` 包的同一个 apt-get 中，但为了展示层缓存功能，我们将单独运行它：


`./examples/ex2/Dockerfile`
``` Dockerfile
FROM python:3.10

LABEL example=1

ENV PYTHON_VER=3.10

RUN apt-get update && apt-get install -y --no-install-recommends curl

RUN apt-get update && apt-get install -y --no-install-recommends vim
```

我们将使用下面的命令来构建这个镜像，并将其标记为 `rkrispin/vscode-python:ex2`：

``` shell
docker build . -f ./examples/ex-2/Dockerfile -t rkrispin/vscode-python:ex2 --progress=plain
```
你应该会看到类似下面的输出（如果你运行过上一次构建）：

``` shell
 => [internal] load build definition from Dockerfile                                                                                                                                     0.0s
 => => transferring dockerfile: 234B                                                                                                                                                     0.0s
 => [internal] load .dockerignore                                                                                                                                                        0.0s
 => => transferring context: 2B                                                                                                                                                          0.0s
 => [internal] load metadata for docker.io/library/python:3.10                                                                                                                           0.0s
 => [1/3] FROM docker.io/library/python:3.10                                                                                                                                             0.0s
 => CACHED [2/3] RUN apt-get update && apt-get install -y --no-install-recommends curl                                                                                                   0.0s
 => [3/3] RUN apt-get update && apt-get install -y --no-install-recommends vim                                                                                                          34.3s
 => exporting to image                                                                                                                                                                   0.4s 
 => => exporting layers                                                                                                                                                                  0.4s 
 => => writing image sha256:be39eb0eb986f083a02974c2315258377321a683d8472bac15e8d5694008df35                                                                                             0.0s 
 => => naming to docker.io/rkrispin/vscode-python:ex2   
 ```


正如从上面的构建输出中可以注意到的，第一层和第二层已经从上一次构建中存在了。因此，docker 引擎把它们的缓存层添加到镜像中（而不是从零开始构建它们），只构建第 3 层并安装 vim 编辑器。

**注意：** 默认情况下，构建输出是简洁短小的。你可以通过添加 `progress` 参数并将其设置为 `plain`，在构建期间获得更详细的输出：

``` shell
> docker build . -f ./examples/ex-2/Dockerfile -t rkrispin/vscode-python:ex2 --progress=plain
#1 [internal] load .dockerignore
#1 transferring context: 2B done
#1 DONE 0.0s

#2 [internal] load build definition from Dockerfile
#2 transferring dockerfile: 234B done
#2 DONE 0.0s

#3 [internal] load metadata for docker.io/library/python:3.10
#3 DONE 0.0s

#4 [1/3] FROM docker.io/library/python:3.10
#4 DONE 0.0s

#5 [2/3] RUN apt-get update && apt-get install -y --no-install-recommends curl
#5 CACHED

#6 [3/3] RUN apt-get update && apt-get install -y --no-install-recommends vim
#6 CACHED

#7 exporting to image
#7 exporting layers done
#7 writing image sha256:be39eb0eb986f083a02974c2315258377321a683d8472bac15e8d5694008df35 0.0s done
#7 naming to docker.io/rkrispin/vscode-python:ex2 done
#7 DONE 0.0s
```

由于我们在上一次构建中已经缓存了第 3 层，上面输出中的所有层都是缓存的，运行时间不到 1 秒。

在设置你的 Dockerfile 时，你应该注意并有策略地处理层缓存过程。层的顺序确实很重要！下面的图片展示了 docker 引擎何时使用缓存层以及何时重建它们。第一张图说明了初始构建：

<br>
<br /><figure>
<img src="assets/docker layers 1.png" width="100%" align="center"/></a>
<figcaption> 图 5 - 镜像初始构建的图示。左侧代表 Dockerfile 的命令，右侧代表对应的层</figcaption>
</figure>

<br>
<br />

在本例中，我们有一个包含四条命令的 Dockerfile，在构建时被转换为四个层。如果我们在第三条命令之后添加第五条命令会发生什么？docker 引擎会识别出 Dockerfile 中第一条和第二条命令没有变化，因此会使用对应的缓存层（第一层和第二层），并从零开始重建其余层：

<br>
<br /><figure>
<img src="assets/docker layers 2.png" width="100%" align="center"/></a>
<figcaption> 图 6 - 镜像重建期间缓存过程的图示</figcaption>
</figure>
<br>
<br />

在规划你的 Dockerfile 时，如果适用，一个好的做法是把最可能保持不变的命令放在前面，并尽可能把新的更新放到文件末尾。

那只是冰山一角，关于 Docker 还有很多可学的。下一节将探索在容器内运行 Python 的不同方法。

## Docker 运行

在前面的章节中，我们看到了如何用 `Dockerfile` 定义镜像要求，并用 `build` 命令构建它。本节重点介绍使用 `docker run` 命令在容器内运行 Python。

`docker run` 或 `run` 命令让我们能够从镜像创建并运行一个新容器。通常，`run` 命令用于启动一个容器化的应用或服务器，或按照以下语法执行代码：

``` shell
docker run [OPTIONS] IMAGE [COMMAND] [ARG...]
```

例如，我们可以将 `run` 命令用于官方 Python 3.10 镜像：

``` shell
docker run python:3.10 
```

令人惊讶（或不惊讶）的是，什么都没发生。为了更好地理解这一点，我们需要回到 `Dockerfile`。一般来说，镜像可以用于运行：
- 服务器
- 应用

在这两种情况下，我们都使用 `Dockerfile` 来设置并在运行时启用它们的启动。对于服务器，我们使用 `Dockerfile` 上的 `PORT` 和 `CMD` 命令分别设置镜像上的服务器端口并启动服务器。然后我们使用 `run` 命令并添加 `-p`（或 `--publish list`）选项，把服务器的端口映射到本地端口。类似地，要启动一个应用，我们使用 `Dockerfile` 上的 `CMD` 命令在运行时定义启动命令，并使用 `--interactive` 和 `--tty` 选项以交互模式启动容器，这让我们能够访问该应用。

现在让我们回到 `python:3.10` 镜像，使用 `inspect` 命令检查是否定义了 `CMD` 命令：

``` shell
> docker inspect python:3.10 | jq '.[] | .Config.Cmd'
[
  "python3"
]
```

**注意：** 我们再次使用 `jq` 库从 JSON 输出中解析出 CMD 元数据

正如你所看到的，`python:3.10` 镜像上的 `CMD` 被设置为运行默认的 Python 启动命令 - `python3`，它在运行时启动 Python。现在让我们添加 `--interactive` 和 `--tty` 选项，以交互模式运行容器：

```shell
 docker run --interactive --tty python:3.10 
 ```
这会启动镜像上的默认 Python 版本。然后我们可以通过使用 `print` 命令打印 `Hello World!` 来测试它：

```python
Python 3.10.12 (main, Jun 14 2023, 18:40:54) [GCC 12.2.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> print("Hello World!")
Hello World!
>>> 
```

## 卷挂载（Volume Mounting）

正如你在上面输出中注意到的，`docker run` 命令在 bash 终端内启动了容器。默认情况下，容器在一个临时（ephemeral）环境中运行，这意味着我们在镜像内创建的任何代码都无法导出，并且会在我们停止容器运行后丢失。


一个简单的解决方案是使用卷参数挂载一个卷。为简单起见，我们继续挂载本地文件夹 `ex3`，其中包含以下 Python 脚本：
`hello-world.py`
``` python
print("Hello World!")
```

在启动容器之前，让我们重新构建镜像，并添加 `CMD` 指令，以便在容器内启动 bash 终端而不是 Python。我们将使用下面的 `Dockerfile`：

`./examples/ex3/Dockerfile`
``` Dockerfile
FROM python:3.10

LABEL example=3

ENV PYTHON_VER=3.10

RUN apt-get update && apt-get install -y --no-install-recommends curl

RUN apt-get update && apt-get install -y --no-install-recommends vim

CMD ["/bin/sh", "-c", "bash"]
```

这将让我们能够访问文件系统并从 bash 终端运行脚本。

让我们再次构建镜像，但这次使用我们刚创建的 Dockerfile：

```shell
docker build . -f ./examples/ex3/Dockerfile -t rkrispin/vscode-python:ex3
```

然后用以下命令启动它：

```
docker run -v .:/ex3  --interactive --tty rkrispin/vscode-python:ex3
```



我们将运行该命令，并使用卷参数把本地文件夹 ex3 映射为我们容器中的一个卷。我们可以通过运行以下命令来实现：

``` shell
docker run -v ./examples/ex3:/ex3  --interactive --tty python:3.10 
```
其中 `-v` 参数把本地文件夹 `./examples/ex3` 映射到我们容器中的 `/my_python_scipts`。这会启动容器并在容器内打开 bash 终端。正如你在下面看到的，`ls` 命令的输出返回了根文件夹下的文件和文件夹。其中包括我们用 `-v` 参数挂载的本地文件夹 -`my_python_scripts`：

```shell
root@8c94db531eb4:/# ls
bin  boot  dev	etc  home  lib	media  mnt  my_python_scipts  opt  proc  root  run  sbin  srv  sys  tmp  usr  var
root@8c94db531eb4:/# cd my_python_scipts/
root@8c94db531eb4:/my_python_scipts# ls
Dockerfile  hello-world.py
root@8c94db531eb4:/my_python_scipts# python hello-world.py
Hello World!
root@8c94db531eb4:/my_python_scipts#
```

使用这种技术，我们可以在本地维护代码，同时在容器内运行它。

## 容器化 AI Agent

到目前为止，我们已经回顾了如何设置 Dockerfile、构建镜像并将其作为容器运行。在本节中，我们将把这些点串联起来，演示如何将一个简单的 AI Agent 容器化，并在容器内运行它。

让我们先定义一个简单的 Python 脚本，它向 OpenAI API 发送请求并打印结果：

`./examples/ex4/simple_agent.py`
``` python
from openai import OpenAI

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "What is the capital of France?"}],
)

print(response.choices[0].message.content)
```

我们将用下面的 Dockerfile 包装这个 Python 脚本：
`./examples/ex4/Dockerfile`

``` Dockerfile
FROM python:3.10-slim

RUN pip install --no-cache-dir openai

COPY ./examples/ex4/simple_agent.py /app/simple_agent.py

CMD ["python", "/app/simple_agent.py"]
```
我们使用 `FROM` 命令拉取官方 Python 镜像 - 3.10 的 slim 版本（轻量）。接下来，我们使用 `RUN` 命令安装 `openai` Python 库，然后使用 `COPY` 命令把 Python 脚本从本地文件夹复制到镜像文件系统。最后但同样重要的是，我们将使用 `CMD` 命令在容器运行时执行该 Python 脚本。

接下来，我们将使用以下命令构建镜像：

``` shell
docker build . -f ./examples/ex4/Dockerfile -t rkrispin/simple_agent:ex4
```

在镜像运行期间，我们必须提供 OpenAI API key。作为最佳实践，你绝不应在构建期间把凭据或密钥存储在镜像上。相反，我们将使用 `--env`（或 `-e`）参数把 API key 设置为环境变量：

``` shell
docker run --env OPENAI_API_KEY=$OPENAI_API_KEY rkrispin/simple_agent:ex4
```
**注意：** 你应该把 `OPENAI_API_KEY` 替换为保存你 API key 的环境变量的名称。

你应该会看到类似下面的输出：

``` shell
The capital of France is Paris.
```

### 让容器功能化（Functionalize）

前面的示例很有限，用处不大，因为它只能回答一个问题。通过小幅调整，你可以让它变得动态，让用户能够提问。让我们从 Python 脚本开始：

`./examples/ex5/dynamic_agent.py`
```python
import os
from openai import OpenAI

client = OpenAI()

question = os.getenv("QUESTION", "What is the capital of France?")

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user",  "content": question}],
)

print(f"Question: {question}")
print(f"Answer: {response.choices[0].message.content}")
```

正如你所看到的，我们添加了一个名为 `QUESTION` 的环境变量，它将被用作我们 Agent 的输入。该脚本将打印问题和答案。

同样，我们将修改 Dockerfile：
``` Dockerfile
FROM python:3.10-slim

RUN pip install --no-cache-dir openai

COPY ./examples/ex5/dynamic_agent.py /app/dynamic_agent.py

ENV QUESTION="What is the capital of France?"

CMD ["python", "/app/dynamic_agent.py"]

```

**注意：** 虽然不是必须的，但为环境变量 QUESTION 设置一个默认值是个好做法。这样，如果用户没有为该变量提供值，它就会使用默认值。

让我们构建容器：

``` shell
docker build . -f ./examples/ex5/Dockerfile -t rkrispin/dynamic_agent:ex5
```

然后运行容器，并把问题设置为环境变量：
```shell
docker run --env OPENAI_API_KEY=$OPENAI_API_KEY --env QUESTION="What is the capital of United Kingdom"  rkrispin/dynamic_agent:ex5
```

这将返回以下输出：

```shell
Question: What is the capital of United Kingdom
Answer: The capital of the United Kingdom is London.
```

## 结论

在本教程中，我们回顾了 Docker 的基础。Docker 解决了软件开发的一个核心问题——可复现性。我们深入探讨了使用 `Dockerfile` 构建镜像的过程，并看了一个如何能在容器内运行代码的简单示例。最后但同样重要的是，我们演示了如何将一个简单的 AI Agent 容器化到容器中，并在运行时调用 OpenAI API。

这只是 Docker 所能做的事情的冰山一角，希望它让你了解你可以用 Docker 做什么，以及如何开始使用它。

---
本教程作者：[Rami Krispin](https://europe-west1-atp-views-tracker.cloudfunctions.net/working-analytics?notebook=tutorials--docker-intro--readme&click=linkedin-rami-krispin&target=https%3A%2F%2Fwww.linkedin.com%2Fin%2Frami-krispin%2F&text=Rami%20Krispin)
