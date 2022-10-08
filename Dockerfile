# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.8-slim

# Current working Ip Address and port
ENV IP='127.0.0.1'
ENV PORT=8001

# Number of seconds per seed. To breaak the total delta to different number of seeds to split the chain
ENV SECONDS_PER_SEED=2

# Number of redundancies or verifiers. The more the better, but requires more nodes online
ENV REDUNDANCIES=2

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

WORKDIR /app
COPY . /app

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["python", "main.py"]
