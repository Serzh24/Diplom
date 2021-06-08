import requests
import json
import pprint
import time
from tqdm import tqdm

class VKontakte:

    def __init__(self, user_ident):
        self.user_ident = user_ident

    def get_photos_list(self):
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
            'count': '5',
            'access_token': '958eb5d439726565e9333aa30e50e0f937ee432e927f0dbd541c541887d919a7c56f95c04217915c32008',
            'v': '5.131'
        }
        res = requests.get(url, params=params)
        result_request = res.json()
        # pprint.pprint(result_request)
        return result_request

    def get_likes(self):
        likes_url = {}
        for el in user.get_photos_list()['response']['items']:
            likes_url[(str(el['likes']['count']))+'_'+(str(el['date']))] = el['sizes'][-1]['url']
        return likes_url

    def get_info(self):
        list_image_info = []
        for el in user.get_photos_list()['response']['items']:
            image_info = {}
            image_info['file_name'] = (str(el['likes']['count']))+'_'+(str(el['date']))
            image_info['size'] = el['sizes'][-1]['type']
            list_image_info.append(image_info)
        print(list_image_info)
        return list_image_info

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
        # if response.status_code == 201:
        #     print("Success")

TOKEN = ""

if __name__ == '__main__':
    user = VKontakte('552934290')
    user.get_photos_list()
    user.get_likes()
    ya = YandexDisk(token=TOKEN)
    ya.create_folder(disk_file_path='Photos')
    for k, v in tqdm(user.get_likes().items()):
        ya.upload_file_to_disk_url(disk_file_path='Photos/'+k, download_url=v)
        time.sleep(1)
    pprint.pprint(user.get_likes())
    with open('info.json', 'w') as file:
        json.dump(user.get_info(), file, indent=2)
    ya.upload_file_to_disk(disk_file_path='Photos/info.json', filename='info.json')