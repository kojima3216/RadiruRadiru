#! /usr/bin/python
# -*- coding: utf-8 -*-;

'''
Copyright(C) 2021 KOJIMA Mitsuhiro
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

import argparse, sys, os, re
import datetime
from datetime import timedelta
from time import strptime

# global variables which show each directries
config_path = "~/.radiru_confs"

config = {'script_dir':'~/radiru_scripts', 'radiru_dir':'~/Radiru','DB_dir':'~/Radiru'}

def read_configs(path):
    global config
    if os.path.isfile(path):
        f = open(path,'r')
        lines = f.readlines()
        for i in lines:
            (it, dt) = i.rstrip().split(':')
            config[it] = dt
    for key in config:
        config[key] = os.path.expanduser(config[key])

def init():
    '''
    設定ファイル(~/.radiru_confs)を読んで，script_dir, radiru_dir, DB_dir の位置を
    config{}に収める．指定されたディレクトリが無い場合は新しく作る．
    '''
    conf_path = os.path.expanduser(config_path)
    print(conf_path)
    read_configs(conf_path)
    scriptdir = config['script_dir']
    musicdir = config['radiru_dir']

    if os.access(scriptdir, os.W_OK) != True:
        os.makedirs(scriptdir)

    #if os.access(fifodir, os.W_OK) != True:
    #    os.makedirs(fifodir)

    if os.access(musicdir, os.W_OK) != True:
        os.makedirs(musicdir)


def get_args():
    parser = argparse.ArgumentParser(description='radiru_radiru record scripts builder')
    parser.add_argument('-d','--daily', action='store_true', help='repeat r times(set by -r option) by daily')
    parser.add_argument('-w','--weekly', action='store_true', help='repeat r times(set by -r option) by weekly')
    parser.add_argument('-t', '--title', help='set program title. If not indicated, channel name(fm, r1, r2) is used as program title')
    parser.add_argument('-n', '--number', help='add sequential numbers to program title, such as myprogram_1, myprogram_2,, . ')
    parser.add_argument('-r', '--repeat', help='repeat R times by daily or weekly')
    parser.add_argument('rec_data', nargs='*', help='(such as) "fm 8/23 12:00 14:00"  Style is "channel(fm|r1|r2) [begin_date] begin_time [end_date] end_time|recording_time". Begin_date should be month/date format(8/31). If you ignore begin_date, it interpreted as today. You can use recording_time(such as 1h30m) instead of end_time')
    args = parser.parse_args()
    return args

def usage():
    print("NHKのネットラジオ「らじる☆らじる」を録音するためのスクリプトを作成するスクリプト")
    print("    {0} [-d|-w] [-r R] [-n N] [-t Title] channel [begin_date] begin_time [end_date] end_time|recording_time".format(sys.argv[0]))
    print("")
    print("    channelはfm|r1|r2， begin_date, end_date は 月/日の形式で，省略すれば今日．begin_time, end_timeは24時間制で，深夜番組向けに26:00くらいまでは指定可能．end_timeの代りに録音時間を2h30mのように直接指定することも可能")
    print("")
    print("    -d|-wは-rと組み合わせて繰り返し形式を指定する．-dは日毎の繰り返し，-wは週毎の繰り返し．-rで繰り返しの回数を指定する．-w -r4とすれば，4週間に渡って，同じ曜日に同じチャンネル，同じ時刻に録音するスクリプトを生成する")
    print("    -n は繰り返し録音時にタイトルに連番を付けたい際に用いる．")
    print("")
    print("    例： {0} -d -r 5 -n 10 -t myprogram fm 8/23 10:00 30m".format(sys.argv[0]))
    print("       8/23,24,25,26,27の5日間，それぞれ10:00 から30分間，NHK FMの番組を録音するためのスクリプトを生成する．録音したファイルには 2012-08-23-10-00_myprogram_10.mp3, 2012-08-24-10-00_myprogram_11.mp3,, のようなファイル名が付く")
    print("")
    print("        {0} -w -r 5 -n 10 -t program r2 8/23 10:00 30m の場合は，".format(sys.argv[0]) )
    print("        8/23,30,9/6,13,20の5週に渡って，それぞれ10:00から30分間，ラジオ第二の番組を録音するためのスクリプトを生成する．")

def norm_date(dt_str):
    """日付の文字列がMM/DDの場合，YY-MM-DDにして返す"""
    res = re.match('[0-9]+/[0-9]+/[0-9]+', dt_str)
    if res == None: # MM/DD format
        year = datetime.datetime.today().strftime("%Y")
        (month, day) = dt_str.split('/')
    else:  # YY/MM/DD format
        (year, month, day) = dt_str.split("/")

    date_str = year + "-" + month + "-" + day
    # print "dt_str:", dt_str
    return date_str

def norm_time(date_str, time_str):
    """日付と時刻の文字列を標準化する．
    もし時刻が24:00以降の場合，時刻を-24してからdateオブジェクトを作った
    上でtimedeltaを1日加える(dateオブジェクトはhour<24が必要のため)
    せいぜい26:00くらいまでしか使わない前提なので，48:00 以上の指定は不可"""
    (str_year, str_month, str_day) = date_str.split("-")
    year = int(str_year)
    month = int(str_month)
    day = int(str_day)

    (str_hour, str_minute) = time_str.split(":")
    hour = int(str_hour)
    minute = int(str_minute)
    day_over = 0
    if hour >= 24:
        hour = hour - 24
        day_over = 1

    date_obj = datetime.datetime(year, month, day, hour, minute)
    if day_over == 1:
        date_obj = date_obj + datetime.timedelta(days=1)

    return date_obj

def norm_duration(d):
    """録画時間の指定を分単位に換算する"""
    t = d.lower()
    if t.find('h') > 0:  # ex: 1h30m
        (h, m) = t.split('h')
        # print "h:",h, "m:",m
        mm = m.rstrip('m')
        if mm != '':
            duration = int(h)*60 + int(mm)
        else:
            duration = int(h)*60
    else:
        mm = t.rstrip('m')
        duration = int(mm)
    return duration

def parse_parms(rec_data):
    """位置引数として与えられた引数をパースする．
    引数の順番は"チャンネル" "開始時刻" {"終了時刻" | "録音時間" } の順． 
    開始時刻，終了時刻ともに日付の指定が無ければ「今日」．
    時刻指定は，慣例的な 25:00 みたいな指定も可能．
    録音時間は 90m か 1h30m の形．h か m が無いとエラーになる"""
    dc = len(rec_data)
    if dc < 3 or dc > 5:
        print("エラー！ 録音設定に必要な情報が足りません")
        print("入力データ:{0}".format(rec_data))
        usage()
        sys.exit(1)

    channel = rec_data.pop(0)
    start_flag = 0
    duration = 0
    while len(rec_data) > 0:
        if (start_flag == 0):
            i = rec_data.pop(0)
            if re.match('[0-9]+/[0-9]+', i): # date part
                begin_date_str = norm_date(i)
                i = rec_data.pop(0)
                begin_time_str = i
            else:
                begin_date_str = datetime.datetime.today().strftime("%Y-%m-%d")
                begin_time_str = i
            start_flag = 1
            begin = norm_time(begin_date_str, begin_time_str)

        else:
            i = rec_data.pop(0)
            if re.match('[0-9]+/[0-9]+', i): # date part
                end_date_str = norm_date(i)
                i = rec_data.pop(0)
                end_time_str = i
            elif re.search('[HhMm]', i) != None:
                duration = norm_duration(i)
                end_date_str = 'none'
                end_time_str = 'none'
            else:                    
                end_date_str = begin_date_str
                end_time_str = i

            if duration == 0:
                end = norm_time(end_date_str, end_time_str)

    if duration == 0:
        interval = end - begin
        duration = interval.days*24*60 + interval.seconds/60 + 1

    return(channel, begin, duration)

def get_serial():
    scriptdir = config['script_dir']
    serial_data = scriptdir + "/serial"

    try:
        fp = open(serial_data, 'r')
    except IOError:
        serial = 0
    else:
        tmp = fp.read()
        serial = int(tmp)
        fp.close()

    new_serial = str(serial +1)
    fp = open(serial_data, 'w')
    tmp = str(new_serial)
    fp.write(tmp)
    fp.close()

    return serial


def make_script(channel, duration, title):
    """録音用のシェルスクリプトを作る．
    シェルスクリプトの置き場は config['script_dir'](デフォルト ~/radiru_scripts/) で，
    録音データの置き場は config['radiru_dir'](デフォルト ~/Radiru/)を想定(~/.radiru_confs で変更可)．
    config['script_dir']/serial に最後に作成したスクリプトの番号が記録されるので、
    それに +1 したものがスクリプトのファイル名になる。
    作成したスクリプトを register_script() でatコマンドに登録する．"""
    scriptdir = config['script_dir']
    musicdir = config['radiru_dir']
    sduration = duration * 60 + 30   # delay があるので30秒追加
    my_id = get_serial()
    # print("scriptdir:{0},musicdir:{1}".format(scriptdir,musicdir))
    if channel == 'r1':
        url = 'https://radio-stream.nhk.jp/hls/live/2023508/nhkradirubkr1/master.m3u8'
    elif channel == 'r2':
        url = 'https://radio-stream.nhk.jp/hls/live/2023501/nhkradiruakr2/master.m3u8'
    elif channel == 'fm':
        url = 'https://radio-stream.nhk.jp/hls/live/2023509/nhkradirubkfm/master.m3u8'
    else:
        print("channel set error:{0}".format(channel))
        usage()
        sys.exit(1)

    if os.access(scriptdir, os.R_OK) == False:
        print("{0} not writable.".format(scriptdir))
        sys.exit(1)
    
    scriptname = scriptdir + "/" + str(my_id)
    f = open(scriptname, "w")

    '''
    録音用スクリプトは，開始後1分待ってから radiru_noa.py を使って現在，
    そのチャンネルで放送している
    番組情報を取り込み，radiru_titles.sql3 データベースに記録する．
    指定された録音時間 + 1m 後，radiru_id3.py を使って，データベースに記録した
    情報をm4aファイルのID3タグに書き込む
    '''
    lines = []
    lines.append('#!/bin/sh')
    lines.append('sleep 30')
    lines.append('m4afile={0}/{1}.m4a'.format(musicdir, title))

    lines.append('( ffmpeg -loglevel fatal -i {0} -t {1} -movflags faststart -c copy -bsf:a aac_adtstoasc  $m4afile ) 1>&2 &'.format(url, sduration))

    lines.append("sleep 60s")
    lines.append("radiru_noa.py {0} {1}.m4a".format(channel,title))
    lines.append("sleep {}s".format(sduration))
    lines.append("radiru_tag.py {0}/{1}.m4a".format(musicdir,title))
    lines.append("rm -f {}\n".format(scriptname))
    script = "\n".join(lines)

    f.write(script)
    f.close

    return(scriptname)


def register_script(script, begin):
    begin_str = begin.strftime("%H:%M %m/%d/%Y")
    os.environ.pop('TIME_STYLE', None)
    cmd = "at {0} -f {1}".format(begin_str, script)
    # print(cmd)
    result = os.system(cmd)
    return result

def main():
    init()
    params = get_args()
    (channel, begin, duration) = parse_parms(params.rec_data)
    if params.title == None:
        title = channel
    else:
        title = params.title

    if params.number != None:
        number = int(params.number)
        if number < 10:
            title = title + '_00' + params.number
        elif number < 100:
            title = title + '_0' + params.number
        else:
            title = title + '_' + params.number

    if duration < 0:
        print("エラー! 録音時間がマイナスになっています")
        sys.exit(1)
    elif duration < 5:
        print("警告．録音時間が5分以下です")
    elif duration > 180:
        print("警告．録音時間が3時間以上です")

    
    now = datetime.datetime.today()
    if begin < now :
        print("エラー! 開始時刻はすでに過ぎています")
        print("{0},{1}, {2},{3}".format(title, channel, begin, duration))
    else:
        print("{0},{1}, {2},{3}".format(title, channel, begin, duration))
        rec_title = begin.strftime("%F-%H-%M") + "_" + title
        scriptname = make_script(channel, duration, rec_title)
        result = register_script(scriptname, begin)

        if result != 0 :
            print("エラー! 録音用スクリプトが登録できませんでした．")
            sys.exit(1)

    if params.repeat != None:
        repeat = int(params.repeat) - 1

        while repeat > 0:
            if params.number != None:
                number = number + 1
                if number < 10:
                    title = params.title + '_00' + str(number)
                elif number < 100:
                    title = params.title + '_0' + str(number)
                else:
                    title = params.title + '_' + str(number)
        
            if params.daily == True and  params.weekly == True:
                print("エラー! -d は -w と同時に指定できません.")
                sys.exit(1)

            if params.weekly == True :
                interval = 7
            else:
                interval = 1

            begin = begin + datetime.timedelta(days=interval)
            if begin < now :
                print("エラー! 開始時刻はすでに過ぎています: {0},{1}, {2},{3}".format(title, channel, begin, duration))
            else:
                print("{0},{1}, {2},{3}".format(title, channel, begin, duration))
                rec_title = begin.strftime("%F-%H-%M") + "_" + title
                scriptname = make_script(channel, duration, rec_title)
                result = register_script(scriptname, begin)

                if result != 0:
                    print("エラー! 録音用スクリプトが登録できませんでした")

            repeat = repeat - 1
    
if __name__ == "__main__":
    main()
