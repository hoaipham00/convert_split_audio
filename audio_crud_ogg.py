from flask import Flask
from flask import jsonify, request
from flask_restful import Api, Resource, reqparse
from google.resumable_media import requests
import tinydb
from gcs_util import GoogleStorageUtil
from tinydb_util import AudioMetadata
from convert_long_audio_ogg import ConvertSplitAudioOGG
import json
import uuid
from requests.exceptions import Timeout
import math
import datetime
import os
import glob
from flask_cors import CORS
from pydub import AudioSegment
import subprocess
import io

BUCKET_NAME = 'hoai_try'
ORIGIN_BUCKET = 'audio-origin'
SPLIT_BUCKET = 'audio-split'

DATABASE_CONNECTION_STRING = '/home/lenovo/Desktop/convert_audio_2/audio_metadata/audio_db.json'
SAVE_PATH = '/home/lenovo/Desktop/convert_audio_2/audio_metadata'
DATABASE = ''
TABLE = ''

SOURCE_SPLIT = '/home/lenovo/Desktop/convert_audio_2/music'

BIG_CHUNK_AUDIO_SECONDS = 1800
FOLDER_DST_OGG = '/home/lenovo/Desktop/convert_audio_2/convert_to_ogg'

SMALL_CHUNK_AUDIO_SECONDS = 5
FOLDER_DST_CHUNK = '/home/lenovo/Desktop/convert_audio_2/split_5_seconds'

gcs_util = GoogleStorageUtil(BUCKET_NAME)
db_metadata_audio = AudioMetadata(DATABASE, TABLE, DATABASE_CONNECTION_STRING)
convert_split = ConvertSplitAudioOGG(SOURCE_SPLIT, FOLDER_DST_OGG, FOLDER_DST_CHUNK, BIG_CHUNK_AUDIO_SECONDS, SMALL_CHUNK_AUDIO_SECONDS)

app = Flask(__name__)
CORS(app)
cors = CORS(app, resource={
    r"/*":{
        "origins":"*"
    }
})

@app.route('/get-list-audio', methods=['GET'])
def get_list_audios():
    try:
        if request.method == 'GET':
            numPage = request.args.get('page')
            name = request.args.get('username')
            page = 0
            if (numPage is not None):
                page = int(numPage) - 1
                
            list_result, total_record = db_metadata_audio.get_all(page)
            return jsonify(results = list_result, total_record=total_record)
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
            numPage = request.args.get('page')
            name = request.args.get('name')
            owner = request.args.get('owner')
            page = 0
            if (numPage is not None):
                page = int(numPage) - 1
            if(name==''):
                name = None
            if(owner == ''):
                owner = None

            fields_dict = {'name': name, 'owner': owner, 'page': page}
            result, total_record = db_metadata_audio.get_by_multiple_fields(fields_dict)

            return jsonify(results = result, total_record=total_record)
    except Exception as error:
        return jsonify({'status': 'failed to search', 'error': error})
        print('Cannot search audio cause ' + repr(error))

def fill_full_metadata_audio(audio_info, audio_file, dest_upoad, id_parent, start_cutter, end_cutter):
    id = str(uuid.uuid4())
    save_path = SAVE_PATH + f'/{id}.ogg'
    dest_upload = f'{dest_upoad}/{id}.ogg'
    audio_file.save(save_path)
    audio_from_file = AudioSegment.from_file(save_path)
    audio_info['id']= id
    audio_info['last_updated'] = math.floor(datetime.datetime.now().timestamp())
    audio_info['path'] = f'gs://{BUCKET_NAME}/{dest_upload}'
    audio_info['url_path'] = f'https://storage.googleapis.com/{BUCKET_NAME}/{dest_upload}'
    audio_info['is_visible'] = True
    audio_info['id_parent'] = id_parent
    audio_info['start_cut'] = start_cutter
    audio_info['duration'] = audio_from_file.duration_seconds

    if(end_cutter == audio_info['duration'] or end_cutter == 0):
        audio_info['end_cut'] = audio_from_file.duration_seconds
        
    else:
        start = int(start_cutter)*1000
        end = int(end_cutter)*1000
        audio_from_file[start:end].export(save_path, format="ogg")

    return save_path, dest_upload, audio_info


@app.route('/insert-audio', methods=['POST'])
def insert_audio_blob():
    try:
        if request.method == 'POST':
            audio_file = request.files['audio-blob']
            audio_info = json.loads(request.form.get('info').replace("'",'"'))
            save_path, dest_upload, audio_insert = fill_full_metadata_audio(audio_info, audio_file, ORIGIN_BUCKET, '', 0, 0)
            db_metadata_audio.insert_to_db(audio_insert)
            gcs_util.upload_blob(save_path, dest_upload)
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
            dest_upload = f'{SPLIT_BUCKET}/{id}.ogg'
            audio_file = request.files['audio-blob']
            audio_info = json.loads(request.form.get('info').replace("'",'"'))

            save_path, dest_upload, audio_edit = fill_full_metadata_audio(audio_info, audio_file, SPLIT_BUCKET, audio_info['id'], audio_info['start_cut'], audio_info['end_cut'])
            db_metadata_audio.insert_to_db(audio_edit)
            gcs_util.upload_blob(save_path, dest_upload)
            # # gcs_util.edit_blob()
            os.remove(save_path)

            return jsonify({'status': 'success'})
    except Exception as error:
        return jsonify({'status': 'failed to edit', 'error': error})
        print('Cannot edit audio cause ' + repr(error))


# @app.route('/download-audios', methods=['POST'])
# def dowload():
#     try:
#         if request.method == 'POST':
#             body = json.loads(request.get_data().replace(b"'", b'"'))
#             username = body.get('username')
#             path_save_local = body.get('destination')
#             bucket_dir_download = body.get('source')
#             # print(path_save_local)
#             if (path_save_local is None):
#                 path_save_local = SOURCE_SPLIT
#             if(bucket_dir_download is None):
#                 bucket_dir_download = f'gs://{BUCKET_NAME}'
#             gcs_util.download_dir(bucket_dir_download, path_save_local)
#             return jsonify({'status': 'success'})
#     except Exception as error:
#         return jsonify({'status': 'failed to edit', 'error': error})
#         print('Cannot edit audio cause ' + repr(error))
        

# @app.route('/upload-audios', methods=['POST'])
# def upload():
#     try:
#         if request.method == 'POST':
#             body = json.loads(request.get_data().replace(b"'", b'"'))
#             username = body.get('username')
#             source_to_upload = body.get('source')
#             destination = body.get('destination')
#             if (source_to_upload is None):
#                 source_to_upload = FOLDER_DST_CHUNK
#             if(destination is None):
#                 destination = f'gs://{BUCKET_NAME}'

#             files = glob.glob(f'{source_to_upload}/**/*.ogg', recursive = True)
#             list_names = []
#             for file in files:
#                 split_array = file.split('/')
#                 list_names.append(split_array[-1])
#             for name in list_names:
#                 db_object = {
#                     'id': str(uuid.uuid4()),
#                     'name': name,
#                     'owner': username,
#                     'last_updated': math.floor(datetime.datetime.now().timestamp())
#                 }
#                 db_metadata_audio.insert_to_db(db_object)
                
#             gcs_util.upload_dir(source_to_upload, destination)
#             return jsonify({'status': 'success'})
#     except Exception as error:
#         return jsonify({'status': 'failed to edit', 'error': error})
#         print('Cannot edit audio cause ' + repr(error))

# @app.route('/split-all-audio-to-5s', methods=['POST'])
# def split_all_audio():
#     try:
#         if request.method == 'POST':
#             body = json.loads(request.get_data().replace(b"'", b'"'))
#             username = body.get('username')
#             src_slice = body.get('source')
#             dst_slice = body.get('destination')
#             if(src_slice is None):
#                 src_slice = SOURCE_SPLIT
#             if(dst_slice is None):
#                 dst_slice = FOLDER_DST_CHUNK
#             convert_split.convert_file_folder_to_ogg()
#             convert_split.split_all_audio_to_frame(SMALL_CHUNK_AUDIO_SECONDS)
#             return jsonify({'status': 'success to split audio'})
#     except Exception as error:
#         return jsonify({'status': 'failed to split', 'error': error})
#         print('Cannot split audio cause ' + repr(error))

# this is for metadata audio split
def add_info_metadata_split_audio(index, name, origin_metadata, file_name, folder_name, folder_dest_upload):
    audio_metadata_object = origin_metadata
    # file name in local
    id = file_name
    audio_metadata_object['name'] = f'{name}_split_{index}'
    audio_metadata_object['id'] = id.replace('.ogg','')
    audio_metadata_object['last_updated'] = math.floor(datetime.datetime.now().timestamp())
    audio_metadata_object['path'] = f'{folder_dest_upload}/{folder_name}/{file_name}'
    audio_metadata_object['url_path'] = f'https://storage.googleapis.com/{BUCKET_NAME}/{SPLIT_BUCKET}/{folder_name}/{file_name}'
    audio_metadata_object['start_cut'] = 0
    audio_metadata_object['end_cut'] = 5
    audio_metadata_object['duration'] = 5
    audio_metadata_object['transcrib'] = 'Please insert transcrib'
    audio_metadata_object['is_visible'] = True
    audio_metadata_object['id_parent'] = origin_metadata['id']
    return audio_metadata_object

@app.route('/split-audio', methods=['POST'])
def split_audio():
    try:
        if request.method == 'POST':
            body = json.loads(request.get_data().replace(b"'", b'"'))
            username = body.get('username')
            id = body.get('id')
            blob_path = body.get('path')
            name = body.get('name')


            # only use below func for python>=3.9
            blob_path_without_bucket = blob_path.removeprefix(f'gs://{BUCKET_NAME}/')
            dest_path = f'{SOURCE_SPLIT}/{id}.ogg'
            folder_dst = f'{id}_split'
            folder_source_upload = f'{FOLDER_DST_CHUNK}/{folder_dst}'
            folder_dest_upload = f'gs://hoai_try/{SPLIT_BUCKET}'
            gcs_util.dowload_object_blob(blob_path, dest_path)
            convert_split.convert_file_folder_to_ogg()

            convert_split.split_all_audio_to_frame(SMALL_CHUNK_AUDIO_SECONDS)
            
            gcs_util.upload_dir(folder_source_upload, folder_dest_upload)

            # upload_to_database
            list_files_name = os.listdir(folder_source_upload)

            for idx, each_file in enumerate(list_files_name):
                if (".ogg" in each_file):
                    audio_metadata_object = add_info_metadata_split_audio(idx, name, body, each_file, folder_dst, folder_dest_upload)
                    db_metadata_audio.insert_to_db(audio_metadata_object)

            return jsonify({'status': 'success to split audio'})
    except Exception as error:
        return jsonify({'status': 'failed to split', 'error': error})
        print('Cannot split audio cause ' + repr(error))

def update_metadata_audio(audio_source_path, origin_metadata):
    audio_from_file = AudioSegment.from_ogg(audio_source_path)
    duration = audio_from_file.duration_seconds
    origin_metadata['duration'] = duration
    origin_metadata['is_visible'] = True
    origin_metadata['last_updated'] = math.floor(datetime.datetime.now().timestamp())
    return origin_metadata


@app.route('/edit-multiple-audio', methods=['POST'])
def edit_multiple_audios():
    try:
        if request.method == 'POST':
            body = json.loads(request.get_data().replace(b"'", b'"'))
            list_audios = body.get('list')
            for audio in list_audios:
                id = audio.get('id')
                blob_path = audio.get('path')

                # only use below func for python>=3.9
                # blob_path_without_bucket = blob_path.removeprefix(f'gs://{BUCKET_NAME}/')

                dest_path = f'{SOURCE_SPLIT}/{id}.ogg'
                folder_dst = f'{id}_split'
                # download blob
                gcs_util.dowload_object_blob(blob_path, dest_path)
                # convert to format file ogg
                src_ogg = f'{SOURCE_SPLIT}/{id}.ogg'
                if('.ogg' not in blob_path):
                    convert_split.convert_file_folder_to_ogg()
                    src_ogg = f'{FOLDER_DST_OGG}/{id}.ogg'

                dst_split = f'{FOLDER_DST_CHUNK}/{folder_dst}.ogg'
                dst_upload = audio.get('path')
                # cut audio
                convert_split.audio_cutter(src_ogg, dst_split, audio.get('start_cut'), audio.get('end_cut'))

                # before upload, delete blob
                gcs_util.delete_blob_by_gsutil(blob_path)
                # upload to gcs
                gcs_util.upload_blob_by_gsutil(dst_split, dst_upload)

                # upload_to_database
                metadata = update_metadata_audio(dst_split, audio)
                db_metadata_audio.update_to_db(metadata)


                    
            return jsonify({'status': 'success to split multiple audios'})
    except Exception as error:
        return jsonify({'status': 'failed to split', 'error': error})
        print('Cannot split audio cause ' + repr(error))

@app.route('/delete-audio', methods=['POST'])
def delete_audios():
    try:
        if request.method == 'POST':
            body = json.loads(request.get_data().replace(b"'", b'"'))
            id = body.get('id')
            print(id)
            print(body)
            db_metadata_audio.delete_to_db(id)
                    
            return jsonify({'status': 'success to delete audio'})
    except Exception as error:
        return jsonify({'status': 'failed to split', 'error': error})
        print('Cannot split audio cause ' + repr(error))


app.run()