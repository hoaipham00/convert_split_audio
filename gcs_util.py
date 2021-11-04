from google.cloud import storage
from google.cloud.storage import bucket
from termcolor import colored
import os
import glob
import datetime;
import math
import subprocess

BUCKET_NAME = 'hoai_try'

class GoogleStorageUtil():
    def __init__(self, bucket_name):
        self.bucket_name = bucket_name
        self.storage_client = storage.Client()

    def pretty_response(self, blob):
        if(blob.metadata is not None):
            return {
                'id': blob.metadata.get('gen_id'),
                'path': blob.name,
                'name': blob.name,
                'owner': blob.metadata.get('owner'),
                'last_updated': blob.metadata.get('last_updated'),
                'size': blob.size
            }
        else:
            return {
                'id': blob.id,
                'path': blob.name,
                'name': blob.name,
                'owner': blob.owner,
                'last_updated': blob.updated,
                'size': blob.size
            } 

    def get_list_blobs(self):
        blobs = self.storage_client.list_blobs(self.bucket_name)
        list_blobs_name = []
        for blob in blobs:
            list_blobs_name.append(self.pretty_response(blob))
        return list_blobs_name

    def get_list_blobs_with_prefix(self, prefix, delimiter=None):
            # If you specify prefix ='a/', without a delimiter, you'll get back:

            #   a/1.txt
            #   a/b/2.txt

            # However, if you specify prefix='a/' and delimiter='/', you'll get back
            # only the file directly under 'a/':
            #     a/1.txt

        blobs = self.storage_client.list_blobs(self.bucket_name, prefix=prefix, delimiter=delimiter)
        list_blobs_name = []
        for blob in blobs:
            # print(blob.metadata)
            if(blob.metadata is not None):
                list_blobs_name.append(blob.metadata)
            else:
                list_blobs_name.append({})
        return list_blobs_name


    def get_bucket_metadata_by_name(self):
        bucket = self.storage_client.get_bucket(self.bucket_name)
        print(f"ID: {bucket.id}")
        print(f"Name: {bucket.name}")
        print(f"Storage Class: {bucket.storage_class}")
        print(f"Location: {bucket.location}")
        print(f"Location Type: {bucket.location_type}")
        print(f"Cors: {bucket.cors}")
        print(f"Default Event Based Hold: {bucket.default_event_based_hold}")
        print(f"Default KMS Key Name: {bucket.default_kms_key_name}")
        print(f"Metageneration: {bucket.metageneration}")
        print(
            f"Public Access Prevention: {bucket.iam_configuration.public_access_prevention}"
        )
        print(f"Retention Effective Time: {bucket.retention_policy_effective_time}")
        print(f"Retention Period: {bucket.retention_period}")
        print(f"Retention Policy Locked: {bucket.retention_policy_locked}")
        print(f"Requester Pays: {bucket.requester_pays}")
        print(f"Self Link: {bucket.self_link}")
        print(f"Time Created: {bucket.time_created}")
        print(f"Versioning Enabled: {bucket.versioning_enabled}")
        print(f"Labels: {bucket.labels}")
    
    def set_blob_metadata(self, blob_name, user_name, id):
        try:
            # save as timestamp unix
            ts = math.floor(datetime.datetime.now().timestamp())

            #use this to convert timestamp to datetime
            # datetime.datetime.utcfromtimestamp(ts).strftime('%Y-%m-%dT%H:%M:%SZ')
            metadata = {
                'gen_id': id, 
                'name': blob_name,
                'owner': user_name,
                'last_updated': ts  
                }
            return metadata
        except Exception as error:
            print('Caught this error: ' + repr(error))

    def edit_blob(self, blob_name, id):
        try:
            bucket = self.storage_client.bucket(self.bucket_name)
            blob = bucket.get_blob(blob_name)
            blob.metadata = self.set_blob_metadata(blob_name=blob_name, user_name='hoaipham', id=id)
            blob.patch()
        except Exception as error:
            print('Cannot update metadata of blob cause: ' + repr(error))

    def upload_blob(self, src_path_upload, dest_blob):
        try:
            bucket = self.storage_client.get_bucket(self.bucket_name)
            blob = bucket.blob(dest_blob)
            #load from local
            blob.upload_from_filename(src_path_upload)
        except Exception as error:
            print('Cannot upload blob cause: ' + repr(error))
    
    def upload_blob_by_gsutil(self, src_path_upload, dest_blob):
        try:
           command = f'gsutil cp {src_path_upload} {dest_blob}'
           subprocess.run(command, shell=True)

        except Exception as error:
            print('Cannot upload blob cause ' + repr(error))



    def upload_dir(self, src_dir_upload, dest_dir_bucket):
        # rel_paths = glob.glob(src_dir_upload + '/**', recursive=True)
        # bucket = self.storage_client.get_bucket(self.bucket_name)
        # for local_file in rel_paths:
        #     remote_path = f'{dest_dir_name}/{"/".join(local_file.split(os.sep)[1:])}'
        #     if os.path.isfile(local_file):
        #         blob = bucket.blob(remote_path)
        #         blob.metadata = self.set_blob_metadata(blob_name=remote_path, user_name='hoaipham')
        #         blob.upload_from_filename(local_file)

        try:
            command = f'gsutil -m cp -r dir {src_dir_upload} {dest_dir_bucket}'
            subprocess.run(command, shell=True)
        except Exception as error:
            print('Cannot upload entire directory cause ' + repr(error))


    # blob_name = 'your-object-name'
    def get_blob_metadata(self, blob_name):
        bucket = self.storage_client.bucket(self.bucket_name)
        blob = bucket.get_blob(blob_name)

        print("Blob: {}".format(blob.name))
        print("Bucket: {}".format(blob.bucket.name))
        print("Storage class: {}".format(blob.storage_class))
        print("ID: {}".format(blob.id))
        print("Size: {} bytes".format(blob.size))
        print("Updated: {}".format(blob.updated))
        print("Generation: {}".format(blob.generation))
        print("Metageneration: {}".format(blob.metageneration))
        print("Etag: {}".format(blob.etag))
        print("Owner: {}".format(blob.owner))
        print("Component count: {}".format(blob.component_count))
        print("Crc32c: {}".format(blob.crc32c))
        print("md5_hash: {}".format(blob.md5_hash))
        print("Cache-control: {}".format(blob.cache_control))
        print("Content-type: {}".format(blob.content_type))
        print("Content-disposition: {}".format(blob.content_disposition))
        print("Content-encoding: {}".format(blob.content_encoding))
        print("Content-language: {}".format(blob.content_language))
        print("Metadata: {}".format(blob.metadata))
        print("Custom Time: {}".format(blob.custom_time))
        print("Temporary hold: ", "enabled" if blob.temporary_hold else "disabled")
        print(
            "Event based hold: ",
            "enabled" if blob.event_based_hold else "disabled",
        )
        if blob.retention_expiration_time:
            print(
                "retentionExpirationTime: {}".format(
                    blob.retention_expiration_time
                )
            )

        return self.pretty_response(blob)

    def dowload_object_blob(self, src_path_blob, dst_path):
        # can use gsutil, example: 
        # gsutil cp gs://hoai_try/demo2.py C:/Users/ADMIN/Desktop/grokking_lab/tryyy/tenten/

        # bucket = self.storage_client.get_bucket(self.bucket_name)
        # blob = bucket.blob(src_path_blob)
        # blob.download_to_filename(dst_path)

        try:
            command = f'gsutil -o GSUtil:parallel_composite_upload_threshold=100M cp {src_path_blob} {dst_path}'
            subprocess.run(command, shell=True)
        except Exception as error:
            print('Cannot upload entire directory cause ' + repr(error))


    def download_dir(self, src_dir_bucket, dst_dir_local):
        try:
            command = f'gsutil -m cp -r dir {src_dir_bucket} {dst_dir_local}'
            subprocess.run(command, shell=True)
        except Exception as error:
            print('Cannot download entire bucket cause ' + repr(error))

    def delete_blob(self, blob_path):
        bucket = self.storage_client.bucket(self.bucket_name)
        blob = bucket.blob(blob_path)
        blob.delete()
        print("Blob {} deleted.".format(blob_path))

    def delete_blob_by_gsutil(self, blob_path):
        try:
            command = f'gsutil rm {blob_path}'
            subprocess.run(command, shell=True)
        except Exception as error:
            print('Cannot delete blob cause ', repr(error))

    def delete_dir(self):
        bucket = self.storage_client.get_bucket(self.bucket_name)
        blobs = bucket.list_blobs(prefix='/')
        for blob in blobs:
            blob.delete()




# slice upload
# gsutil -o "GSUtil:parallel_thread_count=1" -o "GSUtil:parallel_process_count=8" cp /home/lenovo/Desktop/convert_audio_2/audio_metadata/7de386c1-b7ed-4291-9dfa-b72cd98f6b2a.wav gs://hoai_try/audio-origin/large_audio.wav

# parallel upload
# gsutil -o GSUtil:parallel_composite_upload_threshold=100M  cp /home/lenovo/Desktop/convert_audio_2/audio_metadata/7de386c1-b7ed-4291-9dfa-b72cd98f6b2a.wav gs://hoai_try/audio-origin/large2_audio.wav
