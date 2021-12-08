#!/usr/bin/python
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

import sys, os, subprocess

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
            print(config)
    for key in config:
        config[key] = os.path.expanduser(config[key])

    '''
    scriptdir = config['script_dir']
    musicdir = config['radiru_dir']
    '''

def usage():
    print("Usage:")
    print(" {0} delete_qid1 [delete_qid2 ...]".format(sys.argv[0]))
    print("   指定したIDのジョブをatコマンドのキューから削除すると共に，不要になった録音用スクリプトを削除する")
    print("   IDは複数個指定可能")
    sys.exit()

def get_script(id):
    res = subprocess.check_output(['at', '-c', id])
    res_list = res.decode('utf-8').splitlines()
    for i in res_list:
        if i.find("rm -f") == 0:
            cmd_list = i.split(" ")
            num = cmd_list[-1].split("/")
            print("que_num:{}".format(num))
            return num[-1]
    print("cannot find script at que_id:{}".format(id))
    sys.exit(1)

def remove_que(id, script):
    scriptdir = config['script_dir']
    scriptname = scriptdir + "/" + str(script)
    print("delete que_id:{0} filename:{1}".format(id, scriptname))
    res = subprocess.check_call(['atrm', id])
    os.remove(scriptname)

def main():
    if len(sys.argv) < 2:
        usage()

    init()
    for i in sys.argv[1:]:
        script = get_script(i)
        print("script:{0}".format(script))
        remove_que(i, script)

if __name__ == "__main__":
    main()
