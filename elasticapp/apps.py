from django.apps import AppConfig
from elasticsearch_dsl.connections import connections


class ElasticappConfig(AppConfig):
    name = 'elasticapp'

    # Calling this elasticsearch connection while app loading
    def ready(self):
        connections.create_connection()
