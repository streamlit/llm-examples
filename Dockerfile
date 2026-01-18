# 1. 选底座：找一个装好了 Python 3.10 的轻量级 Linux 系统
# slim 版本比完整版小很多，适合生产环境
FROM python:3.10-slim

# 2. 设工位：在容器内部创建一个 /app 目录，把这里当作工作台
WORKDIR /app

# 3. 装依赖 (关键步骤！运维面试考点)
# 我们先只把 requirements.txt 拷进去，安装依赖
# 为什么不一次性全拷进去？因为依赖不常变，代码常变。
# 分开写可以让 Docker "缓存" 这一层。下次你只改代码时，就不需要重新 pip install 了。
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. 搬代码：把当前目录下剩下的所有文件（.py, pages文件夹等）都拷进容器
COPY . .

# 5. 开窗口：告诉外界，这个容器会占用 8501 端口 (Streamlit 默认端口)
EXPOSE 8501

# 6. 启动指令：容器一跑起来，就执行这句话
# --server.address=0.0.0.0 是必须的！
# 如果不加，Streamlit 默认只监听 localhost，你在容器外面（浏览器里）是访问不到的。
CMD ["streamlit", "run", "Chatbot.py", "--server.port=8501", "--server.address=0.0.0.0"]