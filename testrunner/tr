#!/bin/bash

solution=$1
testdir=$2
testfile=$3
resdir=$4
resfile=$5


mkdir tmp
cp $solution tmp
cp $testdir/$testfile tmp
cd tmp
touch __init__.py
python3 -m unittest -v $testfile > $resfile 1>&1 2>&1
status=$?
mv test_results ../$resdir/$resfile
cd ..
rm -r tmp
exit $status