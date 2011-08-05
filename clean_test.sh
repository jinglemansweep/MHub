#!/bin/bash

rm -rf build dist
python setup.py install && bin/mhub-server -v
