import requests
from progress.bar import ShadyBar

class YaUploader:
    def __init__(self, user_token_file):
        with open(user_token_file, 'r') as token_file:
            self.token = token_file.read().strip()

    def headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': f'OAuth {self.token}'
        }
    def _get_upload_link(self, disk_file_path):
        url = f'https://cloud-api.yandex.net/v1/disk/resources/upload'
        params = {'path': disk_file_path, 'overwrite': 'true'}
        res = requests.get(url, headers=self.headers(), params=params)
        return res.json()

    def upload(self, file_list, disk_file_folder):
        bar = ShadyBar('Загрузка файлов на Ya.Disk:')
        for file in file_list:
            url = self._get_upload_link(f'{disk_file_folder}/{file}').get('href', '')
            res = requests.put(url=url, data=open(file, 'rb'))
            res.raise_for_status()
            if res.status_code == 201:
                print(f'Файл "{file}" успешно загружен в папку "{disk_file_folder}"')
                bar.next()


if __name__ == '__main__':
    path_to_token = 'TokenYa.txt'
    uploader = YaUploader(path_to_token)
    file_list = ['HW_file.txt', 'HW_file_for_test_list_uploading.txt']
    disk_file_folder = 'HomeWorks'
    uploader.upload(file_list, disk_file_folder)

