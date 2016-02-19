SECTION="uwsgi"
KEY="pidfile"
INI=""

if [ $# -eq 0 ]; then
    INI="production.ini"
else
    INI=$1
fi

PIDFILE=`cat $INI | awk 'BEGIN {FS="=";OFS=":";} /\['$SECTION'\]/,/\[.*[^('$SECTION')].*\]/{gsub(/[[:blank:]]*/,"",$1);if(NF==2 && $1=="'$KEY'"){gsub(/^[[:blank:]]*/,"",$2);gsub(/[[:blank:]]*$/,"",$2);print $2;}}'`

kill -9 `cat $PIDFILE`

