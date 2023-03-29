from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import User



class Datasource(models.Model):
	COMPLETED = 0
	PROCESSING = 1
	NOT_STARTED = 2
	ERROR = 3
	REVERTING = 4
	UNZIP_STATUS = (
		(COMPLETED, 'completed'),
		(PROCESSING, 'processing'),
		(NOT_STARTED, 'not_started'),
		(ERROR, 'error'),
		(REVERTING, 'reverting'),
	)
	fingerprint_id = models.CharField(max_length=255, unique=True, blank=False, null=False)
	datasource_url = models.URLField()
	user = models.ForeignKey(User, unique=False, blank=True, null=True)
	created_date = models.DateTimeField(auto_now_add=True)
	latest_date = models.DateTimeField(auto_now=True)
	progress = models.IntegerField(choices=UNZIP_STATUS, default=NOT_STARTED)
	revision = models.IntegerField(default=0)
	def status(self):
		return Datasource.UNZIP_STATUS[self.progress][1]
	def zip_name(self, path):
		return ('%s%s_%s.zip')%(path, self.fingerprint_id, self.revision)

class DatasourceZip(models.Model):
    fingerprint_id = models.CharField(max_length=255, unique=True, blank=False, null=False)
    total_files = models.IntegerField(default=1)
    extracted_files = models.IntegerField(default=0)
