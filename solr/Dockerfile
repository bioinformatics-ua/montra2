FROM solr:8.11

COPY confs server/solr/configsets

COPY precreate-cores.sh /docker-entrypoint-initdb.d
