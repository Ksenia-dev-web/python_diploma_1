import requests
from pprint import pprint
from tqdm import tqdm
import json

vKtoken = '958eb5d439726565e9333aa30e50e0f937ee432e927f0dbd541c541887d919a7c56f95c04217915c32008'
yAndextoken = ''

vK_account = input('Введите id аккаунта ВКонтакте:')
# собираем фото аккаунта
# максимальный ра3мер
class vkUser:
    # url = 'https://api.vk.com/method/'
    def __init__(self, VKtoken, version):
        self.token = vKtoken
        self.version = version
        self.url = 'https://api.vk.com/method/'
        self.params = {
            'access_token': self.token,
            'v': self.version
        }

    def get_profile_photos(self, user_id=vK_account, count=5):
        final_list = []
        photo_params = {
            'owner_id': user_id,
            'album_id': 'profile',
            'extended': 1,
            'photo_sizes': 1
        }
        res = requests.get(self.url + 'photos.get', params={**self.params, **photo_params})
        try:
            list_of_all_photos = res.json()['response']['items']
        except KeyError:
            print('Фотографии недоступны')
            list_of_all_photos = []
        for photo in tqdm(list_of_all_photos):
            for each_size in photo['sizes']:
                max_size = max(photo['sizes'], key=lambda item: item['height'] * item['width'])
            final_list.append({'likes': str(photo['likes']['count']), 'url': max_size['url'],
                               'date': str(photo['date']), 'type': max_size['type']})
        return final_list

# загрузка на диск
# создание json

class Upload_to_yandex_disk:
    def __init__(self, token):
        self.token = yAndextoken
        self.headers = {'Authorization': self.token}

    def make_new_folder(self, name):
        url = 'https://cloud-api.yandex.net/v1/disk/resources'
        params = {'path': name}
        requests.put(url=url, params=params, headers=self.headers)

    def execute_upload_vk(self, vkUser):
        folder_new = 'account_pics'
        self.make_new_folder(folder_new)
        pic_extraction = vkUser.get_profile_photos()
        pic_list = []
        pic_list_for_file = []
        for pic in tqdm(pic_extraction):
            if pic['likes'] not in pic_list:
                new_pic = pic['likes']
            else:
                new_pic = pic['likes'] + pic['date']
            pic_list.append(new_pic)

            path = folder_new + '/' + new_pic
            url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
            params = {'url': pic['url'], 'path': path}
            res = requests.post(url=url, params=params, headers=self.headers)
            pic_list_for_file.append({'file_name': new_pic, 'size': pic['type']})
        with open('list_of_pics', 'w') as f:
            json.dump(pic_list_for_file, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    uploader = Upload_to_yandex_disk(yAndextoken)
    vk_user = vkUser(vKtoken, '5.130')
    uploader.execute_upload_vk(vk_user)
