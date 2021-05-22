# competition-manager

link to
- [Organizers](https://github.com/opusymcomp/competition-manager#Organizers)
- [Participants](https://github.com/opusymcomp/competition-manager#Participants)

# Organizers
## Requirement
- OS
  - Ubuntu 16 or 18
- tool
  - [rcssserver](https://github.com/rcsoccersim/rcssserver)
  - [loganalyzer3](https://github.com/opusymcomp/loganalyzer3)
  - [tournamnet](https://github.com/rcsoccersim/tournament)
- library
  - Python3
  - NumPy
  - slackbot
  - gspread
  - oauth2client
  - pyyaml
  - ruby2

## Install
```
$ git clone http://github.com/opusymcomp/competition-manager
```
Install all required libraries.
```
$ pip install numpy
$ pip install slackbot
$ pip install gspread
$ pip install oauth2client
$ pip install pyyaml
$ pip install pydrive
$ pip install discord.py
```

## Setting

### slackbotの設定
まず [Slack](https://slack.com/get-started#/create) のアカウントを作成する．

次に，[Slackbot](https://my.slack.com/services/new/bot) を作成する.

その後，APIトークンを作成し，次のファイルに記入する．
```
competition-manager/src/slackbot/slackbot_settings.py
```
最後に，Slackbotをチャンネル（e.g. #general）に追加する．

### testの設定
次のファイルにagent2dへのパスを記入する．
```
competition-manager/test/autotest.sh
```

### competition-managerの設定
次のファイルに各設定を書き込む．
```
competition-manager/config/manager.yml
```

[comment]: <> (### tournamentの設定)

[comment]: <> (toolでインストールしたtournamentの設定を行う．以下のファイルを作成・編集する．)

[comment]: <> (- confファイルの設定)

[comment]: <> (  - 次の行を試合設定によって変更する．)

[comment]: <> (```)

[comment]: <> (player_conf: config/rcssserver/player_official.conf)

[comment]: <> (server_conf: config/rcssserver/server_official.conf)

[comment]: <> (```)

### resultsの設定
tournamentの設定でmode_groupを使用する場合は必要なし

tournamentの設定でmode_single_matchを使用する場合
- google spreadsheetの設定jsonファイルを設置
- competition-manager/src/gametools/resultsにあるggssapi_gameresult.pyとstanding.pyの設定jsonファイルへのパスとドキュメントIDを設定
```
path='to/json/path.json'
doc_id='[document_id]'
```
上記の[document_id]は使用するspreadsheetのURLの以下の部分を参照
```
https://docs.google.com/spreadsheets/d/[document_id]/edit#gid=0
```


### GoogleDriveアップロードの設定
OAuthクライアントIDを取得する
- [参考](https://qiita.com/akabei/items/f25e4f79dd7c2f754f0e)

クライアントID，クライアントシークレットを以下のファイルに記入
```
competition-manager/config/manager.yml
```

以下のファイルを実行
```
$ cd competition-manager/config
$ python drive.py
```

認証を行う．以下のファイルが生成されていれば成功．
```
competition-manager/config/credentials.json
```

### チームリーダーの登録
チームをアップロードするユーザのメールアドレスを以下のファイルに記入
```
competition-manager/config/maillist.txt
```

## Usage
```
$ cd compatition-manager/src/slackbot
$ python ./run.py
```
このコマンド後は，slack上で操作


### 管理者用チャンネルで可能なコマンド
- コマンドの説明
```
help
```
- バイナリテスト完了チームリストの表示
```
team
```
- トーナメントのグループ作成
```
group* teamA,teamB,teamC,...
```
- トーナメントの開始
```
start group*
```
- トーナメントを開始後，以下のコマンドで試合の進行を通知
```
announce match
```
- slackbotにDMでバイナリ受け入れ開始コマンドを送信
```
binary upload start
binary upload end
```
- バイナリテスト完了チームリストの初期化
```
clear
```
- 各フラグの確認
```
status
```
- rcssserverのIPアドレスをセット（そのホストへは鍵交換をするなどしてパスワード無しで入れるようにしておく）
```
server *
```
- hostのIPアドレスをセット（そのホストへは鍵交換をするなどしてパスワード無しで入れるようにしておく）
```
host host1,host2
```
- Google Driveへ自動アップロード on (off)
```
gdrive true (or false)
```
- Google Driveに手動アップロード
```
share teams (or logs)
```
- Discord Botとの連携．Discordにも発言させる．
```
discordbot true (or false)
```

# Participants
[画像付きマニュアル](https://docs.google.com/document/d/1MCK7K-u6vaTPXFklca4m6ZYC2Izul3Cr4Psi4NJtS-Y/edit#)
## バイナリアップロード
- 管理者にチームをアップロードする人のslackで使用しているメールアドレスを以下のファイルに記入してもらう
`competition-manager/test/maillist.txt`

- チームバイナリの準備をする
  1. チームディレクトリを用意する．この時，チーム名とチームディレクトリの名前は同じにしておく
  2. チームディレクトリの中から必要なファイルを残し，それ以外のものは削除する．また，後述するstartとkill以外のファイルに関するディレクトリ構造に制限はない．例として agent2d の場合の必要なファイルを以下に挙げる．
     - coach.conf：agent2d-3.1.1/src/coach.conf
	 - player.conf：agent2d-3.1.1/src/player.conf
	 - sample_coach：agent2d-3.1.1/src/sample_coach
	 - sample_player：agent2d-3.1.1/src/sample_player
	 - フォーメーションのconfファイル：
	   - agent2d-3.1.1/src/formations-dt
	   - agent2d-3.1.1/src/formations-keeper
	   - agent2d-3.1.1/src/formations-taker
  3. 整理したディレクトリの中に以下のディレクトリとファイルを入れる．
     - ライブラリディレクトリ
	 - [start](https://drive.google.com/file/d/1UizYFqT5FSlhuAR-Hd6yCyXuuRcYdq6D/view?usp=sharing)
	 - [kill](https://drive.google.com/file/d/1HUDek415-KXovcY4msK3wIBIXzICR8Kt/view?usp=sharing)
  4. startファイルを書き換える．以下の部分をチームに対応する用に変更する
```
teamname="agent2d"
player="./sample_player"
coach="./sample_coach"
config="player.conf"
config_dir="formation-dt"
coach_config="coach.conf"
```
  5. ~/直下にチームディレクトリを配置して起動するか確認する
  6. 起動が確認でき``たら.tar.gz形式に圧縮する．上の部分で決定したチームネームの名前にする．

チームディレクトリの例
```
Example_team
├── ※lib (ライブラリディレクトリ)
├── formations-dt
├── coach.conf
├── kill
├── player.conf
├── sample_coach
├── sample_player
├── start
└── start.sh (起動確認用)
```

※参考：[librcsc](http://rctools.osdn.jp/pukiwiki/index.php?librcsc) の指定位置へインストールする場合

- アップロード
  1. チームアップロードの準備ができているか確認
  	 - チームディレクトリ名と圧縮後ファイル名が試合中のチーム名と同じになっているか確認
 	 - チーム名 team2020 の場合
	 /team2020 /team2020.tar.gz
  3. Slackのサイドバー"App"からCompetition-Manager(bot)を選択し，ダイ
  レクトメッセージで"upload [teamname]"を入力&バイナリ添付
 	 - チーム名がagent2dの場合，"upload agent2d"
	 - 添付時，アップロードが完了するまで待つ
	   - 容量が大きい場合はアップロード完了してからも10秒程待つ
	 - 一度に何度も送らないようにする
	 - 1チームずつ行う
  4. test完了メッセージを待つ
  5. Binary test succeededと表示されれば完了
 	 - その他のメッセージが表示されて中止された場合，バイナリを確認してやり直す
	 - わからない場合は運営に確認する
