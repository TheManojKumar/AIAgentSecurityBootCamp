FROM python:3.12-slim
WORKDIR /lab
# docker CLI so the agent container can spawn a sibling sandbox container
RUN apt-get update && apt-get install -y --no-install-recommends docker.io \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV OLLAMA_HOST=http://host.docker.internal:11434
CMD ["python", "check_env.py"]
