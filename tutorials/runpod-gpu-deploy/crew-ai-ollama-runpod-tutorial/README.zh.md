> 📄 English: [README.md](README.md)

![](https://europe-west1-atp-views-tracker.cloudfunctions.net/working-analytics?notebook=tutorials--runpod-gpu-deploy--crew-ai-ollama-runpod-tutorial--readme)

# RunPod 上的 CrewAI + Ollama：Serverless AI Agent

## 概览

本仓库演示如何在 [RunPod](https://europe-west1-atp-views-tracker.cloudfunctions.net/working-analytics?notebook=tutorials--runpod-gpu-deploy--crew-ai-ollama-runpod-tutorial--readme&click=runpod-nirdiamant&target=https%3A%2F%2Fget.runpod.io%2Fnirdiamant&text=RunPod) 的 serverless 基础设施上部署一个 AI Agent 系统。示例应用会创建一个 API 端点，通过 AI Agent 工作流为任意主题生成博客文章。

关键组件：
- **CrewAI**：用于编排角色扮演式 AI Agent 的框架
- **Ollama**：用于在本地运行开源 LLM 的工具
- **RunPod**：用于 AI 部署的 Serverless GPU 基础设施

*引用自：[RunPod Worker Template](https://europe-west1-atp-views-tracker.cloudfunctions.net/working-analytics?notebook=tutorials--runpod-gpu-deploy--crew-ai-ollama-runpod-tutorial--readme&click=github-worker-template&target=https%3A%2F%2Fgithub.com%2Frunpod-workers%2Fworker-template&text=RunPod%20Worker%20Template)*

## RunPod 模板

使用我们预配置好的 RunPod 模板立即开始：

[<img src="https://img.shields.io/badge/RunPod-Deploy%20Now-blue?style=for-the-badge&logo=none" alt="Deploy on RunPod" width="200"/>](https://europe-west1-atp-views-tracker.cloudfunctions.net/working-analytics?notebook=tutorials--runpod-gpu-deploy--crew-ai-ollama-runpod-tutorial--readme&click=runpod-nirdiamant&target=https%3A%2F%2Fget.runpod.io%2Fnirdiamant&text=%3Cimg%20src%3D%22https%3A%2F%2Fimg.shields.io%2Fbadge%2FRunPod-Deploy%2520Now-blue%3Fstyle%3Dfor-the-badge%26logo%3Dnone%22%20alt%3D%22Deploy%20on%20RunPod%22%20width%3D%22200%22%2F%3E)

## 工作原理

这个应用会：
1. 通过 RunPod 暴露一个 API 端点
2. 接收一个主题作为输入
3. 使用 CrewAI 管理一个 AI Agent，该 Agent：
   - 研究该主题（在本例中使用一个模拟研究工具）
   - 撰写一篇结构化的博客文章
4. 将生成的博客文章作为 JSON 返回

## 架构

- **Handler 函数**：处理请求的入口点（handler.py）
- **博客写作 Agent**：为内容创作而配置的 AI Agent
- **模拟研究工具**：通过提供预定义的事实来模拟研究
- **Docker 容器**：与 Ollama 一起打包，用于 serverless 部署

## 快速开始

### 部署到 RunPod

#### 选项 1：使用 RunPod 模板（推荐）

1. 点击上面的“Deploy on RunPod”按钮
2. 配置你的端点设置
3. 部署并立即开始使用

#### 选项 2：构建并部署自定义镜像

1. 构建 Docker 镜像：
   ```bash
   docker build -t yourusername/crew-ai-ollama:latest . --platform linux/amd64
   docker push yourusername/crew-ai-ollama:latest
   ```

2. 在 RunPod 上创建一个新的 Serverless Endpoint
3. 选择“Docker Image”作为来源
4. 输入你的镜像 URL
5. 配置硬件设置（推荐：24GB+ 显存的 GPU）
6. 设置 worker 数量（最小：0，最大：根据预期流量）
7. 部署你的端点

## 使用

### API 端点

部署完成后，你的 RunPod 端点将提供如下格式的 URL：
```
https://api.runpod.ai/v2/[ENDPOINT_ID]/run
```

### 示例请求

```bash
curl --request POST \
     --url https://api.runpod.ai/v2/[ENDPOINT_ID]/run \
     --header "accept: application/json" \
     --header "authorization: [YOUR_API_KEY]" \
     --header "content-type: application/json" \
     --data '
{
  "input": {
    "topic": "artificial intelligence"
  }
}
'
```

### 示例响应

```json
{
  "delayTime": 14836,
  "executionTime": 10799,
  "id": "4c04615b-540f-4d82-917d-4eb4256acd96-u1",
  "output": {
    "blog_post": "Title: The Future of Technology: A Promising Horizon\n\nIntroduction:\nTechnology has been a driving force behind human progress, constantly evolving to meet the challenges of our time. In recent years, the pace of technological advancements has accelerated, and we stand on the precipice of an exciting new era. This blog post explores the current state of technology, highlights its most promising trends, and looks forward to what's in store for the future.\n\nMain Points:\n1. The Unrelenting Importance of Technology: As per recent research, 82% of industry leaders consider technology a pivotal area of focus, demonstrating its significance in shaping our world. From healthcare and education to communication and entertainment, technology continues to transform our daily lives.\n2. Rising Research Investments: Last year alone, spending on technology-related research grew by an impressive 34%. This surge in investment highlights the growing belief that technological innovation will be a primary catalyst for economic growth and societal progress.\n3. Soaring Consumer Interest: Consumer interest in technology has soared since 2022, with a staggering 56% increase recorded. This rapid growth is a testament to the increasing role of technology in our lives and its ability to address the evolving needs and desires of individuals worldwide.\n4. A Promising Horizon: Experts predict that the next five years will bring significant advancements in technology. From artificial intelligence and quantum computing to breakthroughs in biotechnology, the future promises a world of endless possibilities and new frontiers to explore.\n\nConclusion:\nThe future of technology is undoubtedly bright, with innovation driving us towards a more connected, efficient, and prosperous society. As we forge ahead into this exciting new era, it's crucial that we continue to invest in research, foster collaboration, and embrace the transformative potential of technology. Our collective commitment to harnessing its power will determine the extent to which we can leverage technology to overcome global challenges and shape a better tomorrow for all.\n\nCall to Action:\nJoin the conversation on social media using #FutureOfTech and share your thoughts about how technology is changing our world. Let's engage in a dialogue that fosters understanding, inspiration, and collective action towards an even brighter future.",
    "status": "success"
  },
  "status": "COMPLETED",
  "workerId": "fy17taoa4pyz2c"
}
```

## 关键文件

### handler.py

处理请求的主入口点：

```python
import runpod
from crewai import Agent, Task, Crew, LLM
from crewai.tools import tool
import os

# Configure Ollama LLM
llm = LLM(model="ollama/openhermes", base_url="http://localhost:11434")

# Create a pseudo-research tool that returns fake information
@tool("Research Tool")
def fake_research(topic: str) -> str:
    """
    Pretends to search for information about a topic. 
    Will always return some fake pre-defined content.
    """
    # ... returns fake research data
    
# Create blog writer agent
blog_writer = Agent(
    role="Blog Writer",
    goal="Write engaging and informative blog posts on various topics",
    backstory="You are a professional blog writer...",
    tools=[fake_research],
    verbose=True,
    llm=llm
)

def create_blog_post(topic):
    """Creates a blog post on the given topic using CrewAI"""
    # ... creates and executes the task

def handler(job):
    """Handler function that will be used to process jobs."""
    job_input = job["input"]
    topic = job_input.get("topic", "technology")
    
    try:
        blog_post = create_blog_post(topic)
        return {
            "status": "success",
            "blog_post": blog_post
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

runpod.serverless.start({"handler": handler})
```

### Dockerfile

包含创建应用容器化版本所需的配置：

```Dockerfile
FROM runpod/pytorch:2.0.1-py3.10-cuda11.8.0-devel-ubuntu22.04

# Install Python dependencies
COPY requirements.txt /requirements.txt
RUN pip install --upgrade pip && \
    pip install uv && \
    uv pip install --upgrade -r /requirements.txt --no-cache-dir && \
    uv pip install "langchain-community>=0.0.34" --no-cache-dir

# Download model during build
RUN ollama serve > /dev/null 2>&1 & \
    sleep 25 && \
    ollama pull openhermes && \
    sleep 10 && \
    pkill ollama

# Startup script
CMD ["/start.sh"]
```

## 性能注意事项

- 第一个请求可能会经历冷启动延迟，因为容器需要初始化
- 在 Docker 镜像中预加载 Ollama 模型可显著改善响应时间
- 根据主题复杂度，响应时间通常在 5-15 秒之间

## 扩展本项目

这个模板可以通过多种方式进行扩展：
- 用真实的网络搜索功能替换模拟研究工具
- 为内容创作的不同方面添加更多专门的 Agent
- 实现多个 Agent 协作的更复杂工作流
- 针对你的具体用例微调 LLM

## 致谢

- [CrewAI](https://europe-west1-atp-views-tracker.cloudfunctions.net/working-analytics?notebook=tutorials--runpod-gpu-deploy--crew-ai-ollama-runpod-tutorial--readme&click=github-crewai&target=https%3A%2F%2Fgithub.com%2FcrewAIInc%2FcrewAI&text=CrewAI)
- [Ollama](https://europe-west1-atp-views-tracker.cloudfunctions.net/working-analytics?notebook=tutorials--runpod-gpu-deploy--crew-ai-ollama-runpod-tutorial--readme&click=github-ollama&target=https%3A%2F%2Fgithub.com%2Follama%2Follama&text=Ollama)
- [RunPod](https://europe-west1-atp-views-tracker.cloudfunctions.net/working-analytics?notebook=tutorials--runpod-gpu-deploy--crew-ai-ollama-runpod-tutorial--readme&click=runpod-nirdiamant&target=https%3A%2F%2Fget.runpod.io%2Fnirdiamant&text=RunPod)
- [RunPod Worker Template](https://europe-west1-atp-views-tracker.cloudfunctions.net/working-analytics?notebook=tutorials--runpod-gpu-deploy--crew-ai-ollama-runpod-tutorial--readme&click=github-worker-template&target=https%3A%2F%2Fgithub.com%2Frunpod-workers%2Fworker-template&text=RunPod%20Worker%20Template)
