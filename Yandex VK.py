import requests
import json
import pprint
import time
from tqdm import tqdm
import datetime

class VKontakte:

    def __init__(self, user_ident, access_token):
        self.user_ident = user_ident
        self.access_token = access_token

    def get_photos_list(self, count_photos):
        url = 'https://api.vk.com/method/photos.get'
        params = {
            'user_id': self.user_ident,
            'album_id': 'profile',
            # 'photo_ids': '',
            'rev': '0',
            'extended': '1',
            # 'feed_type': '',
            'photo_sizes': '1',
            # 'offset': '',
            'count': count_photos,
            'access_token': self.access_token,
            'v': '5.131'
        }
        res = requests.get(url, params=params)
        result_request = res.json()
        # pprint.pprint(result_request)
        return result_request

    def get_likes(self):
        likes_url = {}
        for el in user.get_photos_list(count_photos)['response']['items']:
            unix_date = el['date']
            value = datetime.datetime.fromtimestamp(unix_date)
            standart_date = value.strftime('%Y-%m-%d %H-%M-%S')
            if str(el['likes']['count']) in likes_url:
                likes_url[(str(el['likes']['count']))+'_'+(str(standart_date))] = el['sizes'][-1]['url']
            else:
                likes_url[(str(el['likes']['count']))] = el['sizes'][-1]['url']
        # print('Выведем список имен файлов со ссылками:')
        # pprint.pprint(likes_url)
        return likes_url

    def get_info(self):
        list_name = []
        list_size = []
        for k in user.get_likes().keys():
            dict_name = {}
            dict_name['file_name'] = k
            list_name.append(dict_name)
        for el in user.get_photos_list(count_photos)['response']['items']:
            dict_size = {}
            dict_size['size'] = el['sizes'][-1]['type']
            list_size.append(dict_size)
        # print(list_name)
        # print(list_size)
        list_info = list(zip(list_name, list_size))
        return list_info

class YandexDisk:

    def __init__(self, token):
        self.token = token

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.token)
        }

    def create_folder(self, disk_file_path):
        url = "https://cloud-api.yandex.net/v1/disk/resources"
        headers = self.get_headers()
        params = {"path": disk_file_path}
        response = requests.put(url, headers=headers, params=params)
        response.raise_for_status()
        # if response.status_code == 201:
        #     print("Success")

    def upload_file_to_disk_url(self, disk_file_path, download_url):
        url_method = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        headers = self.get_headers()
        params = {"path": disk_file_path, "url": download_url}
        response = requests.post(url_method, headers=headers, params=params)
        response.raise_for_status()
        # if response.status_code == 202:
        #     print("Success")

    def _get_upload_link(self, disk_file_path):
        upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        headers = self.get_headers()
        params = {"path": disk_file_path, "overwrite": "true"}
        response = requests.get(upload_url, headers=headers, params=params)
        return response.json()

    def upload_file_to_disk(self, disk_file_path, filename):
        href = self._get_upload_link(disk_file_path=disk_file_path).get("href", "")
        response = requests.put(href, data=open(filename, 'rb'))
        response.raise_for_status()
        if response.status_code == 201:
            print("Файл успешно загружен.")

    def get_files_list(self, disk_file_path):
        file_folders_list = []
        files_url = 'https://cloud-api.yandex.net/v1/disk/resources'
        headers = self.get_headers()
        params = {"path": disk_file_path}
        response = requests.get(files_url, headers=headers, params=params)
        file_folders = response.json()
        for el in file_folders['_embedded']['items']:
            file_folders_list.append(el['name'])
        print(f'Проверим список имеющихся папок на диске: {file_folders_list}')
        return file_folders_list

if __name__ == '__main__':
    user = VKontakte(user_ident=input('Введите id ВК или имя пользователя: '), access_token=input('Введите токен ВК: '))
    count_photos = str(input('Введите максимальное количество загружаемых фотографий: '))
    user.get_photos_list(count_photos)
    ya = YandexDisk(token=input('Введите токен Яндекс.Диск: '))
    new_folder = input('Введите название новой папки: ')
    print()
    for i in ya.get_files_list('/'):
        if i == new_folder:
            new_folder = input('Такая папка уже существует! Придумайте другое название: ')
    print()
    ya.create_folder(disk_file_path=new_folder)
    print('Выведем список новых имен файлов со ссылками: ')
    pprint.pprint(user.get_likes())
    print()
    print('Сформируем отчет о загружаемых файлах - название и размер: ')
    print(user.get_info())
    print()
    print('Начинается загрузка файлов на Яндекс.Диск...')
    for k, v in tqdm(user.get_likes().items()):
        ya.upload_file_to_disk_url(disk_file_path=new_folder+'/'+k, download_url=v)
        time.sleep(1)
    print()
    print('Загружаем файл с информацией о файлах на Яндекс.Диск в формате json...')
    print()
    with open('info.json', 'w') as file:
        json.dump(user.get_info(), file, indent=2)
    ya.upload_file_to_disk(disk_file_path=str(new_folder)+'/info.json', filename='info.json')