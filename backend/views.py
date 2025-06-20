from django.views import View
from django.shortcuts import render
import os
import datetime
import subprocess
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from django.conf import settings
from google.cloud import storage
from order.models import BackupDate
from helpers.permissions import IsSuperUser

class BackupDatabaseAPIView(APIView):
    permission_classes = [IsSuperUser]

    def post(self, request):
        # --- Database Settings ---
        db_settings = settings.DATABASES['default']
        db_name = db_settings['NAME']
        db_user = db_settings['USER']
        db_password = db_settings['PASSWORD']
        db_host = db_settings.get('HOST', 'localhost')
        db_port = db_settings.get('PORT', '3306')

        # --- Backup Setup ---
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'backup_{timestamp}.sql'
        backup_file = os.path.join(backup_dir, filename)

        # --- Build mysqldump Command ---
        cmd = [
            'mysqldump',
            f'-u{db_user}',
            f'-p{db_password}',
            db_name
        ]
        if db_host:
            cmd.append(f'-h{db_host}')
        if db_port:
            cmd.append(f'-P{db_port}')

        try:
            # --- Run mysqldump ---
            with open(backup_file, 'w') as f:
                subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, check=True)

            gcs_url = None

            # --- Upload to GCS if enabled ---
            if getattr(settings, 'USE_GCS', False):
                bucket_name = settings.GS_BUCKET_NAME
                destination_blob_name = f'db_backups/{filename}'

                storage_client = storage.Client()
                bucket = storage_client.bucket(bucket_name)
                blob = bucket.blob(destination_blob_name)
                blob.upload_from_filename(backup_file)
                gcs_url = f'gs://{bucket_name}/{destination_blob_name}'

                # --- Clean up old GCS backups ---
                for old_blob in bucket.list_blobs(prefix='db_backups/'):
                    if old_blob.name != destination_blob_name and old_blob.name.endswith('.sql'):
                        old_blob.delete()

            # --- Clean up local backups (except current) ---
            for f in os.listdir(backup_dir):
                path = os.path.join(backup_dir, f)
                if f.endswith('.sql') and path != backup_file:
                    os.remove(path)

            BackupDate.objects.create()

            # Get the current (local) time
            latest_backup = timezone.localtime(timezone.now())
            formatted_time = latest_backup.strftime("%d/%m/%Y %I:%M %p")

            return Response({
                'status': 'success',
                'local_backup': backup_file,
                'gcs_url': gcs_url,
                'latest_backup': formatted_time
            })

        except subprocess.CalledProcessError as e:
            return Response({'status': 'error', 'message': e.stderr.decode()}, status=500)
        except Exception as ex:
            return Response({'status': 'error', 'message': str(ex)}, status=500)

    def get(self, request):
        try:
            latest_backup = BackupDate.objects.latest('created_at')
            # Explicitly convert the datetime to the active timezone
            local_time = timezone.localtime(latest_backup.created_at)
            formatted_time = local_time.strftime("%d/%m/%Y %I:%M %p")

            return Response({
                "status": "success",
                "latest_backup": formatted_time
            })
        except BackupDate.DoesNotExist:
            return Response({
                "status": "error",
                "message": "No backups have been recorded yet."
            }, status=404)

class ReactAppView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "index.html")
    
