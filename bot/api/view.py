from flask import Blueprint, request, current_app as app
from operator import methodcaller
import requests
import time
import os
from bot.facerec import extract_faces

api = Blueprint('api', 'api_bp', url_prefix='/api')


@api.route('/', methods=['GET', 'POST'])
def home():
    data = request.json
    print(data)
    app.logger.debug(data)
    file_info_url = app.config.get('TELEGRAM_FILE_INFO_URL')
    file_download_url = app.config.get('TELEGRAM_FILE_URL')
    if data:
        message = data.get('message')
        if message:
            photo = message.get('photo')
            if photo:
                photo.sort(key=methodcaller('__getitem__', 'file_size'))
                app.logger.info(photo)
                file_id = photo[-1].get('file_id')
                app.logger.info('file_id ' + str(file_id))
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
                            app.logger.info(file_info)
                            file_path = file_info.get('file_path')
                            if file_path:
                                print('download file with url:', '{}{}'.format(file_download_url, file_path))
                                try:
                                    file_res = requests.get('{}{}'.format(file_download_url, file_path), stream=True)
                                except Exception as ex:
                                    print('Error getting file')
                                    print(str(ex))
                                else:
                                    if file_res.ok:
                                        filepath = os.path.join('tmp', str(time.time()) + app.config.get('IMG_EXTN'))
                                        with open(filepath, 'wb') as f:
                                            for chunk in file_res.iter_content(1024):
                                                f.write(chunk)
                                        app.logger.info('new image written at ' + filepath)
                                        app.logger.info('faces' + str(extract_faces(filepath)))
                                    else:
                                        print('getting file data request not ok: ' + file_res.url)
                    else:
                        print('getting file info request not ok: ' + file_info_res.url)
    return 'Working!!'
