# Godot Issuebot

Simple bot to ferry between rocket.chat and Github. If you want to run one for yourself you can build the container.

What does it do? It will add issue/pr links to messages that mention a valid issue. Either by typing `#1335` to go to the default repository or `repository#345` for a particular one. The bot will edit the message in question and add links, description, and status to the message.

## Environment variables
The following environment variables are supported:

 * `BOT_DEBUG` - Turn on exessive debug messages when set
 * `DEFAULT_AVATAR_URL` - *required* url to some image if gh can't provide an avatar
 * `DEFAULT_REPOSITORY` - *required* default repository to search if a 'bare' issue # gets sent
 * `ROCKET_WS_URL` - *required* url to the rocket.chat server (wss://chat.godotengine.org/websocket)
 * `ROCKET_USERNAME` - *required* username of the rocket.chat user to login as
 * `ROCKET_PASSWORD` - *required* password of the rocket.chat user
 * `GITHUB_PROJECT` - *required* github project to search in
 * `GITHUB_USERNAME` - *required* username to use for the github APIs
 * `GITHUB_TOKEN` - *required* github user token to authenticate to the APIs with

## Running without a container

Requirements are pretty small, only python-requests and python-websockets are required. After that make sure you set the above env variables and you're good to go!

## Running the bot through podman

Docker users can probable just replace `podman` with `docker`

 * clone the repostiory
 * `podman build . -t issuebot:latest`
 * `podman run -it --env-file=env issuebot:latest`

example env file:
```
BOT_DEBUG=true
DEFAULT_AVATAR_URL=https://chat.godotengine.org/avatar/github
DEFAULT_REPOSITORY=godot
GITHUB_PROJECT=godotengine
ROCKET_WS_URL=wss://chat.godotengine.org/websocket
ROCKET_USERNAME=github
ROCKET_PASSWORD=supersecret
GITHUB_USERNAME=hpvb
GITHUB_TOKEN=verysecret
```
