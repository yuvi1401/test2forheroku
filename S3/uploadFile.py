import boto3
import botocore

# Create an S3 client
s3 = boto3.client('s3')

filename = 'new_encrypted_file'
bucket_name = 'lizzie-bucket'

# Uploads the given file using a managed uploader, which will split up large
# files automatically and upload parts in parallel.
try:
    s3.upload_file(filename, bucket_name, filename)
    print('Upload complete')
except Exception as e:
        print('Upload Failed!')
        print(e)






