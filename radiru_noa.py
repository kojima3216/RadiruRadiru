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

import sqlite3, os, sys, json, requests

"""
NHKのNow On Air情報を提供しているサイト
(http://www2.nhk.or.jp/hensei/api/noa.cgi?c=3&wide=1&mode=jsonp)から，
指定したチャンネル(r1, r2, fm)で現在放送中の番組情報を入手して，
その結果をSQLite3のデータベースに書き込むスクリプト．
SQLite3の文字列はUTF-8が求められているので，
このスクリプトの文字コードも UTF-8 になっていることに注意．
"""

# global variables which show each directries
config_path = "~/.radiru_confs"
config = {'script_dir':'~/radiru_scripts', 'radiru_dir':'~/Radiru','DB_dir':'~/Radiru'}

def init():
    '''
    config_path を読んで，config{} を設定する．
    scriptdir = config['script_dir']
    musicdir = config['radiru_dir']
    '''
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


def init_db(dbname):
    '''
    録音した番組情報を記録するためのデータベースを初期化する．
    データベースは radiru_titles.sql3 というファイル名で，
    titlesとcontentsの2つのテーブルを持つ．
    titles は全てテキストフィールドで |filename|date|ch|title|act| という構造．
    1番組分を1行に収める．
    titles 行のoidをキー(id)にして，contentsは |id|list|という行が必要な数だけ並ぶ．
    '''
    conn = sqlite3.connect(dbname)
    conn.isolation_level = None
    cursor = conn.cursor()
    cursor.execute('''create table titles
       (filename text, date text, ch text, title text, act text)''')
    cursor.execute('''create table contents
       (id int, list text)''')
    return conn


def insert_title(cursor, t):
    try:
        # print("inserting ", t)
        cursor.execute('insert into titles values(?, ?, ?, ?, ?)', t)
    except sqlite3.Error :
        print("An error occurred:", e.args[0])

def insert_contents(cursor, t):
    try:
        # print("inserting ", )
        cursor.execute('insert into contents values(?, ?)', t)
    except sqlite3.Error as  e:
        print("An error occurred:{}".format(e.args[0]))

def get_json_data():
    '''
    NHKのNOA(Now On Air)から，json形式で現在放送中の番組情報を入手する．
    下記URLを叩くと，一番外側に nowonair(...) という形でデータが帰ってくるので，
    それらを剥ぎ取らないと正しくjson形式として処理できない．
    '''
    url = 'http://www2.nhk.or.jp/hensei/api/noa.cgi?c=1&wide=1&mode=jsonp'
    req = requests.get(url)
    data = json.loads(req.text.lstrip('nowonair(').rstrip(');'))
    return data

def main():
    init()
    dbdir = config['DB_dir']
    dbname = dbdir + '/radiru_titles.sql3'
    if os.access(dbname, os.R_OK) == False:
        connection = init_db(dbname)
        cursor = connection.cursor()
    else:
        connection = sqlite3.connect(dbname)
        cursor = connection.cursor()

    channel = sys.argv[1]
    filename = sys.argv[2]

    '''
    if channel == 'fm':
        ch = '001netfm0'
    elif channel == 'r1':
        ch = '001netr10'
    elif channel == 'r2':
        ch = '001netr20'
    else:
        print("{} is not a valid channel(fm, r1, r2)".format(channel))
        sys.exit(1)
    '''

    '''
    dt_tag は 001"channnel"0 が現在，001"channel"B1 が一つ前，001"channel"F1 が次の番組を示す
    'music'の場合，各曲は＜BR＞で区切られている．
    '''
    data   = get_json_data()
    dt_tag = '001' + channel + '0'
    title  = data[dt_tag]['title']
    act    = data[dt_tag]['act']
    date   = data[dt_tag]['starttime']

    # print("title:{}, act:{}, date:{}, music:{}".format(title, act, date, music))
    
    insert_title(cursor, (filename, date, channel, title, act))
    connection.commit()
    # print(cursor.lastrowid)
    did = cursor.lastrowid

    '''
    DBの contents には，'music' > 'content' > 'subtitle' の順でデータを拾う．
    music  = data[dt_tag]['music'].replace("＜BR＞", "\n")
    '''
    if len(data[dt_tag]['music']) > 2:
        txt = data[dt_tag]['music'].replace('＜BR＞','\n')
        # print("music exist")
    elif len(data[dt_tag]['content']) > 2:
        txt = data[dt_tag]['content']
        #  print("content exist")
    elif len(data[dt_tag]['subtitle']) > 2:
        txt = data[dt_tag]['subtitle']
        # print("subtitle exist")
    else :
        txt = data[dt_tag]['act']
        # print("use act")
              
    # print("txt:{}".format(txt))
    
    insert_contents(cursor, (did, txt))
    connection.commit()
              
'''
    for i in cols:
        tmp = i.replace('\\n', '\n')
        insert_contents(cursor, (did, tmp))
        # print("list:{}".format(tmp))
        connection.commit()
        # print(cursor.lastrowid)
'''

if __name__ == "__main__":
    main()
