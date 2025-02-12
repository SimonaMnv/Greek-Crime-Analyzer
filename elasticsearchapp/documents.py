from django_elasticsearch_dsl import Index, fields
from django_elasticsearch_dsl.documents import Document
from api.models.article_model import ArticleOfInterest
from elasticsearch_dsl.connections import connections
from django_elasticsearch_dsl.registries import registry
from elasticsearchapp.custom_analyzers import greek_analyzer
from elasticsearchapp.custom_analyzers import greek_simple_analyzer

connections.create_connection()

article_index = Index('articles')

article_index.settings(
    number_of_shards=1,
    number_of_replicas=0
)


@registry.register_document
@article_index.document
class ArticleDocument(Document):
    title = fields.TextField(
        analyzer=greek_analyzer,  # main analyzer
        fields={'simple_analyzer': fields.TextField(analyzer=greek_simple_analyzer)}
    )
    date = fields.DateField()
    body = fields.TextField(
        analyzer=greek_analyzer,
        fields={'simple_analyzer': fields.TextField(analyzer=greek_simple_analyzer)}
    )
    tags = fields.TextField()
    author = fields.TextField()
    link = fields.TextField()
    type = fields.TextField()
    scope = fields.TextField()

    crime_analysis = fields.NestedField(
        attr='article_analysis',
        properties={
            'acts_committed': fields.TextField(),
            'location_of_crime': fields.TextField(),
            'ages_involved': fields.TextField(),
            'time_of_crime': fields.TextField(),
            'victim_gender': fields.TextField(),
            'criminal_status': fields.TextField(),
            'drug_type': fields.TextField(),
        }
    )

    class Django:
        model = ArticleOfInterest

# sync django / elastic:
# 1. create elasticsearchapp indexes: python manage.py elasticsearchapp --create -f
# 2. sync data: python manage.py elasticsearchapp --populate -f

# TODO: python manage.py search_index --rebuild
# TODO: in kibana change the limits
