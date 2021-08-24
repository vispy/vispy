#!/bin/bash

for file in *.png
do
    echo "Converting $file"
    convert $file -thumbnail '200x200'^ -extent 200x200 thumbnails/`basename $file`;
done
