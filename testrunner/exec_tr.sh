#!/bin/bash
solution=$1
testcase=$2
t_result=$3


mkdir tmp
cp $solution tmp
cp $testcase tmp
cd tmp
touch __init__.py
python -m unittest -v $testcase > test_results
status=$?
mv test_results $t_result/test_results
cd ..
rm -r tmp
exit $status