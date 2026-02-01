import boto3
from botocore.client import Config
from botocore.exceptions import ClientError


class S3Client:
    def __init__(self, endpoint, access_key, secret_key, bucket):
        """
        Инициализация клиента для работы с S3-совместимым хранилищем.
        """
        self.bucket = bucket

        self.s3 = boto3.client(
            's3',
            endpoint_url=endpoint,            # URL S3-хранилища (Selectel / MinIO / Yandex)
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            config=Config(signature_version='s3v4'),
            region_name="us-east-1"
        )

    # ==========================
    # Базовые методы (пример)
    # ==========================

    def upload(self, file_path, object_name):
        """
        Загружает файл в бакет.
        """
        self.s3.upload_file(file_path, self.bucket, object_name)
        print(f"Загружено: {object_name}")

    def download(self, object_name, save_path):
        """
        Скачивает объект из S3.
        """
        self.s3.download_file(self.bucket, object_name, save_path)
        print(f"Скачано: {object_name}")

    # ==========================
    # Методы из задания
    # ==========================

    def list_files(self):
        """
        Возвращает список всех объектов в бакете.
        """
        response = self.s3.list_objects_v2(Bucket=self.bucket)
        if "Contents" not in response:
            return []

        return [obj["Key"] for obj in response["Contents"]]

    def file_exists(self, object_name):
        """
        Проверяет существование объекта в бакете. Возвращает True/False.
        """
        try:
            self.s3.head_object(Bucket=self.bucket, Key=object_name)
            return True
        except ClientError:
            return False
