#!/bin/sh

find data -wholename 'data/20*PROPERTIES.xml' -print | while read i
# outputs like "data/20110113-054102/PROPERTIES.xml"
do
    data_dir=`dirname $i`
    datestamp=`basename $data_dir`
    #echo $datestamp
    cp $i data/output_aggregates/properties-$datestamp.xml
done
