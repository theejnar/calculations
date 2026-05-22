# Ensure fish config/data directories exist before anything touches universal variables
mkdir -p $HOME/.config/fish $HOME/.local/share/fish

fish_add_path -g $HOME/.local/bin

set -gx HISTSIZE 50000

function mkcd
    mkdir -p -- $argv[1]; and cd -- $argv[1]
end

if command -q zoxide
    zoxide init fish | source
end

if command -q atuin
    atuin init fish | source
end
