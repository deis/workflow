from django.core.management.base import BaseCommand
from django.conf import settings
import django.db
import sys


class Command(BaseCommand):
    """Management command for healthchecks"""
    def handle(self, *args, **options):
        """Ensure DB and other things are alive"""
        print("Checking if database is alive")
        try:
            django.db.connection.cursor()
            print("Database is alive!")
        except Exception as e:
            print("There was a problem connecting to the database")
            if settings.DEBUG:
                print(str(e))

            sys.exit(1)
