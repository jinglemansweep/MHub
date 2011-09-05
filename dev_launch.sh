#!/bin/bash

./dev_reset.sh
./dev_build.sh

echo "Launching..."
#twistd -l mhub.log -n mhub -s
twistd -n mhub -s
