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
  - cython

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
$ pip install cython
```

## Setting

### slackbotで用いる外部ツールの設定

#### [Loganalyzer3](https://github.com/opusymcomp/loganalyzer3.git)
- 以下のコマンドでloganalyzer3をダウンロードする．

`$ git clone https://github.com/opusymcomp/loganalyzer3.git`

- 必要なライブラリをインストールする．
  - matplotlib
  - cython

- 以下のコマンドでコンパイルする．`finish compiliation`とでたら成功．
```
$ cd /path/to/loganalyzer3
$ ./build.sh
```  

#### [tournament](https://github.com/rcsoccersim/tournament.git)
- 以下のコマンドでtournamentをダウンロードする．

`$ git clone https://github.com/rcsoccersim/tournament.git`

- 必要なライブラリをインストールする

`# apt-get install ruby`

#### サーバ，ホスト
tournamentスクリプトはパスワードなしでログインできる状態が前提となっている．
鍵交換にて接続するサーバにパスワードなしで入れるようにしておく．
一度は接続し，sshの初回認証を済ませておく．

### slackbotの設定
まず [Slack](https://slack.com/get-started#/create) のアカウントを作成する．

次に，[Slackbot](https://my.slack.com/services/new/bot) を作成する.

SlackBotに発言させたいチャンネルにBotを追加する．

### [GoogleDrive](https://console.developers.google.com/)
GoogleDriveClientIdを取得する．
ログやバイナリを公開するため，「外部」を選択し，テストユーザーとして，自分のアカウントを登録する．

（!!!外部かつテストのとき，一週間経過するとアプリの認証が切れます．詳細は下でも書いてます!!!）

### [Discordbot](https://discord.com/login?redirect_to=%2Fdevelopers%2Fapplications%2F)
Discordボットのセットアップを行い，トークンを得る．
用いない場合は無視して良い．


### competition-managerの設定
次のファイルに各設定を書き込む．
```
competition-manager/config/manager.yml
```

各設定項目は以下の通りである．

- `competition_manager_path`: 
  - このソースまでのパスを記入する．最後にスラッシュをつけるのを忘れずに．
  - RoboCup2021の設定例：`/Users/fukushima/rcss/competition-manager/`
- `tournamant_path`:
  - loganalyzer3までのパスを記入する．最後にスラッシュをつけるのを忘れずに．
  - RoboCup2021の設定例：`/Users/fukushima/rcss/loganalyzer3/`
- `tournamant_path`:
  - tournamentまでのパスを記入する．最後にスラッシュをつけるのを忘れずに．
  - RoboCup2021の設定例：`/Users/fukushima/rcss/tournament/`
- `username`:
  - サーバ上のユーザ名を記入する．特に理由がなければrobocupでいいかと思われる．（ドキュメントでも/home/robocup/{teamname}で動くようにチームバイナリを作成するように指示しているため．）
  - RoboCup2021の設定例：`robocup`
- `slack_api_token`: 
  - SlackBot利用時のAPIトークンを書き込む．
  - 上記で設定したらAPIトークンをコピーできる．
- `dropbox`関連:
  - 用いていないため不明．動作確認もしていない．
- `google_drive_client_id`:
  - GoogleDriveにアップロードするためのクライアントIDを書き込む．
  - 上記で設定したら獲得可能．
- `google_drive_folder_id`: 
  - GoogleDriveのアップロード先を書き込む．
  - Googleドライブ上に共有フォルダを先に作成する．
  - ユーザアクセスを"リンクを知っている全員"に変更する．
  - リンク”https://drive.google.com/drive/folders/○○”における○○の部分を記載する．
- `discord_token`: 
  - Discordで発言するためのトークンを書き込む．
  - Discordボットセットアップ時に得られるトークンを記載する．
- `discord_channel_id`:
  - Discordで発言するチャンネルIDを書き込む．
  - チャンネルIDは下記のルールで記載されている．
  - https://discord.com/channels/`ServerID`/`ChannelID`
- `organizer_channnel_name`:
  - Slackの運営用チャンネル名を書き込む．このチャンネル内で各権限や試合実行等のコマンドを入力する． 
  - RoboCup2021の設定例：`organizer`
- `announce_channel_name`: 
  - Slack．Discordの通知用チャンネル名を書き込む．
  - このチャンネル内に試合結果やファイル共有先などが書き込まれる．
  - main_tournament_channel, sub_tournament_channelの名前は変更してもよい．また，３つ以上のチャンネルを設定しても良い．
  - それぞれの設定名に対して，slackのチャンネル名とDiscordのID名を記入する． Discordを用いない場合は書く必要はない． 
  - RoboCup2021の設定例：
    ```
    main_tournament_channnel:
        slack: scores
        discord: ???
    ```
- `competition_name`:
  - ログやチームを共有する際の，フォルダ名に用いる．
  - RoboCup2021の設定例：`RoboCup2021`
- `teams_dir`:
  - チームバイナリのアーカイブ箇所を指定する．
  - RoboCup2021の設定例：`/Users/fukushima/rcss/competition-manager/teams/`
- `log_dir`:
  - RoboCup2021の設定例：`/Users/fukushima/rcss/competition-manager/logs/`


### (2021-12-04追記) SlackBot: ”Error: method_deprecated”が出る場合について
https://api.slack.com/changelog/2021-10-rtm-start-to-stop

2021-11-30をもって，rtm.start関数が動かなくなったらしい．
SlackBotは未だにこの関数で実装されているものなので，ライブラリの更新を待つ他ない．（2021-12-04現在，slackbot ver 1.0.0）

ライブラリ内，slackclient.pyの45行目付近と60行目付近を以下のように書き換えるとなんとかなる．
ライブラリを直接変更するため，仮想環境などを用いることを推奨．

↓変更前（45行目付近）

`reply = self.webapi.rtm.start(**(self.rtm_start_args or {})).body`

↓変更後

`reply = self.webapi.rtm.connect(**(self.rtm_start_args or {})).body`

↓変更前（60行目付近）

`self.parse_user_data(login_data['users'])`

↓変更後

`self.parse_user_data(self.webapi.users.list().body['members'])`

↓変更前（60行目付近）
```
self.parse_channel_data(login_data['channels'])
self.parse_channel_data(login_data['groups'])
self.parse_channel_data(login_data['ims'])
```

↓変更後

`self.parse_channel_data(self.webapi.conversations.list(types=['public_channel', 'private_channel', 'mpim', 'im']).body['channels'])`


### testの設定
テスト実行時の敵として，HELIOS_baseをcompetition-manager/testディレクトリの中におく． 
フォルダ名は必ずagent2dとし，他チームと同様startスクリプトなどを決められた形に沿って配置する．


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

一週間経過するとアプリの認証が切れる．
そのため，再度上記コマンドを実行し認証を行う必要がある．

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
allow binary upload
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


### Competition-manager 実行例
テスト時
```
server 192.168.1.2

host 192.168.1.2,192.168.1.2

allow binary upload

… （全チームのバイナリアップロード完了）

binary upload end
```

試合実行時
```
（まとめて設定する場合　set group以下順不同）
set groupA --teams=team1,team2,team3 --server=192.168.1.2 --hosts=192.168.1.2,192.168.1.2 --channel=main_tournament_channel --roundrobin-title=SeedingRound --mode=group --server-conf=server_official.conf

start groupA

announce match groupA
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
