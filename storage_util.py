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
# client = storage.Client(credentials=credentials, project='olli-iviet')
# bucket = client.get_bucket('hoai_try')
# blob = bucket.blob('demo')
# blob.upload_from_filename('myfile')
from google.cloud import storage
from google.cloud.storage import bucket
storage_client = storage.Client()

def get_list_buckets():
    buckets = list(storage_client.list_buckets())
    for bucket in buckets:
        print(type(bucket))

def get_bucket_metadata_by_name():
    bucket = storage_client.get_bucket('hoai_try')
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

def upload():
    bucket = storage_client.get_bucket('hoai_try')
    blob = bucket.blob('/demo2.py')
    #load from local
    blob.upload_from_filename('C:/Users/ADMIN/Desktop/grokking_lab/tryyy/audio_import.py')

def get_object_in_bucket():
    bucket = storage_client.get_bucket('hoai_try')
    for blob in bucket.list_blobs():
        print(blob.name, blob.size)


# not working but use gsuit working
def dowload_object_blob():
# can use gsutil like: 
# gsutil cp gs://hoai_try/demo2.py C:/Users/ADMIN/Desktop/grokking_lab/tryyy/tenten/

    bucket = storage_client.get_bucket('hoai_try')
    blob = bucket.blob('/haha/hihi.html')
    blob.download_to_filename('C:/Users/ADMIN/Desktop/grokking_lab/tryyy/kaka.html')

def download_dir():
    bucket_name = 'hoai_try'
    prefix = '/'
    dl_dir = 'C:/Users/ADMIN/Desktop/grokking_lab/tryyy/download_all/'
    bucket = storage_client.get_bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=prefix)  # Get list of files
    for blob in blobs:
        print("blob: ", blob)
        filename = blob.name.replace('/', '_') 
        blob.download_to_filename(dl_dir + filename)


def delete_blob():
    bucket = storage_client.bucket('hoai_try')
    blob = bucket.blob('/haha/hihi.html')
    blob.delete()
    print("Blob {} deleted.".format('hihi.html'))

def delete_dir():
    bucket = storage_client.get_bucket('hoai_try')
    blobs = bucket.list_blobs(prefix='/')
    for blob in blobs:
        blob.delete()


# upload()
# dowload_object_blob()
# get_bucket_metadata_by_name()
# get_object_in_bucket()
# download_dir()
# delete_blob()
delete_dir()