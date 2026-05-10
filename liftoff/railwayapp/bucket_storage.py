import os
import re
import uuid
from pathlib import Path

import boto3
from botocore.exceptions import ClientError
from django.core.exceptions import ValidationError
import filetype


ALLOWED_MIME_TYPES = {
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'image/jpeg',
    'image/png',
    'text/plain',
}

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


def _get_client():
    return boto3.client(
        's3',
        endpoint_url=os.environ['BUCKET_ENDPOINT_URL'],
        aws_access_key_id=os.environ['BUCKET_ACCESS_KEY_ID'],
        aws_secret_access_key=os.environ['BUCKET_SECRET_ACCESS_KEY'],
        region_name=os.environ.get('BUCKET_REGION', 'auto'),
    )


def _bucket_name():
    return os.environ['BUCKET_NAME']


def validate_upload(file_obj):
    if file_obj.size > MAX_FILE_SIZE:
        raise ValidationError("File exceeds the 50 MB size limit.")

    header = file_obj.read(2048)
    file_obj.seek(0)
    kind = filetype.guess(header)

    if kind is None:
        ext = Path(file_obj.name).suffix.lower()
        if ext == '.txt':
            return 'text/plain'
        raise ValidationError(
            "File type could not be detected or is not permitted. "
            "Allowed: PDF, Word, JPEG, PNG, TXT."
        )

    if kind.mime not in ALLOWED_MIME_TYPES:
        raise ValidationError(
            f"File type '{kind.mime}' is not permitted. "
            "Allowed: PDF, Word, JPEG, PNG, TXT."
        )
    return kind.mime


def upload_file(staff_member, file_obj):
    mime_type = validate_upload(file_obj)
    ext = Path(file_obj.name).suffix.lower()
    safe_name = re.sub(r'[^a-zA-Z0-9]', '', f"{staff_member.first_name}{staff_member.last_name}").lower()
    folder = f"{safe_name}_{staff_member.pk}"
    safe_filename = re.sub(r'[^a-zA-Z0-9._-]', '_', Path(file_obj.name).stem)
    object_key = f"{folder}/{safe_filename}_{uuid.uuid4()}{ext}"

    client = _get_client()
    client.upload_fileobj(
        file_obj,
        _bucket_name(),
        object_key,
        ExtraArgs={
            'ContentType': mime_type,
            'Metadata': {'staff_id': str(staff_member.pk)},
        },
    )
    return object_key, mime_type


def stream_download(object_key):
    client = _get_client()
    response = client.get_object(Bucket=_bucket_name(), Key=object_key)
    return response['Body'], response['ContentType'], response['ContentLength']


def delete_file(object_key):
    client = _get_client()
    client.delete_object(Bucket=_bucket_name(), Key=object_key)
