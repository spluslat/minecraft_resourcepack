#!/bin/bash

file_name="custom_mecab"

/usr/lib/mecab/mecab-dict-index -d /usr/lib/x86_64-linux-gnu/mecab/dic/mecab-ipadic-neologd/ -u ${file_name}.dic -f utf-8 -t utf-8 ${file_name}.csv
