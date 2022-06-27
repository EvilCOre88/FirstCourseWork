import json
import requests
import time

from progress.bar import IncrementalBar


class GetPhotos:
    def __init__(self):
        self.vk_token = input('Введите название .txt файла с VK.Токеном или введите токен вручную: ').strip()
        if self.vk_token[-3:] == 'txt':
            with open(self.vk_token, 'r') as token_file:
                self.vk_token = token_file.read().strip()
        self.files_dict = {}
        self.photos_dump = []
        self.count = 5
        self.user_profile = input('Введите профиль пользователя: ').strip()
        self.vk_url = 'https://api.vk.com/method'

    def user_input(self):
        params = {
            'user_ids': f'{self.user_profile}',
            'v': '5.131',
            'access_token': self.vk_token
        }
        res = requests.get(url=f'{self.vk_url}/users.get', params=params).json()
        try:
            try:
                if self.user_profile.isdigit():
                    return int(self.user_profile)
                else:
                    return int(res['response'][0]['id'])
            except IndexError:
                quit(f'Введен не корректный профиль!')
        except KeyError:
            quit(f'Введен не верный токен!')

    def __get_albums(self):
        params = {
            'owner_id': self.user_input(),
            'need_system': 1,
            'v': '5.131',
            'access_token': self.vk_token
        }
        try:
            all_albums = requests.get(url=f'{self.vk_url}/photos.getAlbums', params=params).json()['response']['items']
            albums_ids = {all_albums[i]['title']: all_albums[i]["id"] for i in range(len(all_albums))}
            for album, ids in albums_ids.items():
                print(f'Альбом: {album} ; ID: {ids}')
            return input('Введите ID альбома из представленных для загрузки: ')
        except KeyError:
            print(f'Данные этого профиля заблокированы, но мы поищем в служебных альбомах)')
            return 'profile'

    @property
    def get_photos(self):
        res = {}
        res_list = []
        params = {
            'owner_id': f'{self.user_input()}',
            'album_id': f'{self.__get_albums()}',
            'extended': 1,
            'v': '5.131',
            'photo_sizes': 0,
            'access_token': self.vk_token
        }
        try:
            res = requests.get(url=f'{self.vk_url}/photos.get', params=params).json()['response']
            if res["count"] >= 5:
                try:
                    self.count = int(input(f'Введите количество фотографий для загрузки '
                                           f'(минимум 5 , максимум {res["count"]}): '))
                    if self.count < 5:
                        quit(f'Вы ввели число меньше минимального!')
                except ValueError:
                    quit(f'Вы ввели не число!')
            else:
                self.count = res["count"]
        except KeyError:
            quit(f'Такого альбома не существует или доступ закрыт!')
        for item in res["items"]:
            res_dict = {}
            res_dict['likes'] = int(item['likes']['count'])
            res_dict['url'] = item['sizes'][-1]['url']
            res_dict['type'] = item['sizes'][-1]['type']
            res_dict['date'] = item['date']
            if item['sizes'][-1]['height'] >= item['sizes'][-1]['width']:
                res_dict['size'] = item['sizes'][-1]['height']
            else:
                res_dict['size'] = item['sizes'][-1]['width']
            res_list.append(res_dict)
        if self.count >= 5:
            for i in range(res["count"]-self.count):
                into_pop = min([res_list[i]['size'] for i in range(len(res_list))])
                for pop_id, item in enumerate(res_list):
                    if res_list[pop_id]['size'] == into_pop:
                        res_list.pop(pop_id)
                        break
            res = res_list
        else:
            res = res_list
        for item in res:
            if f'{item["likes"]}.jpg' not in [i for i in self.files_dict.keys()]:
                self.files_dict[f'{item["likes"]}.jpg'] = item["url"]
                self.photos_dump.append({'filename': f'{item["likes"]}.jpg',
                                         'size': item["size"]})
            else:
                date = time.strftime("%d-%m-%Y_%H-%M-%S", time.localtime(item['date']))
                self.files_dict[f'{item["likes"]}_{date}.jpg'] = item["url"]
                self.photos_dump.append({'filename': f'{item["likes"]}.jpg',
                                         'size': item["size"]})
        return [self.files_dict, self.photos_dump]


class YaUploader:
    def __init__(self):
        self.ya_token = input('Введите название .txt файла с Я.Токеном или введите токен вручную: ').strip()
        if self.ya_token[-3:] == 'txt':
            with open(self.ya_token, 'r') as token_file:
                self.ya_token = token_file.read().strip()
        self.disk_file_folder = input('Введите название папки для сохранения фото: ')

    def headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': f'OAuth {self.ya_token}'
        }

    def photo_dump(self, dump_list):
        dump_name = f'photos_dump.json'
        with open(dump_name, 'a') as dump_file:
            json.dump([{time.strftime("%d-%m-%Y"): time.strftime("%H-%M-%S")}], dump_file, indent=4)
            json.dump(dump_list, dump_file, indent=4)

    def __create_folder(self):
        url = f'https://cloud-api.yandex.net/v1/disk/resources'
        params = {'path': self.disk_file_folder}
        res = requests.put(url=url, headers=self.headers(), params=params).json()
        if 'href' in res.keys():
            print(f'Папка {self.disk_file_folder} успешно создана! Записываем файлы!')
        else:
            print(f'Папка {self.disk_file_folder} уже существует... Но мы все-равно записываем файлы!')

    def upload(self, file_dict):
        url = f'https://cloud-api.yandex.net/v1/disk/resources/upload'
        self.__create_folder()
        bar = IncrementalBar('Загрузка файлов на Ya.Disk:', max=len(file_dict))
        for file_name, file_url in file_dict.items():
            params = {'path': f'/{self.disk_file_folder}/{file_name}', 'url': file_url}
            requests.post(url=url, headers=self.headers(), params=params)
            time.sleep(0.3)
            bar.next()
        bar.finish()
        input('Файлы успешно загружены, нажмите любую кнопку')


if __name__ == '__main__':
    photos = GetPhotos().get_photos
    uploader = YaUploader()
    uploader.photo_dump(photos[1])
    uploader.upload(photos[0])
