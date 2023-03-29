# -*- coding: utf-8 -*-
# Copyright (C) 2014 Universidade de Aveiro, DETI/IEETA, Bioinformatics Group - http://bioinformatics.ua.pt/
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
from Bio import Entrez
import json

import time

from emif.settings import PUBMED_EMAIL, pubmed_feed_collection

from pymongo.errors import DuplicateKeyError

from fingerprint.listings import get_databases_process_results
from searchengine.search_indexes import CoreEngine

from community.models import Community

from tag.models import Tag

from fingerprint.models import Answer

class PubMedFeed:
    def __init__(self, rows=9999, start=0, retmax=20):
        self.rows = rows
        self.start = start
        self.retmax=retmax

    def index_communities(self):
        # this is an optional alternative to index_dbs, as with this we are only indexing the community tags, instead of trying to guess from the databases. This should gibe better results
        comms = Community.objects.all()

        pubmed_feed_collection.remove()

        for comm in comms:

            comm_query = comm.query
            if len(comm_query) != 0:
                self.__index_db_articles(comm.name, comm_query, comm.slug)
                time.sleep(0.6)
                continue

            tags = comm.tags.all()

            if tags.count() > 0:
                for tag in tags:
                    self.__index_db_articles(comm.name, tag.slug, comm.slug)
                    time.sleep(0.6)

        for name in Answer.objects.filter(question__slug='database_name').values_list('data', flat=True):
            # We insert empty strings for the community arguments since it seems
            # like they're not being used. They are inserted in the database but
            # the template doesn't show them.
            self.__index_db_articles('', name, '')
            time.sleep(0.6)

    def index_dbs(self):
        # solr is the easiest place to get this, since it is already trying to normalize location, which is not yet being retried properly
        # always from the same field

        c = CoreEngine()

        # We should only consider production ready databases, not drafts draft_t:false

        results = c.search_fingerprint('*:*', rows=self.rows, start=self.start, fq='draft_t:"False"')

        list_databases = get_databases_process_results(results)
        db = None

        for database in list_databases:
            if database.scien_name and len(database.scien_name) > 0:
                clean_name = database.scien_name.lower().replace('dr.', '').replace('prof.', '')
                db = '"%s" AND %s' % (database.name, clean_name)
            elif database.location and len(database.location) > 0:
                db = '"%s" "%s"' % (database.name, database.location.split('\n')[0])

            self.__index_db_articles(database.id, db, database.id)
            time.sleep(0.5)

    def __index_db_articles(self, db_hash, term, slug):
        Entrez.email = PUBMED_EMAIL

        handle = Entrez.esearch(db="pubmed", term=term, retmax=self.retmax)
        record = Entrez.read(handle)
        idlist = record["IdList"]
        # well, cant use json, is not supported :\
        print "\n-- Processing for %s\nHash: %s\nNumber of results: %d" % (db_hash, term, len(idlist))

        if len(idlist) > 0:
            art_handle = Entrez.efetch(db='pubmed', id=idlist, retmode='xml')
            art_record = Entrez.read(art_handle)['PubmedArticle']

            if len(art_record) > 0:
                for article in art_record:
                    citation = article['MedlineCitation']
                    article = citation['Article']
                    journal = article['Journal']
                    date_tmp = journal["JournalIssue"]["PubDate"],

                    if isinstance(date_tmp, tuple):
                        date_tmp = date_tmp[0]
                    date = ''
                    if 'MedlineDate' in date_tmp:
                        date = date_tmp['MedlineDate']
                    elif 'Day' in date_tmp:
                        date = ( "%s/%s/%s" % (date_tmp['Year'], date_tmp['Month'], date_tmp['Day']))

                    elif 'Month' in date_tmp:
                        date = ( "%s/%s" % (date_tmp['Year'], date_tmp['Month']))

                    elif 'Year' in date_tmp:
                        date = "%s" % date_tmp['Year']
                    else:
                        #print date_tmp
                        raise Exception('Cannot understand the date')
                    #pubmed_feed_collection.insert(

                    abstract = ''
                    try:
                        for phrase in article['Abstract']['AbstractText']:
                            try:
                                abstract += '%s: %s \n' % (phrase.attributes['Label'], str(phrase))
                            except:
                                abstract += '%s\n' % str(phrase)
                    except:
                        print int(str(citation['PMID']))

                    authors = []

                    try:
                        temp_authors = article["AuthorList"]

                        for author in temp_authors:
                            authors.append("%s %s." % (author["LastName"], author["Initials"]) )
                    except Exception, e:
                        pass

                    try:
                        volume = journal["JournalIssue"]["Volume"]
                    except KeyError:
                        volume = ''

                    if 'Pagination' in article:
                        page = article["Pagination"]["MedlinePgn"]
                    else:
                        page = '-1'

                    try:
                        pubmed_feed_collection.insert({
                                'db_hash': db_hash,
                                'pmid': int(str(citation['PMID'])),
                                'title': article['ArticleTitle'],
                                'journal': journal['Title'],
                                'volume': volume,
                                'page': page,
                                #'abstract': abstract,
                                'authors': authors,
                                'pub_date': date,
                                'term': term,
                                'slug': slug
                            })
                    except DuplicateKeyError:
                        print 'Found an article already included on the feed, moving to next database'
                        return

            # Entrez guidelines state we should not do more than 3 requests per seconds, otherwise we risk gettings blocked.

            art_handle.close()
        handle.close()
