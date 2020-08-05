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
```

## Setting

### slackbotの設定
まず[Slack](https://slack.com/get-started#/create)のアカウントを作成する．

次に，[Slackbot](https://api.slack.com/bot-users)を作成する.

その後，APIトークンを作成し，次のファイルに記入する．
```
competition-manager/slackserver/slackbot/slackbot_settings.py
```
最後に，Slackbotをチャンネル（e.g. #general）に追加する．

### testの設定
次のファイルにagent2dへのパスを記入する．
```
competition-manager/test/autotest.sh
```

### tournamentの設定
toolでインストールしたtournamentの設定を行う．以下のファイルを作成・編集する．
```
tournament/config/config.yml
```
- ログの保存場所の設定
  - 次の行を任意のディレクトリに変更する．
```
log_dir: log/dir_name
```

- confファイルの設定
  - 次の行を試合設定によって変更する．
```
player_conf: config/rcssserver/player_official.conf
server_conf: config/rcssserver/server_official.conf
```

- チームディレクトリ位置の設定
  - 次の行を competition-manager/slackserver/slackbot/plugins/reply.py と同じディレクトリを指定する（初期設定は/home/user/）．
```
teams_dir: /home/user/
```

### reply.pyの設定
次のファイルを編集する．
```
competition-manager/slackserver/slackbot/plugins/reply.py
```
- 次の行をtournamentからconfigへの相対パスに設定
```
config='config/config.yml'
```

- organizerチャンネルの名前を設定
  - 次の行で，グループ作成や試合開始などを実行するチャンネルを設定
```
organize_ch_n='organizer'
```

- 管理者のid設定
  - 次の行で，バイナリアップロード開始コマンドなどを行うユーザのidを設定
```
organizer_id="ORGANIZER_ID"
```

- 次の行で，toolでインストールしたloganalyzer3への絶対パスを設定
```
loganalyzer_path='/home/user/path/to/loganalyzer3/'
```

- 次の行で，toolでインストールしたtournamentへの絶対パスを設定
```
tournament_path='/home/user/competition-manager/tournament/'
```

### resultsの設定
tournamentの設定でmode_groupを使用する場合は必要なし
tournamentの設定でmode_single_matchを使用する場合
- google spreadsheetの設定jsonファイルを設置
- competition-manager/slackserver/gametools/resultsにあるggssapi_gameresult.pyとstanding.pyの設定jsonファイルへのパスとドキュメントIDを設定
```
path='to/json/path.json'
doc_id='[document_id]'
```
上記の[document_id]は使用するspreadsheetのURLの以下の部分を参照
```
https://docs.google.com/spreadsheets/d/[document_id]/edit#gid=0
```
### チームリーダーの登録
チームをアップロードするユーザのメールアドレスを以下のファイルに記入
```
competition-manager/test/maillist.txt
```

## Usage
```
$ cd autogame/slackserver/slackbot
$ python ./run.py
```
このコマンド後は，slack上で操作


### 管理者のidに設定したuserで可能なコマンド
- slackbotにDMでバイナリ受け入れ開始コマンドを送信
```
upload start
upload end
```
- バイナリテスト完了チームリストの初期化
```
clear qualification
```
- 試合中フラグの初期化
```
gameflag false
```

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

# Participants

## バイナリアップロード
- 管理者にslackで使用しているメールアドレスを以下のファイルに記入してもらう
`competition-manager/test/maillist.txt`

- チームバイナリの準備をする
  1. チームディレクトリを用意する．この時，チーム名とチームディレクトリの名前は同じにしておく
  2. チームディレクトリの中から必要なファイルを残し，それ以外のものは削除する．また，後述するstartとkill以外のファイルに関するディレクトリ構造に制限はない．

  必要なファイルの例は以下の通り．例としてagent2dのパスを挙げておく．
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
  4. startファイルを書き換える
  以下の部分をチームに対応する用に変更する
```
teamname="agent2d"
player="./sample_player"
coach="./sample_coach"
config="player.conf"
config_dir="formation-dt"
coach_config="coach.conf"
```
  5. ~/直下にチームディレクトリを配置して起動するか確認する
  6. 起動が確認できたら.tar.gz形式に圧縮する．上の部分で決定したチームネームの名前にする．

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

※参考：[librcsc](http://rctools.osdn.jp/pukiwiki/index.php?librcsc)のインストール
- インストール > 指定位置へインストールする場合（推奨）

- アップロード
  1. チームアップロードの準備ができているか確認
  	 - チームディレクトリ名と圧縮後ファイル名が試合中のチーム名と同じになっているか確認
 	 - チーム名 team2020 の場合
	 /team2020 /team2020.tar.gz
  2. GameManager(bot)のDMで"bin [teamname]"を入力&バイナリ添付
 	 - チーム名がagent2dの場合，"bin agent2d"
	 - 添付時，アップロードが完了するまで待つ
	   - 容量が大きい場合はアップロード完了してからも10秒程待つ
	 - 一度に何度も送らないようにする
  3. test完了メッセージを待つ
  4. test completeと表示されれば完了
 	 - その他のメッセージが表示されて中止された場合，バイナリを確認してやり直す
	 - わからない場合は運営に確認する
