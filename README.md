# competition-manager

link to [manual](https://docs.google.com/document/d/1kATDp0V7TZ60z0wWNn--v5CRXlhoadd7kaIN9_PI7oM/edit?usp=sharing)

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
- tournamentの設定でmode_groupを使用する場合は必要なし
- tournamentの設定でmode_single_matchを使用する場合
  - google spreadsheetの設定jsonファイルを設置
  - competition-manager/slackserver/gametools/resultsにある
  ggssapi_gameresult.pyとstanding.pyの設定jsonファイルへのパスとドキュ
  メントIDを設定
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
コマンドの説明
```
help
```
バイナリテスト完了チームリストの表示
```
team
```
