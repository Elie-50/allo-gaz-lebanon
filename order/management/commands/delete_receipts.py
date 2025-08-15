from django.core.management.base import BaseCommand
from django.db import transaction
from google.cloud import storage
from order.models import Receipt
from helpers.util import add_to_system_path

class Command(BaseCommand):
    # add_to_system_path(r"C:\Program Files\MySQL\MySQL Server 8.0\bin")
    help = "Deletes files from GCS and associated Receipt instances"

    def add_arguments(self, parser):
        parser.add_argument('--prefix', type=str, default='media/receipts/', help='Prefix for files in the GCS bucket')
        parser.add_argument('--bucket', type=str, required=True, help='GCS Bucket name')

    def handle(self, *args, **options):
        prefix = options['prefix']
        bucket_name = options['bucket']

        self.stdout.write(f"Starting delete operation for prefix: {prefix}")

        # 1️⃣ Delete files from GCS
        client = storage.Client()
        bucket = client.bucket(bucket_name)

        blobs = list(bucket.list_blobs(prefix=prefix))
        deleted_files_count = 0
        for blob in blobs:
            self.stdout.write(f'Deleting: {blob.name}')
            blob.delete()
            deleted_files_count += 1

        # 2️⃣ Delete associated database records
        with transaction.atomic():
            deleted_records_count, _ = Receipt.objects.all().delete()

        self.stdout.write(self.style.SUCCESS(f'Deleted {deleted_files_count} files from {prefix}'))
        self.stdout.write(self.style.SUCCESS(f'Deleted {deleted_records_count} Receipt instances from the database'))
