from google.cloud import storage

def delete_receipts(bucket_name: str, prefix: str = 'media/receipts/'):
    """Deletes all files under a specific prefix in a GCS bucket."""
    client = storage.Client()
    bucket = client.bucket(bucket_name)

    blobs = bucket.list_blobs(prefix=prefix)
    deleted_count = 0

    for blob in blobs:
        print(f'Deleting: {blob.name}')
        blob.delete()
        deleted_count += 1

    print(f'Deleted {deleted_count} files from {prefix}')
    return deleted_count

if __name__ == '__main__':
    BUCKET_NAME = 'allo-gaz-media-bucket'
    delete_receipts(BUCKET_NAME)
