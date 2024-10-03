import time

from django.conf import settings
import subprocess
from django.core.management import call_command
from django.core.management.base import BaseCommand

from watchfiles import watch
from watchfiles import run_process

def foobar():
    subprocess.run(['python', 'manage.py', 'collectstatic', '--noinput'])

class Command(BaseCommand):
    help = "Automatically calls collectstatic when the staticfiles get modified."

    def handle(self, *args, **options):
        print('WATCH_STATIC: Static file watchdog started.')
        run_process(settings.STATIC_URL, target=foobar)