> 📄 English: [README.md](README.md)

![](https://europe-west1-atp-views-tracker.cloudfunctions.net/working-analytics?notebook=tutorials--runpod-gpu-deploy--readme)

# 使用 RunPod Serverless 部署 AI Agent

## 概览

本教程演示如何使用 RunPod 的 Serverless 基础设施部署 AI Agent。我们将构建并部署一个使用 Ollama 模型的 CrewAI 写作 Agent，创建一个可扩展的 API 端点，根据用户给定的主题生成文章。你将学到容器化、Serverless 部署，以及如何在不管理基础设施的情况下处理动态扩缩容。

## 详细说明

### 动机

传统上，部署 AI Agent 需要大量的基础设施管理——配置服务器、配置自动扩缩容、管理负载均衡器以及处理成本优化。这为那些希望专注于构建智能 Agent 而不是管理基础设施的开发者设置了障碍。

**Serverless 部署从根本上改变了这一范式**，它完全消除了基础设施方面的顾虑。开发者不再管理服务器，而是简单地把代码打包进容器，这些容器会在请求到达时自动执行。RunPod 会自动处理所有扩缩容、负载均衡和资源分配。

这种方法对 AI Agent 尤其有价值，因为 AI Agent 的使用模式不可预测且操作资源密集。使用 RunPod 的 serverless 端点，你只需为你的 Agent 实际使用的计算时间付费。

### 什么是 RunPod

RunPod 是一个为 AI、ML 和通用计算需求而构建的云计算平台。RunPod 让你能轻松启动远程 GPU/CPU 服务器，并提供一种无缝的方式来部署和扩展你的工作负载。

### 我们将要部署的应用

[请参考本仓库中的文件](./crew-ai-ollama-runpod-tutorial/README.md) 获取本教程引用的文件。

目标是创建一个 API 端点，用户可以向它传入一个主题，Agent 进行一些研究（已经为 Agent 提供了一个伪研究工具），并基于 Agent 的研究返回一篇简短的文章。

### 关键组件

我们的部署架构由三个协同工作的基本组件组成：

**CrewAI 框架**：一个多 Agent 系统，协调多个 AI 工作者完成复杂任务。在我们的例子中，它管理着一个研究 Agent 和一个写作 Agent，它们协作生成博客内容。

**Ollama 运行时**：一个本地语言模型服务器，直接在我们的容器中运行像 OpenHermes 这样的模型。这消除了对外部 API 的依赖，并提供更快、更可靠的推理。

**RunPod Serverless**：一个针对 GPU 优化的 serverless 平台，自动管理 AI 工作负载的容器生命周期、扩缩容和资源分配。

### 方法概览

我们的部署方法遵循以下工作流：

1. **容器化**：把 CrewAI 应用、Ollama 运行时和语言模型打包到一个 Docker 容器中
2. **Handler 定义**：创建一个处理传入请求并协调 AI Agent 的 Python 函数
3. **Serverless 部署**：使用自动扩缩容配置，把容器部署到 RunPod 的 serverless 基础设施
4. **API 集成**：通过一个接收主题并返回生成内容的 REST API 端点暴露该 Agent

这种方法把一个复杂的多组件 AI 系统转变为一次简单的 API 调用，所有基础设施问题都自动处理。

### 关键优势

Serverless 方法具有若干优势：
- **自动扩缩容**：容器根据请求量自动启动和关闭
- **成本效率**：只为实际计算时间付费，而不是为闲置资源付费
- **零基础设施管理**：无需配置服务器或处理扩缩容逻辑
- **内置负载均衡**：RunPod 在可用 worker 之间分配请求

## 注册 RunPod

### 注册页面
访问 [RunPod 注册页面](https://europe-west1-atp-views-tracker.cloudfunctions.net/working-analytics?notebook=tutorials--runpod-gpu-deploy--readme&click=runpod-nirdiamant&target=https%3A%2F%2Fget.runpod.io%2Fnirdiamant&text=RunPod%20Sign%20Up%20Page) 创建你的账户。

## 为 RunPod 准备应用

### 理解 Serverless 端点

RunPod 为容器化应用提供了一个云计算平台，你可以使用 RunPod 的 `runpod SDK` 绑定一个 Python 函数，当你的 RunPod 端点被访问时执行它。

因此，我们需要采取的步骤是：
- 定义 Handler
- 容器化我们的应用
- 将应用部署到 RunPod
- 测试应用
- 理解未来的维护

### 定义 Handler

绑定一个要执行的 Python 函数很简单。使用 SDK，我们只需用下面这一行绑定一个 Python 函数：`runpod.serverless.start({"handler": handler})`。这让我们能定义一个入口点，让你的 Agent 基于发送到 RunPod 端点的请求来执行。

入口函数应该能够接收结构如下的 JSON 请求：

```python
{
    "input": {
        ...
    }
}
```

所以参考[我们示例代码中的](./crew-ai-ollama-runpod-tutorial/handler.py) `handler.py`，我们可以看到最重要的部分，我们在那里定义了这样一个 handler，从用户请求中接收一个主题并运行我们的研究函数。

```python
import runpod
...

def create_blog_post(topic):
    """Creates a blog post on the given topic using CrewAI"""
    # Create the task for our topic
    blog_task = Task(
        description=f"""
        Write a blog post about {topic}.
        
        Your blog should:
        1. Have an attention-grabbing title
        2. Include a brief introduction that hooks the reader
        3. Present 3-4 main points supported by research
        4. End with a conclusion and potentially a call to action
        ...

def handler(job):
    """Handler function that will be used to process jobs."""
    job_input = job["input"]
    
    # Extract the topic from job input, default to "technology" if not provided
    topic = job_input.get("topic", "technology")
    
    try:
        # Generate blog post using CrewAI
        blog_post = create_blog_post(topic)
        
        # Return successful response
        return {
            "status": "success",
            "blog_post": blog_post
        }
    except Exception as e:
        # Return error response if something goes wrong
        return {
            "status": "error",
            "message": str(e)
        }


runpod.serverless.start({"handler": handler})
```

### 容器化我们的应用

使用 Docker，我们可以通过把所有的依赖、代码和运行时环境打包进一个可移植的容器来“容器化”我们的应用。这确保我们的 AI Agent 在不同环境中一致地运行——从你的本地机器到 RunPod 的服务器。该容器包含所有需要的东西：基础操作系统、Python 包、Ollama 模型和我们的应用代码，从而消除了“在我机器上能跑”的问题。

#### 我们 Dockerfile 的重要亮点

FROM runpod/pytorch:2.0.1-py3.10-cuda11.8.0-devel-ubuntu22.04

...

# Install Python dependencies
COPY requirements.txt /requirements.txt
RUN pip install --upgrade pip && \
    pip install uv && \
    uv pip install --upgrade -r /requirements.txt --no-cache-dir && \
    uv pip install "langchain-community>=0.0.34" --no-cache-dir && \
    python -c "import crewai; print(f'\nCrewAI version: {crewai.__version__}')" && \
    python -c "import crewai_tools; print('CrewAI Tools import successful')"

...

# Download model during build with better handling
RUN ollama serve > /dev/null 2>&1 & \
    sleep 25 && \
    ollama pull openhermes && \
    sleep 10 && \
    pkill ollama

...

# Startup script
CMD ["/start.sh"]

#### 要点

在容器化我们的应用时，我们只是想要创建一个可以启动的可复现环境。实际上 RunPod 提供了多种 Docker 镜像和模板。

![example](assets/docker_templates.png)

##### 基础模板
在本例中，`runpod/pytorch:2.0.1-py3.10-cuda11.8.0-devel-ubuntu22.04` 作为我们的基础模板，因为它已经预装了许多包，并提供了一个便于在其上添加更多包的简单基础。

##### 安装 Python 依赖

在下一步中，我们只需下载我们所需的 Python 包，主要是 crewAI。

```dockerfile
COPY requirements.txt /requirements.txt
RUN pip install --upgrade pip && \
    pip install uv && \
    uv pip install --upgrade -r /requirements.txt --no-cache-dir && \
    uv pip install "langchain-community>=0.0.34" --no-cache-dir && \
    python -c "import crewai; print(f'\nCrewAI version: {crewai.__version__}')" && \
    python -c "import crewai_tools; print('CrewAI Tools import successful')"
```

##### 安装 Ollama
最后，下载 Ollama 模型，把它烘焙到镜像中。
```dockerfile
RUN ollama serve > /dev/null 2>&1 & \
    sleep 25 && \
    ollama pull openhermes && \
    sleep 10 && \
    pkill ollama
```

#### 注意事项
在构建这个 Dockerfile 时，Serverless 的工作方式是：当有请求到来时，RunPod 会下载、缓存并初始化一个 Docker 容器。这意味着如果可能的话，最好把模型下载到镜像本身中，这样当容器启动时，它已经具备了必要的资源。

如果在执行时还需要下载额外资源（如 Ollama 模型），这会增加响应的延迟。因此，这就是为什么最好尝试把模型烘焙到 Docker 镜像中。

## 部署我们的应用

当你进入 Serverless 标签页时，在部署“New Endpoint”时有两个选项：Docker Image 或 Github Repo。

![example](assets/endpoint_creation_options.png)
![example](assets/endpoint_source_selection.png)

### Github 集成

通过连接你的 Github Repo，RunPod 会自动为你构建并部署镜像。该镜像会被直接推送到 RunPod。

### Docker 镜像

你也可以构建自己的 docker 镜像。所以在本例中，对于 github 仓库，可以使用以下命令构建并推送到 Dockerhub：

```bash
docker build -t justinrunpod/agents:1.0 . --push --platform linux/amd64
```

![example](assets/docker_image_selection.png)

### 选择硬件

选择使用 Docker Image 还是 Github Repo 之后，你将被要求选择要动态分配的硬件。

RunPod 提供了一批 GPU 池，RunPod 会根据可用性自动轮换你按优先级选择的 GPU。

![example](assets/hardware_selection.png)
![example](assets/gpu_prioritization.png)

### 最小和最大 Worker 数

Worker 是当你的端点收到请求时被初始化的容器实例。你通常会看到 worker 处于 `idle`（空闲）状态，这意味着它们在待命，等待请求到来。

你只需为 worker 在启动和响应请求时的实际计算时间付费——你不需要为 `idle` 状态付费。

#### 注意：
![example](assets/worker_allocation.png)

当你创建 worker 时，即使你可能定义了 `3` 个最大 worker，RunPod 也会尝试额外分配几个 worker，以帮助在必要时替换任何被 `throttled`（占用中）的 worker。这样你的应用在最优情况下始终会有你定义的 `max workers` 处于 `idle` 状态并随时准备响应。

### FlashBoot

如果你的应用流量很高，FlashBoot 是 RunPod 的一项功能，可以减少冷启动——即启动机器并把资源加载到内存所需的初始加载时间。冷启动是用户在 serverless 函数需要从零开始初始化时所经历的延迟——这可能包括启动容器、把模型加载到内存以及建立连接。FlashBoot 使这种启动时间降到最低，尤其是对于流量需求更高的应用。

## 测试我们的应用

### 端点
在仪表盘中，你可以看到有一个可以发起请求的端点。你可以直接在仪表盘中运行测试请求，也可以通过编程方式发起请求。

### 内置仪表盘
使用 RunPod 内的 request 标签页，你实际上可以直接在浏览器中运行测试请求。
![example](assets/test_request_dashboard.png)
![example](assets/test_request_input.png)
![example](assets/test_request_output.png)

### cURL / Python / Javascript
创建 API Key 之后，你可以通过编程方式向你的端点发起请求。

```bash
curl --request POST \
     --url https://api.runpod.ai/v2/[ENDPOINT_ID]/run \
     --header "accept: application/json" \
     --header "authorization: [YOUR_API_KEY]" \
     --header "content-type: application/json" \
     --data '
{
  "input": {
    "topic": "Technology"
  }
}
'
```

## 未来维护

### Docker 镜像新版本
如果你有新版本，可以提供更新后的 Docker 镜像。这样做时，它会执行滚动更新，一旦准备好，就会无缝地把你的 worker 切换到新镜像。

![example](assets/docker_image_update.png)

### Github 集成
如果你向 Github 提交了新 commit，你会看到新版本自动部署并为你滚动发布。

![example](assets/github_integration_update.png)

## 结论

在本教程中，我们走完了使用 RunPod serverless 基础设施部署 AI Agent 的完整流程。以下是我们完成内容的总结：

1. **设置 RunPod 账户**并探索平台
2. **准备我们的应用**，定义一个响应 API 请求的 handler 函数
3. **容器化我们的应用**，使用 Docker，包括把 Ollama 模型烘焙进去以获得更快的响应时间
4. **将应用部署到 RunPod**，使用它们的 serverless 基础设施
5. **测试应用**，通过仪表盘界面和编程式 API 调用两种方式
6. **了解如何维护应用**，通过 Docker 镜像更新和 GitHub 集成

这种 serverless 方法让你能够部署可根据需求自动扩缩容的 AI Agent，而无需你管理底层基础设施。你只需为你实际使用的计算时间付费，这对低流量和高流量的应用都具有成本效益。

本教程涵盖的基础知识让你能够部署复杂的 AI 工作流，从原型扩展到生产，而无需大量的 DevOps 专业知识或基础设施投入。
