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

import sqlite3, os, sys
from mutagen.mp4 import MP4

# global variables which show each directries
config_path = "~/.radiru_confs"
config = {'script_dir':'~/radiru_scripts', 'radiru_dir':'~/Radiru','DB_dir':'~/Radiru'}

'''
録音したm4aファイルのファイル名を引数として与えると，
番組情報データベース(radiru_titles.sql3)を引いて，
番組のタイトルや出演者，曲名リストを取り出し，m4aファイルのID3タグに書き込むスクリプト．
システム側で pip install eyed3 しておく必要あり．
'''

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

def query_db(query):
    # print('query:{}'.format(query))
    dbdir = config['DB_dir']
    dbname = dbdir + '/radiru_titles.sql3'
    if os.access(dbname, os.R_OK) == False:
        print("cannot find title DB({})".format(dbname))
        sys.exit(1)

    connection = sqlite3.connect(dbname)
    # connection.isolation_level = None
    cursor = connection.cursor()
    c = cursor.execute(query)
    res = c.fetchall()
    if len(res) == 0:
        print("this query didn't get results.: {} ".format(query))
        print("please check title DB:{}".format(dbname))
        sys.exit(1)
    else:
        return(res)

'''
def query_titles(q):
    # print isinstance(q, int)
    if isinstance(q, int) == True:
        query = u"select oid,title,date,act from titles where oid='{}';".format(q)
    else:
        query = u"select oid,filename,date,ch,title,act from titles where filename='{}';".format(q)

    # print("query:{}".format(query.encode('euc-jp')))
    return(query_db(query))
'''
def query_contents(oid):
    # select oid,* from titles where filename='{}'
    query = u"select * from contents where id={}".format(oid)
    # print("query:{}".format(query))
    t = query_db(query)
    return t

def set_tag(file, tag):
    audio_file = MP4(file)
    # print("file:{} tag:{}".format(file, tag))

    for i in tag :
        audio_file[i] = tag[i]

    # audio_file.pprint()
    audio_file.save()

def main():
    init()
    filepath = sys.argv[1]
    file = os.path.basename(filepath)

    query = u"select oid,title,date,ch,act from titles where filename='{}';".format(file)
    (oid, title, date, channel, act) = query_db(query)[0]
    # print("oid:{}, date:{}, title:{}, channel:{}, act:{}".format(oid, date, title, channel, act))
    '''
    titlesテーブルのoidをcontentsテーブルのidとして使っている
    contentsは一つのidに複数の内容(曲名等)が結びついている．
    '''
    res = query_contents(oid)
    contents = ''
    for i in res:
        (id, l) = i
        contents = contents + l

    album = file.rstrip('.m4a')
    '''
    print("title:{}".format(title))
    print("album:{}".format(album))
    print("act:{}".format(act))
    print("date:{}, channel:{}".format(date, channel))
    print("contents:{}".format(contents))
    '''
    tag = {'\xa9nam':title, '\xa9alb':album, '\xa9ART':act, '\xa9day':date, 'ch':channel, '\xa9cmt':contents}
    # print("tag:{}".format(tag))
    set_tag(filepath, tag)

if __name__ == "__main__":
    main()

