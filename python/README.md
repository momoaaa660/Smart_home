# SmartHome后端
## 环境搭建
1. 创建虚拟环境
cd python && python -m venv .venv
2. 启动虚拟环境
.venv/Scripts/activate
3. 下载python依赖
pip install -r requirments.txt

> 依赖: MarkupSafe-3.0.2 aiosqlite-0.21.0 annotated-types-0.7.0 anyio-4.10.0 bcrypt-4.3.0 certifi-2025.8.3 cffi-1.17.1 click-8.2.1 colorama-0.4.6 cryptography-45.0.6 dnspython-2.7.0 ecdsa-0.19.1 email-validator-2.3.0 fastapi-0.116.1 fastapi-cli-0.0.8 fastapi-cloud-cli-0.1.5 greenlet-3.2.4 h11-0.16.0 httpcore-1.0.9 httptools-0.6.4 httpx-0.28.1 idna-3.10 jinja2-3.1.6 markdown-it-py-4.0.0 mdurl-0.1.2 paho-mqtt-2.1.0 passlib-1.7.4 pyasn1-0.6.1 pycparser-2.22 pydantic-2.11.7 pydantic-core-2.33.2 pygments-2.19.2 python-dateutil-2.9.0.post0 python-dotenv-1.1.1 python-jose-3.5.0 python-multipart-0.0.20 pyyaml-6.0.2 rich-14.1.0 rich-toolkit-0.15.0 rignore-0.6.4 rsa-4.9.1 sentry-sdk-2.35.1 shellingham-1.5.4 six-1.17.0 sniffio-1.3.1 sqlalchemy-2.0.43 starlette-0.47.3 typer-0.16.1 typing-extensions-4.15.0 typing-inspection-0.4.1 urllib3-2.5.0 uvicorn-0.35.0 watchfiles-1.1.0 websockets-15.0.1
> 
>模糊意图理解：灯太亮了
>上下文长对话：空调多少度？低一点？
>一键创建场景：我想设置一个电影模式......
>数据分析：实时分析（可燃气体报警、设备离线/传感器故障分析）、历史一览
> 习惯学习：每日七点起床，主动创建任务
> 动态调整：下雨不浇花
>
ai此时已经能够完成简单的通话，但是这些文件是不是只是简单定义了数据的传输结构，比如我现在告诉它我感觉有点冷，它能实现的业务逻辑是怎样的 
