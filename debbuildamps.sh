#!/usr/bin/env bash
set -e
mkdir dist
cd ./cpp_amplifiers
fakeroot debian/rules binary
cd ..
mv *.deb dist/
