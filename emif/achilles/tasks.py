

from __future__ import absolute_import

from celery import shared_task
from celery import task


from emif.settings import *
import os
from . import api, models
from .models import Datasource, DatasourceZip
import zipfile
from __builtin__ import file
from celery.utils.log import get_task_logger
import shutil

logger = get_task_logger(__name__)

achilles_zip_prefixes = ( 'reports/',
						  'reports/conditioneras/',
						  'reports/conditions/',
						  'reports/drugeras/',
						  'reports/drugs/',
						  'reports/observations/',
						  'reports/procedures/',
						  'reports/visits/')

@shared_task(name='achilles.tasks.unzip_file')
def unzip_file(fingerprint_id):
	ds = None
	try:
		ds = Datasource.objects.get(fingerprint_id=fingerprint_id)
		storagepath = os.path.abspath(api.REPORT_PATH+'tmp/'+fingerprint_id+'/')
		finalstoragepath = os.path.abspath(api.REPORT_PATH+fingerprint_id+'/')
		logger.debug(storagepath)
		zippath = ds.zip_name(api.ZIP_PATH)
		logger.debug(zippath)
		if ds.progress == Datasource.ERROR:
			ds.progress = models.Datasource.REVERTING
		else:
			ds.progress = models.Datasource.PROCESSING
		ds.save()
		zds = DatasourceZip.objects.get(fingerprint_id=ds.fingerprint_id)

		if not os.path.exists(storagepath) or not os.path.isdir(storagepath):
			logger.debug('Creating Folders')
			os.makedirs(storagepath)
		if not os.path.exists(finalstoragepath) or not os.path.isdir(finalstoragepath):
			logger.debug('Creating Folders')
			os.makedirs(finalstoragepath)
		try:
			with zipfile.ZipFile(zippath, "r") as zf:
			#	import pdb; pdb.set_trace()
				zds.total_files = 2*len([ x for x in zf.namelist() if x.startswith(achilles_zip_prefixes)]) + countFiles(finalstoragepath)
				zds.extracted_files = 0
				for i, libitem in enumerate([ x for x in zf.namelist() if (x.startswith(achilles_zip_prefixes) and (x.endswith('/') or x.endswith('.json')))]):
					#logger.debug('Processing: [%-25s] | %s' % ('#'*(i*25/len(zf.namelist())), libitem))
					zds.extracted_files +=1
					zds.save()
					if (libitem.endswith('/')):
						pt = os.path.join(storagepath, libitem)
						logger.debug(pt)
						if not os.path.exists(pt) or not os.path.isdir(pt):
							#print 'creating dir:' + pt
							os.makedirs(pt)

						#print 'extracting %s to %s' % (libitem, os.path.join(storagepath, libitem))
						#if libitem in achilles_report_list
					else:
						filecontent = file(os.path.join(storagepath, libitem),'wb').write(zf.read(libitem))
		except:
			# Error on extraction means we have to rollback to previous revision
			logger.debug('exception' + str(e))

			shutil.rmtree(storagepath)

			ds.revision -= 1
			ds.progress = Datasource.ERROR
			ds.save()
			#reschedule task for rollback previous revision
			if ds.revision > 0:
				unzip_file.delay(fingerprint_id)
			# deleting Datasource
			else:
				ds.delete()
				zds.delete()
			return "Error on extraction"

		try:
			rmtree(finalstoragepath, zds)
		except:
			#does not return because who cares about a few extra kBytes ?
			logger.debug("Error deleting old files")

		try:
			copytree(storagepath, finalstoragepath, zds)
		except Exception as e:
			# error on copy means something went terrible wrong and it's best to rollback, just in case
			logger.debug('exception' + str(e))
			shutil.rmtree(storagepath)

			ds.revision -= 1
			ds.progress = Datasource.ERROR
			ds.save()
			#reschedule task for rollback previous revision
			if ds.revision > 0:
				unzip_file.delay(fingerprint_id)
			# deleting Datasource
			else:
				ds.delete()
				zds.delete()

			return "Error on Copy"
		ds.progress = Datasource.COMPLETED
		ds.save()
		shutil.rmtree(storagepath)
		return "Completed"
	except Exception as ex:
		logger.debug('exception' + str(ex))
		ds.progress = Datasource.ERROR
		ds.save()
		return "Error"

def countFiles(directory):
    files = []

    if os.path.isdir(directory):
        for path, dirs, filenames in os.walk(directory):
            files.extend(filenames)

    return len(files)

def rmtree(dir, zds):
	for root, dirs, files in os.walk(dir, topdown=False):
		for name in files:
			os.remove(os.path.join(root, name))
			zds.extracted_files +=1
			zds.save()
		for name in dirs:
			os.rmdir(os.path.join(root, name))
			zds.extracted_files +=1
			zds.save()

def copytree(src, dest, zds):
	numFiles = countFiles(src)
	if numFiles > 0:
		for path, dirs, filenames in os.walk(src):
			for directory in dirs:
				destDir = path.replace(src,dest)
				os.makedirs(os.path.join(destDir, directory))
				zds.extracted_files +=1
				zds.save()
			for sfile in filenames:
				srcFile = os.path.join(path, sfile)
				destFile = os.path.join(path.replace(src, dest), sfile)
				shutil.copy(srcFile, destFile)
				zds.extracted_files +=1
				zds.save()

