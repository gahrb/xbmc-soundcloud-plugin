#!/bin/bash

dest=plugin.audio.soundcloud
version=`grep "^\s\+version" addon.xml | cut -f2 -d'"'`

if [ -d $dest ]; then
    rm -r $dest
fi

mkdir $dest
cp addon.xml $dest/
cp LICENSE.txt $dest/
cp changelog.txt $dest/
cp icon.png $dest/
cp *.py $dest/
cp -r resources $dest/
cp -r httplib2 $dest/
cp -r xbmcsc $dest/

if [ -f $dest-$version.zip ]; then
    rm $dest-$version.zip
fi

zip -r $dest-$version.zip $dest
rm -r $dest
