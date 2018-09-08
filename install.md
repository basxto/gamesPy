# Linux
## Install Python
### Debian / Ubuntu
```sh
# apt-get install python3 python3-pip git
```
### ArchLinux / Manjaro
```sh
# pacman -S python python-pip git
```
## Getting all dependencies
```sh
# pip3 install xdg notify2 psutil flask
```


# Windows
_untested_

Get [chocolatey](https://chocolatey.org/)

Install via administrator terminal (Windows PowerShell or ConsoleZ)
```sh
# choco install python3 git
```
## Getting all dependencies
After installing python you  have to restart your terminal, then again with administrator rights do
```sh
# pip3 install psutil flask
```

```sh
git clone https://github.com/basxto/gamesPy.git
cd gamesPy
python3 src/main.py
```