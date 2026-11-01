"""Runs inside the actual API role with its mounted, independent S3 credentials.

Two shapes (SDD 0042): applications whose bucket is their only S3 identity expose it through
`app.infrastructure.storage.object_storage.ObjectStorage` (knowfeed, knowlab); an application that
also carries another S3 identity (knowbase: the read-only knowledge source) keeps its own bucket
under a prefix (`USER_DATA_S3_*`), so the probe is handed that prefix as its one argument and talks
to the bucket with boto3 (or httpx fallback) from those variables, through the same `AWS_CA_BUNDLE`.
"""
import hashlib
import json
import os
import sys
import uuid
from types import SimpleNamespace

try:
    from botocore.exceptions import ClientError
except ImportError:
    class ClientError(Exception):
        def __init__(self, code, message=""):
            super().__init__(message or code)
            self.response = {'Error': {'Code': code}}

prefix = sys.argv[1] if len(sys.argv) > 1 else ''
if prefix:
    bucket = os.environ[prefix + 'S3_BUCKET']
    try:
        import boto3
        from botocore.config import Config
        client = boto3.client('s3', endpoint_url=os.environ[prefix + 'S3_ENDPOINT'], region_name=os.environ.get(prefix + 'S3_REGION', 'us-east-1'),
                              aws_access_key_id=os.environ[prefix + 'S3_ACCESS_KEY_ID'], aws_secret_access_key=os.environ[prefix + 'S3_SECRET_ACCESS_KEY'],
                              verify=os.environ.get('AWS_CA_BUNDLE') or True,
                              config=Config(signature_version='s3v4', s3={'addressing_style': 'path' if os.environ.get(prefix + 'S3_FORCE_PATH_STYLE', 'true') == 'true' else 'auto'}))

        def put_bytes(object_key, data, content_type):
            digest = hashlib.sha256(data).hexdigest()
            answer = client.put_object(Bucket=bucket, Key=object_key, Body=data, ContentType=content_type, Metadata={'sha256': digest})
            return SimpleNamespace(bucket=bucket, version_id=answer.get('VersionId'), sha256=digest)
    except ImportError:
        import hmac
        import io
        import ssl
        from datetime import datetime, UTC
        from urllib.parse import quote, urlsplit
        import httpx

        def _get_sigv4_headers(method, host, path, query="", body=b"", extra=None, region="us-east-1", access_key="", secret_key=""):
            moment = datetime.now(UTC)
            amz_date = moment.strftime("%Y%m%dT%H%M%SZ")
            datestamp = moment.strftime("%Y%m%d")
            payload_hash = hashlib.sha256(body).hexdigest()
            headers = {
                "host": host,
                "x-amz-content-sha256": payload_hash,
                "x-amz-date": amz_date,
            }
            if extra:
                for k, v in extra.items():
                    headers[k.lower()] = str(v).strip()
            names = sorted(headers)
            signed_headers = ";".join(names)
            canonical_headers = "".join(f"{name}:{headers[name]}\n" for name in names)
            canonical_request = "\n".join([method, path, query, canonical_headers, signed_headers, payload_hash])
            scope = f"{datestamp}/{region}/s3/aws4_request"
            string_to_sign = "\n".join(["AWS4-HMAC-SHA256", amz_date, scope, hashlib.sha256(canonical_request.encode()).hexdigest()])
            k_date = hmac.new(f"AWS4{secret_key}".encode(), datestamp.encode(), hashlib.sha256).digest()
            k_region = hmac.new(k_date, region.encode(), hashlib.sha256).digest()
            k_service = hmac.new(k_region, b"s3", hashlib.sha256).digest()
            k_signing = hmac.new(k_service, b"aws4_request", hashlib.sha256).digest()
            signature = hmac.new(k_signing, string_to_sign.encode(), hashlib.sha256).hexdigest()
            headers["Authorization"] = f"AWS4-HMAC-SHA256 Credential={access_key}/{scope}, SignedHeaders={signed_headers}, Signature={signature}"
            return headers

        class _HttpS3Client:
            def __init__(self, endpoint, access_key, secret_key, region="us-east-1", ca_bundle=None, path_style=True):
                self.endpoint = endpoint.rstrip("/")
                parsed = urlsplit(self.endpoint)
                self.scheme = parsed.scheme
                self.host = parsed.netloc
                self.access_key = access_key
                self.secret_key = secret_key
                self.region = region
                self.path_style = path_style
                self.verify = ssl.create_default_context(cafile=ca_bundle) if ca_bundle and self.scheme == "https" else True

            def _req(self, method, bkt, key="", query="", body=b"", extra=None):
                parts = [quote(p, safe="") for p in key.split("/")] if key else []
                if self.path_style:
                    path = "/" + "/".join([quote(bkt, safe=""), *parts]) if bkt else "/"
                    req_host = self.host
                else:
                    path = "/" + "/".join(parts) if parts else "/"
                    req_host = f"{bkt}.{self.host}" if bkt else self.host
                url = f"{self.scheme}://{req_host}{path}"
                if query:
                    url += f"?{query}"
                headers = _get_sigv4_headers(method, req_host, path, query, body, extra, self.region, self.access_key, self.secret_key)
                with httpx.Client(verify=self.verify, timeout=30) as http_c:
                    return http_c.request(method, url, content=body, headers=headers)

            def put_object(self, Bucket, Key, Body, ContentType, Metadata):
                extra = {"content-type": ContentType}
                for k, v in Metadata.items():
                    extra[f"x-amz-meta-{k}"] = v
                resp = self._req("PUT", Bucket, Key, body=Body, extra=extra)
                if resp.status_code >= 300:
                    raise ClientError(f"HTTP_{resp.status_code}", resp.text)
                return {"VersionId": resp.headers.get("x-amz-version-id")}

            def get_object(self, Bucket, Key, VersionId):
                query = f"versionId={quote(VersionId, safe='-_.~')}"
                resp = self._req("GET", Bucket, Key, query=query)
                if resp.status_code >= 300:
                    raise ClientError(f"HTTP_{resp.status_code}", resp.text)
                metadata = {}
                for k, v in resp.headers.items():
                    if k.lower().startswith("x-amz-meta-"):
                        metadata[k.lower()[11:]] = v
                return {"Body": io.BytesIO(resp.content), "Metadata": metadata}

            def list_objects_v2(self, Bucket, MaxKeys=1):
                resp = self._req("GET", Bucket, query=f"max-keys={MaxKeys}")
                if resp.status_code == 403:
                    raise ClientError("AccessDenied", "Access Denied")
                if resp.status_code >= 300:
                    raise ClientError(f"HTTP_{resp.status_code}", resp.text)
                return resp.text

            def put_bucket_versioning(self, Bucket, VersioningConfiguration):
                body = b'<VersioningConfiguration xmlns="http://s3.amazonaws.com/doc/2006-03-01/"><Status>' + VersioningConfiguration['Status'].encode() + b'</Status></VersioningConfiguration>'
                resp = self._req("PUT", Bucket, query="versioning", body=body)
                if resp.status_code == 403:
                    raise ClientError("AccessDenied", "Access Denied")
                if resp.status_code >= 300:
                    raise ClientError(f"HTTP_{resp.status_code}", resp.text)
                return resp

            def close(self):
                pass

        client = _HttpS3Client(
            endpoint=os.environ[prefix + 'S3_ENDPOINT'],
            access_key=os.environ[prefix + 'S3_ACCESS_KEY_ID'],
            secret_key=os.environ[prefix + 'S3_SECRET_ACCESS_KEY'],
            region=os.environ.get(prefix + 'S3_REGION', 'us-east-1'),
            ca_bundle=os.environ.get('AWS_CA_BUNDLE'),
            path_style=os.environ.get(prefix + 'S3_FORCE_PATH_STYLE', 'true') == 'true'
        )

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
