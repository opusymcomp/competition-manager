import requests
import codecs
import slackbot_settings
from slacker import Slacker
slacker = Slacker(slackbot_settings.API_TOKEN)

class DownloadFile:
    def __init__(self, file_types, save_directly):
        # 引数が省略された場合は、デフォルトのタイプを指定
        self.file_types = file_types
        self.save_directly = save_directly
    def exe_download(self, file_info):

        file_name = file_info['name']
        url_private = file_info['url_private_download']
        # 保存対象のファイルかチェックする
        print(file_info['filetype'])
        if file_info['filetype'] in self.file_types:
            # ファイルをダウンロード
            self.file_download(url_private, self.save_directly + file_name)
            return 'ok'
        else:
            # 保存対象外ファイル
            return 'file type is not applicable.'
    def file_download(self, download_url, save_path):
        content = requests.get(
            download_url,
            allow_redirects=True,
            headers={'Authorization': 'Bearer %s' % slackbot_settings.API_TOKEN}, stream=True
        ).content
        # 保存する
        target_file = codecs.open(save_path, 'wb')
        target_file.write(content)
        target_file.close()
