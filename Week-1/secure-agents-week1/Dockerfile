FROM python:3.12-slim
WORKDIR /lab
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV OLLAMA_HOST=http://host.docker.internal:11434
CMD ["python", "check_env.py"]
