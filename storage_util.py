# from gcloud import storage
# import os
# credentials_dict = {
#     'type': 'service_account',
#     'client_id': os.environ['BACKUP_CLIENT_ID'],
#     'client_email': os.environ['BACKUP_CLIENT_EMAIL'],
#     'private_key_id': os.environ['BACKUP_PRIVATE_KEY_ID'],
#     'private_key': os.environ['BACKUP_PRIVATE_KEY'],
# }
# credentials = ServiceAccountCredentials.from_json_keyfile_dict(
#     credentials_dict
# )

from google.cloud import storage
from google.cloud.storage import bucket
from termcolor import colored
import os

BUCKET_NAME = 'hoai_try'

class GoogleStorageUtil():
    def __init__(self, bucket_name):
        self.bucket_name = bucket_name
        self.storage_client = storage.Client()

    def get_list_buckets(self):
        buckets = list(self.storage_client.list_buckets())
        for bucket in buckets:
            print(type(bucket))

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
    
    def upload(self, src_path_upload, dest_path_upload, blob_name):
        bucket = self.storage_client.get_bucket(dest_path_upload)
        blob = bucket.blob(blob_name)
        #load from local
        blob.upload_from_filename(src_path_upload)

    def get_object_in_bucket(self):
        bucket = self.storage_client.get_bucket(self.bucket_name)
        for blob in bucket.list_blobs():
            print(blob.name, blob.size)
    
    def dowload_object_blob(self, src_path_blob, dst_path):
        # can use gsutil, example: 
        # gsutil cp gs://hoai_try/demo2.py C:/Users/ADMIN/Desktop/grokking_lab/tryyy/tenten/

        bucket = self.storage_client.get_bucket(self.bucket_name)
        blob = bucket.blob(src_path_blob)
        blob.download_to_filename(dst_path)

    def download_dir(self, dst_dir_local):
        prefix = '/'
        bucket = self.storage_client.get_bucket(self.bucket_name)
        blobs = bucket.list_blobs(prefix=prefix)  # Get list of files
        for blob in blobs:
            filename = blob.name.replace('/', '_') 
            blob.download_to_filename(dst_dir_local + filename)

    def delete_blob(self, blob_path):
        bucket = self.storage_client.bucket(self.bucket_name)
        blob = bucket.blob(blob_path)
        blob.delete()
        print("Blob {} deleted.".format(blob_path))

    def delete_dir(self):
        bucket = self.storage_client.get_bucket(self.bucket_name)
        blobs = bucket.list_blobs(prefix='/')
        for blob in blobs:
            blob.delete()

if __name__ == '__main__':
    gcs_util = GoogleStorageUtil(BUCKET_NAME)
    print(colored("Please wait.....", "green"))
    print(colored("..............................................................", "green"))
    gcs_util.get_bucket_metadata_by_name()
    print(colored("..............................................................", "green"))
    print(colored('Completed','green'))
