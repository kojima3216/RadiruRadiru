#! /usr/bin/python
# -*- coding: utf-8 -*-;

'''
Copyright(C) 2014 KOJIMA Mitsuhiro

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
'''

import sys, os, subprocess, argparse
from datetime import datetime, date,time

# global variables which show each directries
config_path = "~/.radiru_confs"
config = {'script_dir':'~/radiru_scripts', 'radiru_dir':'~/Radiru','DB_dir':'~/Radiru'}

def init():
    global config
    conf_path = os.path.expanduser(config_path)
    if os.path.isfile(conf_path):
        f = open(conf_path,'r')
        lines = f.readlines()
        for i in lines:
            (it, dt) = i.rstrip().split(':')
            config[it] = dt
    for key in config:
        config[key] = os.path.expanduser(config[key])

    '''
    scriptdir = config['script_dir']
    musicdir = config['radiru_dir']
    '''
def get_args():
    parser = argparse.ArgumentParser(description='radiru_radiru registered data checker')
    parser.add_argument('-t','--title', action='store_true', help='sorted by title')
    parser.add_argument('-d','--date', action='store_true', help='sored by rec date')
    parser.add_argument('-q', '--qid', action='store_true', help='sored by queue id')
    args = parser.parse_args()
    return args

def list_atque():
    res = subprocess.check_output(['atq'])
    return res

def check_que(id):
    # print("check_que id:{}".format(id))
    check_id = str(id)
    res = subprocess.check_output(['at', '-c', check_id])
    # print("in check_que: {}".format(res))
    str_res = res.decode('utf-8')
    # print("str_res: {}".format(str_res))
    res_list = str_res.splitlines()
    title = ''
    radiru_chk = 0
    for i in res_list:
        # print("i={}".format(i))
        if i.find("m4afile=") == 0:
            # print("find m4afile:{}".format(i))
            title = get_title(i)
        elif i.find("radio-stream.nhk.jp") > 0:
            # print("i={}".format(i))
            '''
            ffmpeg -i https://radio-stream.nhk.jp/hls/live/2023501/nhkradiruakr2/master.m3u8 -t 900 -movflags faststart -c copy -bsf:a aac_adtstoasc  $m4afile 
            '''
            cmd_line = i.split()
            url = cmd_line[3]
            period = cmd_line[5]
            
            if url.find('kr1') > 0 :
                channel = 'r1'
            elif url.find('kr2') > 0:
                channel = 'r2'
            else :
                channel = 'fm'

    return (channel, title, period)


def get_title(line):
    (tmp, path) = line.split('=')
    base = os.path.basename(path)
    # chk = base.split('`date ')
    # titles = chk[1].partition('_') 
    return base

def main():
    init()
    mon = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}
    j_wday = {'Sun':'日', 'Mon':'月', 'Tue':'火', 'Wed':'水', 'Thu':'木', 'Fri':'金', 'Sat':'土'}

    params = get_args()
    # print params
    # sys.exit()

    res_str = list_atque()
    # print("res_str:{}".format(res_str))
    que_list = res_str.decode('utf-8').splitlines()
    date_que = {}
    rec_que = []
    # id_que = {}
    for i in que_list:
        # print("i = {}".format(i))
        (qid, wday, mon_n, mday, begin_time, year, que, user) = i.split()
        # print("rec data:{} {} ".format(qid, begin_time))
        (channel, title, period) = check_que(qid)
        try:
            # print(int(qid))
            (channel, title, period) = check_que(qid)
            # print("cannel:{} title:{} period:{}".format(channel, title, period))
            (hr,min,sec) = begin_time.split(":")
            rec_start = datetime(int(year), mon[mon_n], int(mday), int(hr), int(min), 0)
            rec_que.append((rec_start, int(qid), channel, title, mon[mon_n], mday, j_wday[wday], begin_time, period))
        except TypeError:
            # pass
            print("try Error")
        
    if params.qid == True:
        sorted_que = sorted(rec_que, key=lambda rec_que: rec_que[1])
        for i in sorted_que:
            (rec_start, qid, channel, title, mon[mon_n], mday, j_wday[wday], begin_time, period) = i
            begin_date = rec_start.strftime("%Y-%m-%d(%a) %H:%M")
            print("{qid} {rec_date} {p} {ch} {ti} ".format(qid=qid, rec_date=begin_date, ch=channel, ti=title, p=period))
            
    elif params.title == True:
        sorted_que = sorted(rec_que, key=lambda rec_que: rec_que[3])
        for i in sorted_que:
            (rec_start, qid, channel, title, mon[mon_n], mday, j_wday[wday], begin_time, period) = i
            begin_date = rec_start.strftime("%Y-%m-%d(%a) %H:%M")
            print("{ti} {qid} {rec_date} {p} {ch} ".format(qid=qid, rec_date=begin_date, ch=channel, ti=title, p=period))
        
    else:
        sorted_que = sorted(rec_que, key=lambda rec_que: rec_que[0])
        for i in sorted_que:
            (rec_start, qid, channel, title, mon[mon_n], mday, j_wday[wday], begin_time, period) = i
            begin_date = rec_start.strftime("%Y-%m-%d(%a) %H:%M")
            print("{rec_date} {p} {qid} {ch} {ti} ".format(qid=qid, rec_date=begin_date, ch=channel, ti=title, p=period))

if __name__ == "__main__":
    main()

