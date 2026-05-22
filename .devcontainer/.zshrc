
# Path to your Oh My Zsh installation.
export ZSH="$HOME/.oh-my-zsh"
export PATH="$HOME/.local/bin:$PATH"

# Persist history across container rebuilds (volume-backed)
export HISTFILE="$HOME/.zsh_history_vol/.zsh_history"
export HISTSIZE=50000
export SAVEHIST=50000
setopt APPEND_HISTORY
setopt INC_APPEND_HISTORY
setopt SHARE_HISTORY
setopt HIST_IGNORE_DUPS
setopt HIST_IGNORE_SPACE

ZSH_THEME="agnoster"

plugins=(git zsh-autosuggestions zsh-syntax-highlighting zsh-completions)
source $ZSH/oh-my-zsh.sh

mkcd () {
    mkdir -p -- "$1" && cd -- "$1"
}

autoload -U compinit
compinit

if command -v zoxide 1>/dev/null 2>&1; then
  eval "$(zoxide init zsh)"
fi

if command -v atuin 1>/dev/null 2>&1; then
  eval "$(atuin init zsh)"
fi
