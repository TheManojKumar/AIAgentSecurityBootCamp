FROM python:3.12-slim
WORKDIR /lab
# heavier image: red-team toolchain + docker CLI for the W4 sandbox path
RUN apt-get update && apt-get install -y --no-install-recommends docker.io curl \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV OLLAMA_HOST=http://host.docker.internal:11434
CMD ["python", "check_env.py"]
