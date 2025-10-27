# Function to parse git branch and set GIT_PROMPT variable
parse_git_branch() {
  # Check if we are in a git repository
  if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    # Get the current branch name
    local branch
    branch=$(git rev-parse --abbrev-ref HEAD)
    # Using tput to set colors.
    # 75 for light blue, 178 for mustard yellow.
    local light_blue
    light_blue=$(tput setaf 75)
    local mustard_yellow
    mustard_yellow=$(tput setaf 178)
    local reset_color
    reset_color=$(tput sgr0)
    # Note: \[ and \] are necessary to tell bash that the color codes are zero-width.
    GIT_PROMPT=" \[$light_blue\]git:(\[$mustard_yellow\]${branch}\[$light_blue\])"
  else
    GIT_PROMPT=""
  fi
}

# Function to set the final PS1 prompt
set_prompt() {
    parse_git_branch
    local user_color
    user_color=$(tput setaf 34)
    local dir_color
    dir_color=$(tput setaf 69)
    local reset_color
    reset_color=$(tput sgr0)
    PS1="\[$user_color\]\u \[$dir_color\]\w${GIT_PROMPT} \[$reset_color\]$ "
}

if [[ $- == *i* ]] && [ -t 1 ]; then
  # History settings: keep unique commands and share across sessions
  export HISTCONTROL=ignoredups:erasedups
  shopt -s histappend
  export HISTSIZE=10000
  export HISTFILESIZE=200000

  # Compose PROMPT_COMMAND to sync history then set the prompt, preserving any existing behavior
  # Ensure set_prompt appears only once
  case ";$PROMPT_COMMAND;" in
    *";set_prompt;"*) ;;
    *) PROMPT_COMMAND="${PROMPT_COMMAND:+$PROMPT_COMMAND; }set_prompt" ;;
  esac

  # Prepend history sync if not already present
  HISTORY_SYNC_CMD='history -a; history -c; history -r'
  case ";$PROMPT_COMMAND;" in
    *";history -a; history -c; history -r;"*) ;;
    *) PROMPT_COMMAND="$HISTORY_SYNC_CMD; $PROMPT_COMMAND" ;;
  esac
fi

if [ -x /usr/bin/dircolors ]; then
  test -r ~/.dircolors && eval "$(dircolors -b ~/.dircolors)" || eval "$(dircolors -b)"
  export LS_OPTIONS='--color=auto'
else
  export LS_OPTIONS=''
fi

SCRIPT_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

alias l='ls -1hpalFv --color=always --group-directories-first --time-style=long-iso'
alias lh='ls $LS_OPTIONS -Alh'
alias duh='du --max-depth 1 | sort -n | cut -f 2 | xargs -d'\''\n'\'' du -h --max-depth 0'
alias gl="git log --graph --abbrev-commit --decorate --format=format:'%C(bold blue)%h%C(reset) - %C(bold green)(%ar)%C(reset) %C(white)%s%C(reset) %C(dim white)- %an%C(reset)%C(bold yellow)%d%C(reset)' --all"
alias glr='gl -n 7'

export GPG_TTY=$(tty)
