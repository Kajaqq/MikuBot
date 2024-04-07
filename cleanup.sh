#!/bin/bash
# This file fixes a weird issue with snap version of chromium when the cache isn't ever deleted and takes up large amount of spaces fast.
# Add it to your cronfile or make it run every few hours or so otherwise you will have 100+GB of cache pretty fast
log_dir=$(realpath $(dirname $0))
sudo rm -rf /tmp/snap-private-tmp/snap.chromium/tmp/.org.chromium.Chromium.* \;
sudo find $script_dir/media/csv/ -name 'cache.txt' -type f -mtime 5 -exec rm -f {} +c \;
sudo find $script_dir/media/csv/ -name 'output.csv' -type f -mtime 5 -exec rm -f {} +c \;
