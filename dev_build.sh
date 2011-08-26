#!/bin/bash

echo "Cleaning..."
rm build dist -rf
rm twisted/plugins/*.cache
find . -name "*.pyc" -exec rm -rf {} \;

echo "Building..."
python setup.py install
