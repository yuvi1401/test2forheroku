import boto3

# Create an S3 client
s3 = boto3.client('s3')

# Call S3 to get CORS configuration for selected bucket
#result = s3.get_bucket_cors(Bucket='shumi-bucket')
result = s3.get_bucket_acl(Bucket='lizzie-bucket')


#result = s3.delete_bucket_cors(Bucket='shumi-bucket')

print (result)