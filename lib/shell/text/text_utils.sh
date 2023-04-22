#!/bin/bash

# Prints text either colored or uncolored with a typewriter effect
function fn_typewriter() {
    if [ $# -gt 2 ]; then
        echo -e "Illegal number of args passed!"
        exit 1
    fi

    string=$1
    if [ $# -gt 1 ]; then
        for ((i = 0; i <= ${#string}; i++)); do
            printf "$2%b$RESET" "${string:$i:1}"
            sleep 0.$(((RANDOM % 2) + 1))
        done
    else
        for ((i = 0; i <= ${#string}; i++)); do
            printf "%s" "${string:$i:1}"
            sleep 0.$(((RANDOM % 2) + 1))
        done
    fi
}
