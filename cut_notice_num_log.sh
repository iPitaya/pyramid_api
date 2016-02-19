#!/bin/sh
#this shell for cut /data/log/api2/notic_num.log everyday
need_cut_file=/data/log/api2/notic_num.log
lastday=`date +%Y-%m-%d -d "-1 days"`
shellpath=/home/api2/hichao_backend
cd ${shellpath}
mv ${need_cut_file} /data/log/api2/${lastday}_notic_num.log
/bin/sh ${shellpath}/notic_stop.sh
sleep 1
/bin/sh ${shellpath}/notic_start.sh
gzip /data/log/api2/${lastday}_notic_num.log
