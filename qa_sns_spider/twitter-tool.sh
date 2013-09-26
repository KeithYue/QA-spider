#! /bin/bash

echo "$1"
tweet_dir=./data/tweets/
follows_dir=./data/twitter-follow/

echo ${follows_dir}${1}

twitter-archiver -o "$1" -s "$tweet_dir"
twitter-follow -o -i -g "$1" > ${follows_dir}${1}
