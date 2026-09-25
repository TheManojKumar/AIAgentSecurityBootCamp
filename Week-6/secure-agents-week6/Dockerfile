FROM python:3.12-slim
WORKDIR /lab
# heavier image: red-team toolchain + docker CLI for the W4 sandbox path
# (docker-cli, not docker.io: on Debian 13+ the client is a separate package
#  and docker.io only Recommends it, which --no-install-recommends skips)
RUN apt-get update && apt-get install -y --no-install-recommends docker-cli curl \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV OLLAMA_HOST=http://host.docker.internal:11434
CMD ["python", "check_env.py"]
