from docs_manager.models import Document

from django.conf import settings
import os

PATH_STORE_FILES = settings.MEDIA_ROOT + 'docs/'

docs = Document.objects.all()

for doc in docs:
    doc.path = doc.path.replace('/projects/emif-prod/emif/static/files/', os.path.abspath(PATH_STORE_FILES)+'/')
    doc.save()
