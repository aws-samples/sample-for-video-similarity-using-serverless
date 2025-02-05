from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth
import opensearchpy
import boto3
import os

# cluster endpoint, for example: my-test-domain.us-east-1.aoss.amazonaws.com
opensearch_host = os.environ.get(
    "OPENSEARCH_HOST", "")
region = os.environ.get("REGION", "us-west-2")
index_name = os.environ.get("INDEX_NAME", "video_similarity")


service = 'aoss'
credentials = boto3.Session().get_credentials()
auth = AWSV4SignerAuth(credentials, region, service)

opensearch_host = opensearch_host.replace("https://", "")

aos_client = OpenSearch(
    hosts=[{'host': opensearch_host, 'port': 443}],
    http_auth=auth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection,
    pool_maxsize=20
)


def create_index_with_knn():
    if aos_client.indices.exists(index_name):
        print(f"index {index_name} already exists")
        return {"index": index_name, "message": "index already exists"}

    index_body = {
        "settings": {
            "index": {
                "knn": True
            }
        },
        "mappings": {
            "properties": {
                "file": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 512
                        }
                    }
                },
                "image": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }},
                "vector": {
                    "type": "knn_vector",
                    "dimension": 1000,
                    "method": {
                        "name": "hnsw",
                        "space_type": "l2",
                        "engine": "nmslib"
                    }
                }
            }
        }
    }

    response = aos_client.indices.create(index_name, body=index_body)
    return response


def bulk_insert_to_opensearch(documents):
    try:
        actions = [
            {
                "_index": index_name,
                "_source": doc
            }
            for doc in documents
        ]

        success, errors = opensearchpy.helpers.bulk(
            aos_client, actions, raise_on_error=False)

        if errors:
            print(f"error number: {len(errors)}")
            for error in errors:
                print(f"error detail: {error}")

        return success, errors

    except Exception as e:
        print(f"error when bulk insert: {str(e)}")
        return 0, [str(e)]


def search_documents(query):
    try:
        response = aos_client.search(
            index=index_name,
            body=query
        )
        return response
    except Exception as e:
        print(f"error when search document: {str(e)}")


def knn_search(vector, size=10):
    search_query = {
        "query": {
            "knn": {
                "vector": {
                    "vector": vector,
                    "k": size
                }
            }
        }
    }
    return search_documents(search_query)
