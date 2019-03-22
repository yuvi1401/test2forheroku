import requests
import time
import base64
import hmac
import hashlib
from audio_analysis.acrconfig import identify_access_key, identify_access_secret, \
    identify_host, signature_version, account_access_key, account_access_secret, account_host


def sign(string_to_sign, secret):
    return base64.b64encode(
        hmac.new(secret.encode(), string_to_sign.encode(), digestmod = hashlib.sha1)
            .digest())


def identify_audio(audio_file, sample_bytes):
    data_type = 'audio'
    http_method = "POST"
    http_uri = "/v1/identify"
    timestamp = time.time()

    string_to_sign = '\n'.join(
        (http_method, http_uri, identify_access_key, data_type, signature_version, str(timestamp)))

    signature = sign(string_to_sign, identify_access_secret)

    files = {'sample': audio_file}

    data = {'access_key': identify_access_key,
            'sample_bytes': sample_bytes,
            'timestamp': str(timestamp),
            'signature': signature,
            'data_type': data_type,
            "signature_version": signature_version}

    requrl = identify_host + http_uri

    r = requests.post(requrl, files = files, data = data)
    r.encoding = "utf-8"

    res = r.json()

    return res
    # audio_id = base64.b64decode(res["metadata"]["music"][0]["acrid"])


def create_acr_bucket(name):
    http_method = "POST"
    timestamp = str(time.time())
    uri = '/v1/buckets'

    string_to_sign = '\n'.join((http_method, uri, account_access_key, signature_version, timestamp))

    signature = sign(string_to_sign, account_access_secret)

    headers = {'access-key': account_access_key, 'signature-version': signature_version, 'signature': signature,
               'timestamp': timestamp}

    data = {'name': name,
            'type': 'File',
            'scale': '10',
            'region': "eu-west-1",
            'content_type': 'Music'}

    requrl = account_host + uri

    r = requests.post(requrl, data = data, headers = headers, verify = True)

    r.encoding = 'utf-8'

    print(r.text)


def upload_audio(audio_file, filename, session_id):

    http_method = "POST"
    timestamp = str(time.time())
    uri = "/v1/audios"

    string_to_sign = '\n'.join(
        (http_method, uri, account_access_key, signature_version, str(timestamp)))

    signature = sign(string_to_sign, account_access_secret)

    files = {'audio_file': ("audio_file", audio_file)}

    headers = {'access-key': account_access_key, 'signature-version': signature_version, 'signature': signature,
               'timestamp': timestamp}

    data = {'title': filename, "audio_id": session_id, "bucket_name": "ssc_bucket", "data_type": "audio"}

    requrl = account_host + uri

    r = requests.post(requrl, files = files, data = data, headers = headers, verify = True)

    r.encoding = "utf-8"

    res = r.json()

    return res
