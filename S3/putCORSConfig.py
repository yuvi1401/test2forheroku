import boto3

# Create an S3 client
s3 = boto3.client('s3')

# Create the CORS configuration
cors_configuration = {
    'CORSRules': [{
        'AllowedHeaders': ['Authorization'],
        'AllowedMethods': ['GET', 'PUT'],
        'AllowedOrigins': ['*'],
        'ExposeHeaders': ['GET', 'PUT'],
        'MaxAgeSeconds': 3000
    }]
}

# Set the new CORS configuration on the selected bucket
s3.put_bucket_cors(Bucket='lizzie-bucket', CORSConfiguration=cors_configuration)
