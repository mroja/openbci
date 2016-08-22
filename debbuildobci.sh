#!/usr/bin/env bash
set -e
mkdir dist
python3.5 setup.py --command-packages=stdeb.command bdist_deb
mv ./deb_dist/*.deb ./dist/
sed "s/GIT_VERSION/$(git describe --tags)/g" obci2all.template > dist/obci2all
cd dist
equivs-build obci2all

