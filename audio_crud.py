from flask import Flask
from flask import jsonify, request
from flask_restful import Api, Resource, reqparse
from google.resumable_media import requests
import tinydb
from gcs_util import GoogleStorageUtil
from tinydb_util import AudioMetadata
from convert_audio_long_audio import ConvertSplitAudio
import json
import uuid
from requests.exceptions import Timeout
from scipy.io import wavfile
import math
import datetime
import os
import glob

BUCKET_NAME = 'hoai_try'
DATABASE_CONNECTION_STRING = '/home/lenovo/Desktop/convert_audio_2/audio_metadata/audio_info.json'
SAVE_PATH = '/home/lenovo/Desktop/convert_audio_2/audio_metadata'
DATABASE = ''
TABLE = ''

SOURCE_SPLIT = '/home/lenovo/Desktop/convert_audio_2/music'

BIG_CHUNK_AUDIO_SECONDS = 1800
FOLDER_DST_WAV = '/home/lenovo/Desktop/convert_audio_2/convert_to_wav'

SMALL_CHUNK_AUDIO_SECONDS = 5
FOLDER_DST_CHUNK = '/home/lenovo/Desktop/convert_audio_2/split_5_seconds'

gcs_util = GoogleStorageUtil(BUCKET_NAME)
db_metadata_audio = AudioMetadata(DATABASE, TABLE, DATABASE_CONNECTION_STRING)
convert_split = ConvertSplitAudio(SOURCE_SPLIT, FOLDER_DST_WAV, FOLDER_DST_CHUNK, BIG_CHUNK_AUDIO_SECONDS, SMALL_CHUNK_AUDIO_SECONDS)

app = Flask(__name__)

@app.route('/get-list-audio', methods=['GET'])
def get_list_audios():
    try:
        if request.method == 'GET':
            page = int(request.args.get('page'))
            name = request.args.get('username')
            if (page is None):
                page = 0
            else:
                page = page - 1
            list_result = db_metadata_audio.get_all(page)
            return jsonify(results = list_result)
    except Exception as error:
        return jsonify({'status': 'failed to get', 'error': error})
        print('Cannot get all list blob cause: ' + repr(error))

@app.route('/get-audio-by-id', methods=['POST'])
def get_list_audios_by_id():
    try:
        if request.method == 'POST':
            body = json.loads(request.get_data().replace(b"'", b'"'))
            username = body.get('username')
            
            # you can use blob's metadata 
            # path = f'music/{body.get("id")}'
            # blob_metadata = gcs_util.get_blob_metadata(path)

            blob_metadata = db_metadata_audio.get_by_id(body.get("id"))
            return jsonify(results = blob_metadata)

    except Exception as error:
        return jsonify({'status': 'failed to get by id', 'error': error})
        print('Cannot get audio by id cause ' + repr(error))

@app.route('/search-audio', methods=['GET'])
def search_audio():
    try:
        if request.method == 'GET':
            username = request.args.get('username')
            page = int(request.args.get('page'))
            name = request.args.get('name')
            owner = request.args.get('owner')
            if (page is None):
                page = 0
            else:
                page = page - 1
            fields_dict = {'name': [name], 'owner': [owner], 'page': page}

            result = db_metadata_audio.get_by_multiple_fields(fields_dict)
            return jsonify(results = result)
    except Exception as error:
        return jsonify({'status': 'failed to search', 'error': error})
        print('Cannot search audio cause ' + repr(error))    

@app.route('/insert-audio', methods=['POST'])
def insert_audio_blob():
    try:
        if request.method == 'POST':
            # get data json from form body
            id = str(uuid.uuid4())
            audio_file = request.files['audio-blob']
            audio_info = json.loads(request.form.get('info').replace("'",'"'))

            audio_info['id_source': None]
            audio_info['start_cut': None]
            audio_info['end_cut': None]
            audio_info['id']= id
            audio_info['last_updated'] = math.floor(datetime.datetime.now().timestamp())

            save_path = SAVE_PATH + f'/{id}'
            audio_file.save(save_path)
            dest_upload = f'music/{id}.wav'

            db_metadata_audio.insert_to_db(audio_info)
            gcs_util.upload_blob(save_path, dest_upload, id)
            os.remove(save_path)

            return jsonify({'status': 'success'})
    except Exception as error:
        return jsonify({'status': 'failed to insert', 'error': error})
        print('Cannot insert audio cause ' + repr(error))

@app.route('/edit-audio', methods=['POST'])
def edit_audio_blob():
    try:
        if request.method == 'POST':
            # get data json from form body
            id = str(uuid.uuid4())
            audio_file = request.files['audio-blob']
            audio_info = json.loads(request.form.get('info').replace("'",'"'))

            audio_info['id_source'] = audio_info['id']
            audio_info['id']= id
            audio_info['last_updated'] = math.floor(datetime.datetime.now().timestamp())

            start_cutter = audio_info['start_cut']
            end_cutter = audio_info['end_cut']

            save_path = SAVE_PATH + f'/{id}'
            audio_file.save(save_path)

            sampleRate, waveData = wavfile.read(save_path )
            startSample = int( start_cutter * sampleRate )
            endSample = int( end_cutter * sampleRate )
            wavfile.write(save_path, sampleRate, waveData[startSample:endSample])

            dest_upload = f'music/{id}.wav'

            db_metadata_audio.insert_to_db(audio_info)
            gcs_util.upload_blob(save_path, dest_upload, id)
            gcs_util.edit_blob
            os.remove(save_path)

            return jsonify({'status': 'success'})
    except Exception as error:
        return jsonify({'status': 'failed to edit', 'error': error})
        print('Cannot edit audio cause ' + repr(error))


@app.route('/download-audios', methods=['POST'])
def dowload():
    try:
        if request.method == 'POST':
            body = json.loads(request.get_data().replace(b"'", b'"'))
            username = body.get('username')
            path_save_local = body.get('destination')
            bucket_dir_download = body.get('source')
            # print(path_save_local)
            if (path_save_local is None):
                path_save_local = SOURCE_SPLIT
            if(bucket_dir_download is None):
                bucket_dir_download = f'gs://{BUCKET_NAME}'
            gcs_util.download_dir(bucket_dir_download, path_save_local)
            return jsonify({'status': 'success'})
    except Exception as error:
        return jsonify({'status': 'failed to edit', 'error': error})
        print('Cannot edit audio cause ' + repr(error))
        

@app.route('/upload-audios', methods=['POST'])
def upload():
    try:
        if request.method == 'POST':
            body = json.loads(request.get_data().replace(b"'", b'"'))
            username = body.get('username')
            source_to_upload = body.get('source')
            destination = body.get('destination')
            # print(path_save_local)
            if (source_to_upload is None):
                source_to_upload = FOLDER_DST_CHUNK
            if(destination is None):
                destination = f'gs://{BUCKET_NAME}'

            files = glob.glob(f'{source_to_upload}/**/*.wav', recursive = True)
            list_names = []
            for file in files:
                split_array = file.split('/')
                list_names.append(split_array[-1])
            for name in list_names:
                db_object = {
                    'id': str(uuid.uuid4()),
                    'name': name,
                    'owner': username,
                    'last_updated': math.floor(datetime.datetime.now().timestamp())
                }
                db_metadata_audio.insert_to_db(db_object)
                
            gcs_util.upload_dir(source_to_upload, destination)
            return jsonify({'status': 'success'})
    except Exception as error:
        return jsonify({'status': 'failed to edit', 'error': error})
        print('Cannot edit audio cause ' + repr(error))

@app.route('/split-all-audio-to-5s', methods=['POST'])
def split_all_audio():
    try:
        if request.method == 'POST':
            body = json.loads(request.get_data().replace(b"'", b'"'))
            username = body.get('username')
            src_slice = body.get('source')
            dst_slice = body.get('destination')
            if(src_slice is None):
                src_slice = SOURCE_SPLIT
            if(dst_slice is None):
                dst_slice = FOLDER_DST_CHUNK
            convert_split.convert_file_folder_to_wav()
            convert_split.split_all_audio_to_frame()
            return jsonify({'status': 'success to split audio'})
    except Exception as error:
        return jsonify({'status': 'failed to split', 'error': error})
        print('Cannot split audio cause ' + repr(error))


app.run()