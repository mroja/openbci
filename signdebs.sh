#!/usr/bin/env bash
set -e

# GPG_KEY - enviroment variable - private key in base64
echo "$GPG_KEY" | base64 -d | gpg --allow-secret-key-import --import -
cd dist

#debsigs --sign=origin openbci-amplifiers*.deb
#debsigs --sign=origin openbci-dummy-amplifier*.deb
#debsigs --sign=origin openbci-file-amplifier*.deb
#debsigs --sign=origin openbci-tmsi-amplifier*.deb
debsigs --sign=origin python3-obci*.deb
debsigs --sign=origin obci2_*.deb

