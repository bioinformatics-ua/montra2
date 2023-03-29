
from fingerprint.models import Fingerprint

from questionnaire.models import Questionnaire
from fingerprint.models import Fingerprint, FingerprintSubscription
from developer.models import Plugin, PluginVersion, PluginFingeprint, VersionDep
from accounts.models import Profile, EmifProfile
from docs_manager.models import FingerprintDocuments
from docs_manager.views import list_fingerprint_files_aux, upload_document_aux


from population_characteristics.models import *

from achilles.models import *

# Jerboa 


jerboas = Characteristic.objects.all()

_PluginHash = '1eba2bf94acdb6353e6c3950094092de'


for j in jerboas:
    try: 
        PluginFingeprint.create(plugin_hash=_PluginHash, 
            fingerprint_hash=j.fingerprint_id, boolean='false')
    except: 
        print("Not found Jerboa %s" % j.fingerprint_id )


# Achilles 
_PluginHash = 'achilles'

achilles = Datasource.objects.all()

for a in achilles:
    try: 
        PluginFingeprint.create(plugin_hash=_PluginHash, 
            fingerprint_hash=j.fingerprint_id, boolean='false')
    except: 
        print("Not found Achilles %s" % j.fingerprint_id )


