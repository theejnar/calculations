FROM mcr.microsoft.com/devcontainers/python:3.13

# Pin tool versions for reproducible builds
ARG DIFFT_VERSION=0.68.0
ARG UV_VERSION=0.11.2
ARG ZOXIDE_VERSION=0.9.9
ARG ATUIN_VERSION=v18.13.6

# Remove yarn repository that has untrusted GPG key
RUN rm -f /etc/apt/sources.list.d/yarn.list

# Install additional development tools and shells
RUN apt-get update && apt-get install -y \
    git \
    openssh-client \
    sqlite3 \
    zsh \
    fish \
    tmux \
    ripgrep \
    && rm -rf /var/lib/apt/lists/*

# Install difftastic (structural diff tool)
RUN curl -sfL "https://github.com/Wilfred/difftastic/releases/download/${DIFFT_VERSION}/difft-x86_64-unknown-linux-gnu.tar.gz" \
    -o /tmp/difft.tar.gz && \
    echo "f50c2d77f44a551fe24a7abfa955fbb893e6d0ab2a3767f39ca3823f0995dabd  /tmp/difft.tar.gz" | sha256sum -c - && \
    tar xz -C /usr/local/bin/ -f /tmp/difft.tar.gz && \
    rm /tmp/difft.tar.gz

# Install uv
RUN curl -LsSf "https://astral.sh/uv/${UV_VERSION}/install.sh" -o /tmp/uv-install.sh && \
    echo "a6ccba649ac029ce18500400019d60de389838d13a6751aa2908ede1b2aa3a87  /tmp/uv-install.sh" | sha256sum -c - && \
    sh /tmp/uv-install.sh && \
    mv /root/.local/bin/uv /usr/local/bin/ && \
    mv /root/.local/bin/uvx /usr/local/bin/ && \
    rm /tmp/uv-install.sh

# Install zoxide (smarter cd)
RUN curl -sfL "https://github.com/ajeetdsouza/zoxide/releases/download/v${ZOXIDE_VERSION}/zoxide-${ZOXIDE_VERSION}-x86_64-unknown-linux-musl.tar.gz" \
    -o /tmp/zoxide.tar.gz && \
    echo "4ff057d3c4d957946937274c2b8be7af2a9bbae7f90a1b5e9baaa7cb65a20caa  /tmp/zoxide.tar.gz" | sha256sum -c - && \
    tar xz -C /usr/local/bin/ zoxide -f /tmp/zoxide.tar.gz && \
    rm /tmp/zoxide.tar.gz

# Install atuin (shell history) and generate offline encryption key
# Use musl build (statically linked) — the gnu build requires glibc ≥2.39 which Debian 12 doesn't have
RUN curl -sfL "https://github.com/atuinsh/atuin/releases/download/${ATUIN_VERSION}/atuin-x86_64-unknown-linux-musl.tar.gz" \
    -o /tmp/atuin.tar.gz && \
    echo "19712eadad816d328086553133f0933a9a4429d52dcf660e8feb8af9f7552f3e  /tmp/atuin.tar.gz" | sha256sum -c - && \
    tar xz --strip-components=1 -C /usr/local/bin/ atuin-x86_64-unknown-linux-musl/atuin -f /tmp/atuin.tar.gz && \
    rm /tmp/atuin.tar.gz && \
    su - vscode -c 'mkdir -p ~/.local/share/atuin && \
    python3 -c "import os,base64;print(base64.b64encode(os.urandom(32)).decode(),end=\"\")" > ~/.local/share/atuin/key && \
    chmod 600 ~/.local/share/atuin/key'

# Install oh-my-zsh for vscode user (skip if already exists)
# Pinned to a specific commit for reproducibility
ARG OMZ_COMMIT=a07126330b9f56f12f1e00ddd29786d35d6e64d9
RUN su - vscode -c 'if [ ! -d ~/.oh-my-zsh ]; then \
    git clone --depth 1 https://github.com/ohmyzsh/ohmyzsh.git ~/.oh-my-zsh && \
    cd ~/.oh-my-zsh && git fetch --depth 1 origin '"${OMZ_COMMIT}"' && git checkout '"${OMZ_COMMIT}"'; \
    fi'

# Install oh-my-zsh plugins for vscode user (pinned to release tags)
RUN su - vscode -c 'git clone --branch v0.7.1 --depth 1 https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions 2>/dev/null || true' && \
    su - vscode -c 'git clone --branch 0.8.0 --depth 1 https://github.com/zsh-users/zsh-syntax-highlighting ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting 2>/dev/null || true' && \
    su - vscode -c 'git clone --branch 0.36.0 --depth 1 https://github.com/zsh-users/zsh-completions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-completions 2>/dev/null || true'

# Set working directory and permissions
WORKDIR /workspaces
RUN chown -R vscode:vscode /workspaces
