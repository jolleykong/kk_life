# PROMPT="[%*] %n:%c $(git_prompt_info)%(!.#.$) "
# fork from geoffgarside.zsh-theme
PROMPT='[%*] %{$fg[cyan]%}%n%{$reset_color%}@%m:%{$fg[green]%}%c%{$reset_color%}$(git_prompt_info) %(!.#.$) '

ZSH_THEME_GIT_PROMPT_PREFIX=" %{$fg[yellow]%}git:("
ZSH_THEME_GIT_PROMPT_SUFFIX=")%{$reset_color%}"
