export PATH="$HOME/.local/bin:$PATH"

# Persist history across container rebuilds (volume-backed)
export HISTFILE="$HOME/.bash_history_vol/.bash_history"
export HISTSIZE=50000
export HISTFILESIZE=50000
shopt -s histappend
export HISTCONTROL=ignoredups:ignorespace

mkcd () {
    mkdir -p -- "$1" && cd -- "$1"
}

if command -v zoxide 1>/dev/null 2>&1; then
  eval "$(zoxide init bash)"
fi

# bash-preexec provides the precmd/preexec hook framework that atuin needs
[[ -f ~/.bash-preexec.sh ]] && source ~/.bash-preexec.sh

if command -v atuin 1>/dev/null 2>&1; then
  eval "$(atuin init bash)"
else
  # Fallback: flush history after each command when atuin is not available
  PROMPT_COMMAND="history -a;${PROMPT_COMMAND:-}"
fi
