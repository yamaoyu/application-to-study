# ベースイメージとしてDev ContainersのPythonイメージを使用
FROM mcr.microsoft.com/devcontainers/python:3.12

# Node.jsのバージョンをインストール
ARG NODE_VERSION="20"
RUN su vscode -c "export NVM_DIR=/usr/local/share/nvm && \
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.3/install.sh | bash && \
    . /usr/local/share/nvm/nvm.sh && \
    nvm install ${NODE_VERSION} && \
    nvm use ${NODE_VERSION} && \
    nvm alias default ${NODE_VERSION} && \
    npm install -g npm"

# 必要なパッケージをインストール
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive && \
    apt-get install -y \
    git \
    curl \
    build-essential \
    libssl-dev \
    libffi-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Pythonの依存関係をインストール
COPY backend/requirements.txt /tmp/pip-tmp/
RUN pip install --no-cache-dir -r /tmp/pip-tmp/requirements.txt && \
    rm -rf /tmp/pip-tmp

# Node.jsの依存関係をインストール
COPY frontend/package.json frontend/package-lock.json /tmp/npm-tmp/
RUN cd /tmp/npm-tmp && npm ci && rm -rf /tmp/npm-tmp

# ユーザーをvscodeに設定
USER vscode

# 作業ディレクトリを設定
WORKDIR /workspace