#!/bin/bash

# Builds confs files with the proper parameters as specified on commandline

if [ $# -gt 1 ] ; then
    1>&2 echo "Usage ./build.sh [tag]"
    exit 1
fi

echo "#################################################################"
echo "########## Starting building catalogue ##########################"
echo "#################################################################"
echo

echo_prop() {
    if [ -z "$1" ]; then
        echo "$2"
    else
        echo "$1"
    fi
}

echo "Running at: "
echo "$(pwd)"

cd ..
tagGit="$(git describe --tags $(git rev-list --tags --max-count=1))"
tag="Test"

if [ $# -eq 0 ] ; then
    echo "Please introduce the version to put in the image [ENTER] (default=$tag)"
    read tagReaded
    echo "############################"
    echo
else
    tagReaded="$1"
fi

tag=$(echo_prop $tagReaded $tag)

if [ "$tag" = "Test" ] && grep -i "DEBUG_RUN=False" docker/.env >/dev/null ; then
    echo -n "Using Test tag on production environment. Continue anyway? (y/N) "
    read cont
    cont=$(echo "$cont" | tr 'A-Z' 'a-z')
    if [ "$cont" = "n" ] || ! [ "$cont" = "y" ] ; then
        exit 0
    fi
fi

tagDate=$(git log -1 --format=%aD $tagGit)

cp requirements.txt docker/requirements.txt
cd docker

if grep -i "TEST_MODE=True" .env >/dev/null ; then
    target="tests"
    cp ../requirements-dev.in requirements-dev.in  # we have to cp this file because for the tests target, the dev target will also be built
    cp ../tests/units/requirements.txt requirements-tests.txt
elif grep -i "DEBUG_RUN=True" .env >/dev/null ; then
    target="dev"
    cp ../requirements-dev.in requirements-dev.in
else
    target="prod"
fi

echo "Creating the container... tag:$tag target:$target"
docker build --rm=true -t bioinformaticsua/catalogue:$tag --target $target .


echo "Configure docker-compose image version..."
sed -i '/image: bioinformaticsua/c\    image: bioinformaticsua/catalogue:'$tag docker-compose.yml
sed -i '/MONTRA_VERSION=/c\MONTRA_VERSION='$tag .env
sed -i '/MONTRA_VERSION_DATE=/c\MONTRA_VERSION_DATE='"$tagDate" .env

rm -f requirements.txt requirements-dev.in requirements-tests.txt

echo "###########################################"
echo " Build Complete"
echo "###########################################"


