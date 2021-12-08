# RadiruRadiru

NHKラジオのストリーミング放送(らじる★らじる)を予約録音するためのPythonスクリプト。
Plamoな環境でしか試してないけど、多分 at が使えるUNIX系の環境なら動くはず。

radiru_rec.py  : 録音用のシェルスクリプトを作成し、指定時刻に起動するように at に登録する。 
radiru_check.py : 登録済みの録音用スクリプトを表示する。
radiru_del.py : 登録した録音用スクリプトを削除する。
radiru_noa.py : 録音用スクリプトから実行され、現在放送中の番組情報を入手する。
radiru_tag.py : 録音終了後、番組情報を録音したファイルに書き込む。

requests と mutagen モジュールを使うので、pip install しておく必要あり。
