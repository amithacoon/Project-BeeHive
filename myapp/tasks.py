import threading
import time
import os
from django.core.management import call_command
from django.conf import settings

def clear_media_periodically(interval):
    def run():
        while True:
            time.sleep(interval)
            media_dir = settings.MEDIA_ROOT
            if os.path.exists(media_dir) and os.listdir(media_dir):  # Check if the directory exists and is not empty
                call_command('clear_media')

    thread = threading.Thread(target=run)
    thread.daemon = True
    thread.start()
