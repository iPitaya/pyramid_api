#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import math
import time

DEFAULT_FACTOR = {
    0:0.01,
    1:0.2,
    2:0.03,
    3:0.3,
    4:0.05,
    5:0.25,
    6:0.1,
    7:0.04,
    8:0.15,
    9:0.07
}

def collect_count(item_id, score, ts):
    _t = int(time.time())
    ts = abs((_t - ts +1)*10)
    try:
        item_id = int(item_id)
        _n = item_id%10
    except:
        _n = 8
    f = DEFAULT_FACTOR[_n] 

    if score:
        score = abs(int(score))
        if score == 0:
            score = f
    else:
        score = f

    _ts = ts/(1.0+_n*10)
    _f_sin = math.sin(f*10) *2
    n = math.log(ts*score)*math.log(ts*_ts)*(_f_sin+0.001 )+ score*(1 + f)
    return int(n)

def collect_count_new(item_id, score, ts):
    _t = int(time.time())
    ts = abs((_t - ts +1)*100)
    try:
        item_id = int(item_id)
        _n = item_id%10
    except:
        _n = 8
    f = DEFAULT_FACTOR[_n] 

    if score:
        score = abs(int(score))
        if score == 0:
            score = f
    else:
        score = f

    _ts = ts/(1.0+_n*10)
    _f_sin = math.sin(f*10) *27
    n = math.log(ts*score)*math.log(ts*_ts)*(_f_sin+0.001 ) + score*(1 + f)
    return int(n)


if __name__ == "__main__":
    print time.time()
    print collect_count_new(12344, 300, 1449664121.47-100000*3)
    pass

