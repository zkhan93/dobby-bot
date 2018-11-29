from flask import Blueprint, request, current_app
from operator import methodcaller
import requests

api = Blueprint('api', 'api_bp', url_prefix='/api')


@api.route('/', methods=['GET', 'POST'])
def home():
    data = request.json
    file_info_url = current_app.config.get('TELEGRAM_FILE_INFO_URL')
    file_download_url = current_app.config.get('TELEGRAM_FILE_URL')
    if data:
        message = data.get('message')
        if message:
            photo = message.get('photo')
            if photo:
                photo.sort(key=methodcaller('__getitem__', 'file_size'))
                file_id = photo[-1].get('file_id')
                try:
                    file_info_res = requests.get(file_info_url, params={'file_id': file_id})
                except Exception as ex:
                    print('Error getting file info')
                    print(str(ex))
                else:
                    if file_info_res.ok:
                        file_info = file_info_res.json()
                        if file_info and file_info.get('result'):
                            file_info = file_info.get('result')
                            file_path = file_info.get('file_path')
                            if file_path:
                                print('download file with url:', '{}{}'.format(file_download_url, file_path))
                                try:
                                    file_res = requests.get('{}{}'.format(file_download_url, file_path))
                                except Exception as ex:
                                    print('Error getting file')
                                    print(str(ex))
                                else:
                                    if file_res.ok:
                                        image_bin_data = file_res.content
                    else:
                        print('getting file info request not ok')
    return 'Working!!'
