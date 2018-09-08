**Py**thon program that tracks **games**.

This application is meant to run in the background.

* [roadmap](roadmap.md)
* [changelog](changelog.md)
* [installation](install.md)

## Run server
```sh
$ python3 src/main.py
```
## Run server as service
```sh
$ ln -s ~/gamesPy/gamesPy.service ~/.config/systemd/user/
$ systemctl --user daemon-reload
$ systemctl --user start gamesPy
```
## Run example client
```sh
$ python3 src/cliclient.py
```