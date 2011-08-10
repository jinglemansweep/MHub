#!/bin/bash

echo "Removing 'build' and 'dist' directories..."
rm -rf build
rm -rf dist

echo "Removing compiled Python objects..."
find . -name "*.pyc" -exec rm '{}' ';'

echo "Removing log files..."
rm -f twistd.log
rm -f twistd.pid

echo "Building project..."
python setup.py install

echo "Done."
