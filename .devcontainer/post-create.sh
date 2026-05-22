#!/usr/bin/env bash
set -euo pipefail

# Block Bitbucket communication from within the container
if ! grep -q 'bitbucket.org' /etc/hosts; then
	echo "127.0.0.1 bitbucket.org api.bitbucket.org" | sudo tee -a /etc/hosts >/dev/null
fi

# Fix volume ownership (Docker creates volume mount points as root)
sudo chown -R vscode:vscode \
	/home/vscode/.bash_history_vol \
	/home/vscode/.zsh_history_vol \
	/home/vscode/.fish_history_vol \
	/home/vscode/.local/share/atuin

# Copy shell config files from repo into home directory
cp .devcontainer/.bashrc /home/vscode/.bashrc
cp .devcontainer/.zshrc /home/vscode/.zshrc
mkdir -p /home/vscode/.config/fish
cp .devcontainer/config.fish /home/vscode/.config/fish/config.fish

# Install bash-preexec (required by atuin for bash hook support)
# Pinned to release 0.6.0 with integrity check
BASH_PREEXEC_URL="https://raw.githubusercontent.com/rcaloras/bash-preexec/0.6.0/bash-preexec.sh"
BASH_PREEXEC_SHA256="998f4d5e9dd82e254463228cc6caa4d40125ae79b31d5a16a2a2f49357f0c160"
if [[ ! -f /home/vscode/.bash-preexec.sh ]]; then
    curl -sfL "$BASH_PREEXEC_URL" -o /home/vscode/.bash-preexec.sh
    echo "$BASH_PREEXEC_SHA256  /home/vscode/.bash-preexec.sh" | sha256sum -c -
fi

# Symlink only the fish history file (not the entire directory) for volume persistence
mkdir -p /home/vscode/.local/share/fish
touch /home/vscode/.fish_history_vol/fish_history
ln -sfn /home/vscode/.fish_history_vol/fish_history /home/vscode/.local/share/fish/fish_history

# Install Python dependencies
sudo uv pip install --system -e ".[dev]"
sudo uv pip install --system prek pylint

# Install pre-commit hooks (skip if git is unavailable, e.g. in worktrees)
if git rev-parse --git-dir >/dev/null 2>&1; then
	prek install
else
	echo 'Warning: skipping prek install — git not available (worktree not fully mounted)'
fi

# Set default shell to match host preference
HOST_SHELL="${1:-/bin/bash}"
case "$HOST_SHELL" in
*zsh) sudo chsh -s /usr/bin/zsh vscode ;;
*fish) sudo chsh -s /usr/bin/fish vscode ;;
*) sudo chsh -s /bin/bash vscode ;;
esac
