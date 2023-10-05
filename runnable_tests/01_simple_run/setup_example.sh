#!/bin/bash

mkdir data/

cd data || exit 1

masses=("0.5" "0.6" "1" "2")
indices=("0" "1" "2" "3")


for i in "${indices[@]}"; do
    python3 ../generate_data.py "${masses[$i]}" "data-$i.npy"
done
