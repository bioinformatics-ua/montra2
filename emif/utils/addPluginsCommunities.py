from community.models import Community, CommunityPlugins
from developer.models import Plugin


communities = {
    'observational': {
        'plugins': ['docs']
    },
    'adcohort': {
        'questionnaires': [53],
        'owners': ['admin'],
        'name': 'AD Cohorts',
        'description': 'Alzheimer\'s Disease Cohorts Cohorts'
    }
}

pgs = list(Plugin.all(type=Plugin.DATABASE))

observational = Community.objects.get(slug='observational')
adcohort = Community.objects.get(slug='adcohort')

observational.show_popchar = False
observational.show_docs = True
observational.save()

def addPgs(comm, pglist):
    i=10
    for pg in pglist:
        i+=1
        CommunityPlugins.objects.create(plugin=pg, community=comm, sortid=i)

addPgs(observational, pgs)

adcohort.show_popchar = True
adcohort.show_docs = True
adcohort.save()

addPgs(adcohort, pgs)

