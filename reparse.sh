#!/bin/bash

for i in laws_ashx/*.xml
do
    ./parse.py $i laws_xml/$(basename $i)
done
