#!/bin/bash

./dev_reset.sh
./dev_build.sh

echo "Launching..."
twistd -n mhub -s