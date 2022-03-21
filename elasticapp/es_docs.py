from elasticsearch_dsl import Document
from elasticsearch_dsl import Long
from elasticsearch_dsl import Text


class ESProduct(Document):
    name = Text(required=True)
    description = Text()
    price = Long(required=True)

    category = Text(required=True, index="not_analyzed")
    tags = Text(multi=True)

    class Meta:
        doc_type = 'products'
