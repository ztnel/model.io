#!/bin/bash

OKG="\033[92m"
WARN="\033[93m"
FAIL="\033[91m"
OKB="\033[94m"
UDL="\033[4m"
NC="\033[0m"

VERSION=""

while getopts ":hr:" opt; do
    case "$opt" in
        h )
            echo "Usage:"
            echo "      build.sh -h                         Display this message"
            echo "      build.sh -r {{ github.ref }}        Build dist from github publish ref"
            exit 0;
            ;;
        r )
            VERSION=$(echo "$OPTARG" | awk -F '/' '{print $3}' | cut -c2-)
            ;;
        \? )
            echo "Invalid option: $OPTARG" 1>&2
            exit 1;
            ;;
        : )
            echo "Invalid option: $OPTARG requires an argument" 1>&2
            exit 1;
            ;;
    esac
done

shift $((OPTIND -1))

if [ -z "$VERSION" ]; then
    echo 'Missing github publish ref' >&2
    exit 1
fi


# build package
printf "%b" "${OKB}Building package distribution for version: $VERSION${NC}\n"
python setup.py sdist bdist_wheel
printf "%b" "${OKG} ✓ ${NC}complete\n"