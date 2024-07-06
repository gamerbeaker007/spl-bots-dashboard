# Splinterlands bots dash board

Main:
[![Flake8](https://gamerbeaker007.github.io/spl-bots-dashboard/main/flake8-badge.svg)](https://gamerbeaker007.github.io/spl-bots-dashboard/main/flake8/)
[![Tests](https://gamerbeaker007.github.io/spl-bots-dashboard/main/junit-badge.svg)](https://gamerbeaker007.github.io/spl-bots-dashboard/main/junit/)
[![Tests Coverage](https://gamerbeaker007.github.io/spl-bots-dashboard/main/coverage-badge.svg)](https://gamerbeaker007.github.io/spl-bots-dashboard/main/coverage/) | branch:
[![Flake8](https://gamerbeaker007.github.io/spl-bots-dashboard/branch/flake8-badge.svg)](https://gamerbeaker007.github.io/spl-bots-dashboard/branch/flake8/)
[![Tests](https://gamerbeaker007.github.io/spl-bots-dashboard/branch/junit-badge.svg)](https://gamerbeaker007.github.io/spl-bots-dashboard/branch/junit/)
[![Tests Coverage](https://gamerbeaker007.github.io/spl-bots-dashboard/branch/coverage-badge.svg)](https://gamerbeaker007.github.io/spl-bots-dashboard/branch/coverage/)

# Instructions

## With executable

* Download executable
* Unzip
* Run main.exe or main.sh
* Browse to http://127.0.0.1:8050
* In the config tab add the accounts you want to monitor
  Tip for windows: to see the console log of the program run this via and command prompt

## With Docker

docker pull gamerbeaker/spl-bots-dashboard:latest

### Windows (docker):

<code>docker run --rm -it -v C:\Temp\:/app/store -p 8050:8050 --name spl-bots-dashboard
gamerbeaker/spl-bots-dashboard:latest</code>
For server mode
<code>docker run --rm -it -v C:\Temp\:/app/store -p 8050:8050 --name spl-bots-dashboard
gamerbeaker/spl-bots-dashboard:latest -s</code>

### Linux (docker):

<code>docker run --rm -it -v \tmp\:/app/store -p 8050:8050 --name spl-bots-dashboard
gamerbeaker/spl-bots-dashboard:latest</code>
For server mode
<code>docker run --rm -it -v \tmp\:/app/store -p 8050:8050 --name spl-bots-dashboard
gamerbeaker/spl-bots-dashboard:latest -s</code>

## With python development or local execution

Download sources and unpack.

Use python 3.8 or higher.
<code>pip install -r requirements.txt
python src/main.py</code>

When installing on a Windows machine and this error given:
<code>scrypt-1.2.1/libcperciva/crypto/crypto_aes.c(6): fatal error C1083: Cannot open include file: 'openssl/aes.h': No
such file or directory</code>
Then install [Win64 OpenSSL](https://slproweb.com/products/Win32OpenSSL.html) (not the light version)

# Result how to use

TODO
