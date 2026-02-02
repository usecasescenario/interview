from elasticsearch import AsyncElasticsearch


def create_es_client(url: str) -> AsyncElasticsearch:
    return AsyncElasticsearch(hosts=[url])
