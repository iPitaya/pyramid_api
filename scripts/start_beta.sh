uwsgi_start_comment="/home/api2/env/bin/uwsgi --ini-paste "

if [ $# -eq 0 ]; then
    INI="beta.ini"
else
    INI=$1
fi

$uwsgi_start_comment $INI

