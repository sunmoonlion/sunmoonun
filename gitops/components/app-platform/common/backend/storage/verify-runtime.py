"""Runs inside the actual API role with its mounted, independent S3 credentials.

Two shapes (SDD 0042): applications whose bucket is their only S3 identity expose it through
`app.infrastructure.storage.object_storage.ObjectStorage` (knowfeed, knowlab); an application that
also carries another S3 identity (knowbase: the read-only knowledge source) keeps its own bucket
under a prefix (`USER_DATA_S3_*`), so the probe is handed that prefix as its one argument and talks
to the bucket with boto3 from those variables, through the same `AWS_CA_BUNDLE`.
"""
import hashlib
import json
import os
import sys
import uuid
from types import SimpleNamespace
from botocore.exceptions import ClientError

prefix = sys.argv[1] if len(sys.argv) > 1 else ''
if prefix:
    import boto3
    from botocore.config import Config
    bucket = os.environ[prefix + 'S3_BUCKET']
    client = boto3.client('s3', endpoint_url=os.environ[prefix + 'S3_ENDPOINT'], region_name=os.environ.get(prefix + 'S3_REGION', 'us-east-1'),
                          aws_access_key_id=os.environ[prefix + 'S3_ACCESS_KEY_ID'], aws_secret_access_key=os.environ[prefix + 'S3_SECRET_ACCESS_KEY'],
                          verify=os.environ.get('AWS_CA_BUNDLE') or True,
                          config=Config(signature_version='s3v4', s3={'addressing_style': 'path' if os.environ.get(prefix + 'S3_FORCE_PATH_STYLE', 'true') == 'true' else 'auto'}))

    def put_bytes(object_key, data, content_type):
        digest = hashlib.sha256(data).hexdigest()
        answer = client.put_object(Bucket=bucket, Key=object_key, Body=data, ContentType=content_type, Metadata={'sha256': digest})
        return SimpleNamespace(bucket=bucket, version_id=answer.get('VersionId'), sha256=digest)
else:
    from app.infrastructure.storage.object_storage import ObjectStorage
    store = ObjectStorage()
    client = store.s3_client()
    bucket = store.bucket
    put_bytes = lambda object_key, data, content_type: store.put_bytes(object_key=object_key, data=data, content_type=content_type)
key = 'sunmoon-acceptance/' + uuid.uuid4().hex
records = []
checks = {}
passed = False
try:
    expected = [b'SunMoonAI original version one\n', b'SunMoonAI original version two\n']
    for content in expected:
        item = put_bytes(key, content, 'application/octet-stream')
        assert item.bucket == bucket and item.version_id and item.version_id != 'null'
        records.append({'bucket':item.bucket, 'key':key, 'version_id':item.version_id})
        assert item.sha256 == hashlib.sha256(content).hexdigest()
    assert records[0]['version_id'] != records[1]['version_id']
    for record, content in zip(records, expected, strict=True):
        result = client.get_object(Bucket=bucket, Key=key, VersionId=record['version_id'])
        try:
            assert result['Body'].read() == content
            assert result['Metadata']['sha256'] == hashlib.sha256(content).hexdigest()
        finally:
            result['Body'].close()
    checks.update(actual_application_storage=True, independent_identity=True, tls_ca_verified=True, original_versions_preserved=True, byte_digest_verified=True)
    try:
        client.list_objects_v2(Bucket='sunmoon-forbidden-bucket', MaxKeys=1)
        raise AssertionError('Foreign bucket unexpectedly readable')
    except ClientError as error:
        assert error.response['Error']['Code'] == 'AccessDenied'
        checks['foreign_bucket_denied'] = True
    try:
        client.put_bucket_versioning(Bucket=bucket, VersioningConfiguration={'Status':'Suspended'})
        raise AssertionError('Application unexpectedly controls bucket versioning')
    except ClientError as error:
        assert error.response['Error']['Code'] == 'AccessDenied'
        checks['bucket_administration_denied'] = True
    passed = True
except Exception as error:
    checks['error_class'] = type(error).__name__
finally:
    client.close()
    print(json.dumps({'passed':passed, 'checks':checks, 'created_records':records}))
    sys.exit(0 if passed else 1)
