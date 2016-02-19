uwsgi_restart_command="/home/api2/env/bin/uwsgi -s:9989 --listen 20480 --harakiri 1 -M --ini-paste /home/api2/hichao_backend/production.ini -d /data/log/api2/log.log --stats 0.0.0.0:1718"

start_uwsgi () {
    echo "restart uwsgi."
    `$uwsgi_restart_command`
    return $?
}

kill_process () {
    _arr=($1)
    for _pid in ${_arr[*]}
    do
        echo "kill -9 $_pid"
    done
    return $?
}

reload_uwsgi () {
    echo "need forcely to restart uwsgi."
    _arr=($@)
    for _pid in ${_arr[*]}
    do
        #echo $_pid
        `kill -9 $_pid`
    done
    start_uwsgi
    return $?
}

assert () {
    if $1 != $2
    then
        echo "assert failed."
    fi
}

main () {
    if [ "$1" = "" ]
    then
        parent=`ps -ef | grep uwsgi | awk '((/9989/)&&(/api2/)&&($3==/1/)){print $2}'`
    else
        parent=$@
    fi
    if [ "$parent" = "" ]
    then
        reload_uwsgi "${parr[@]}"
    else
        parr=($parent)
        parr_len=${#parr[@]}
        if [ $parr_len = 1 ]
        then
            child=`ps -ef | grep uwsgi | awk '((/9989/)&&(/api2/)&&($3=='$parent')){print $2}'`
            arr=($child)
            arr_len=${#arr[@]}
            if [ $arr_len == 64 ]
            then
                echo "uwsgi is working well after log split."
            else
                reload_uwsgi "${parr[@]}" "${arr[@]}"
            fi
        else
            reload_uwsgi "${parr[@]}" "${arr[@]}"
        fi
    fi
}

#test data
pdata="1 2"
main
