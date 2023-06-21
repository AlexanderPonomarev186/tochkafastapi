import logging
import boto3
from botocore.exceptions import ClientError


def create_presigned_url(object_name, expiration=3600):
    """Generate a presigned URL to share an S3 object

    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """

    # Generate a presigned URL for the S3 object
    session = boto3.session.Session()
    s3_client = session.client(
        service_name='s3',
        endpoint_url='https://tochkateststorage.storage.yandexcloud.net',
        aws_access_key_id="YCAJEA8dSV5_-ldxhVO_MRtv5",
        aws_secret_access_key="YCOlMQlCHt98u4V_53yVFTujzV5fsHAGD_LyVLvD"
    )
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': "tochkateststorage",
                                                            'Key': object_name},
                                                    ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response