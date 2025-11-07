# Innovation_Challenge_25

Change service_name | app_name | web_service to actual name

## Wanna Contribute? or just add files to repository a little bit easier?

if you have a mac development is a bit easier to get a hang of. All you need is to have xcode installed.

know how to access your computer's terminal. 

**on mac:**
cmd + space

type in `terminal`

__Windows Users__... if you are using a organization-managed device
**DONT** be too much work lol use something else

### Windows only

Better Tutorial than what I could give: [Here](https://learn.microsoft.com/en-us/windows/wsl/install)

After tutorial above:

```sh
#Start WSL by opening a command prompt and running wsl
sudo apt update
# Git is the only one needed if not coding
sudo apt install -y git curl build-essential libssl-dev libreadline-dev zlib1g-dev
sudo apt install -y nodejs yarn
```

... now !

use `ls` to figure out what folders are in your current directory.
use `cd` to navigate to a spot you want 

`git clone https://github.com/tbehr-core4ce/Innovation_Challenge_25.git`

## Suggested guides

[Markdown Basic Syntax Guide](https://www.markdownguide.org/basic-syntax/)

## Setting Up

### Typescript | Frontend

Install jq (on Ubuntu use sudo apt-get install jq)
Install wget

```Bash
#On Mac
brew install jq (on Ubuntu use sudo apt-get install jq)
brew install wget
```

Install NodeJS https://nodejs.org/en  
Once installed run `npm add -g pnpm`

Will need later to box up the python code?

Install Docker Desktop https://www.docker.com/get-started/  
If using mac or windows, you must enable host based routing (Settings > Resources > Network > [X] Enable host networking)

## Python | Backend

### Pipx

[Pipx Website | Documentation](https://pipx.pypa.io/stable/installation/)

- Required to download poetry and install dependencies

#### According to website ...

On macOS:

```
brew install pipx
pipx ensurepath
```

Additional (optional) commands

To allow pipx actions in global scope.

```
sudo pipx ensurepath --global
```

To prepend the pipx bin directory to PATH instead of appending it.

```
sudo pipx ensurepath --prepend
```
    Install via pip (requires pip 19.0 or later)

If you installed python using Microsoft Store, replace `py` with `python3` in the next line.

```
py -m pip install --user pipx
```

### Poetry

[Poetry Documentation](https://python-poetry.org/docs/)

```
pipx install poetry
```


```
python3 -m venv <myvenv>
```

For `<myvenv>` I used .venv.

You do not need the while loop but it is something I saw in a different project, because apparently for some systems it doesn't work at all times. So just spam it incase.

```Bash
while ! poetry install --no-root; do echo "..."; done
# Activate virtual environment
source $(poetry env info --path)/bin/activate
```
## Starting up

`pnpm dev`

``` docker compose up ```
or
``` uvicorn src.main:app --reload --host 0.0.0.0 --port 8000```