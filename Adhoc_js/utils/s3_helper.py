import os
import boto3
import logging
import datetime
from utils.error_handling import log_error_and_raise_exception

bucket_name = 'campaign-ims-users-migration'
aws_profile = 'campaign-provisioning'

def fetch_file_from_s3(object_name, file_path, tenant_id, aci_instance_id):
    session = boto3.Session(profile_name=aws_profile)
    s3_client = session.client('s3')

    try:
        todays_date = get_date_for_s3_path()
        object_key = os.path.join(tenant_id+"_"+aci_instance_id, todays_date, object_name).lstrip('/')
        s3_client.download_file(bucket_name, object_key, file_path)
        logging.info("File downloaded from S3: {}/{}".format(bucket_name, object_key))
    except Exception as exception:
        log_error_and_raise_exception("An error occurred while downloading the file", exception)

def push_file_to_s3(object_name, file_path, tenant_id, aci_instance_id):
    session = boto3.Session(profile_name=aws_profile)
    s3_client = session.client('s3')

    try:
        todays_date = get_date_for_s3_path()
        object_key = os.path.join(tenant_id+"_"+aci_instance_id, todays_date, object_name).lstrip('/')
        s3_client.upload_file(file_path, bucket_name, object_key)
        logging.info("{} file uploaded to S3: {}/{}/{}".format(file_path, bucket_name, object_key, object_name))
    except Exception as exception:
        log_error_and_raise_exception("An error occurred while uploading the file to S3", exception)

def delete_file_from_s3(object_name, tenant_id, aci_instance_id):
    session = boto3.Session(profile_name=aws_profile)
    s3_client = session.client('s3')
    try:
        todays_date = get_date_for_s3_path()
        object_key = os.path.join(tenant_id+"_"+aci_instance_id, todays_date, object_name).lstrip('/')
        s3_client.delete_object(Bucket=bucket_name, Key=object_key)
        logging.info("{} file deleted from S3: {}/{}".format(object_name, bucket_name, object_key))
    except Exception as exception:
        log_error_and_raise_exception("An error occurred while uploading the file to S3", exception)

def get_date_for_s3_path():
    current_date = datetime.datetime.now().date()
    formatted_date = current_date.strftime("%Y%m%d")
    return formatted_date

def delete_file_or_directory(file_path):
    try:
        if os.path.isfile(file_path): 
            os.remove(file_path)  
            logging.info("File {} deleted successfully.".format(file_path))
        # elif os.path.isdir(file_path):  
        #     os.rmdir(file_path)  
        #     logging.info("Directory {} deleted successfully.".format(file_path))
        else:
            logging.warning("Path '{}' does not exist or is not a file or directory.".format(file_path))
    except Exception as exception:
        log_error_and_raise_exception("An error occurred while deleting file at path '{}'".format(file_path), exception)
