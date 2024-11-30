import os
from fastapi import APIRouter
from elasticsearch import Elasticsearch, NotFoundError

router = APIRouter(tags=["knownRansomwareCampaignUse"])

es_url = os.environ.get("ES_URL")
es_token = os.environ.get("ES_TOKEN")
index_name = "cves"

if not (es_url and es_token): #помилка, якщо креди еластіксерчу не надано
    raise EnvironmentError("No provided Elasticsearch URL and/or Token")
else:
    client = Elasticsearch(es_url, api_key=es_token) #з'єднання з БД

@router.get('/get/known')
def get_cve():
    try:
        
        query = {
            "query": {
                "term": {
                    "knownRansomwareCampaignUse.keyword": {
                        "value": "Known"
                    }
                }
            },
            "size": 10 #витягувати лише перші 10 записів
        }
        
        response = client.search(index=index_name, body=query) #пошуковий запит до Elasticsearch

        return [
            doc["_source"] for doc in response.get("hits", {}).get("hits", []) #обробка виводу результатів без лишніх метаданих
        ]

    except NotFoundError as e:
        return {"error": f"Index not found: {e}"}
    except ConnectionError as e:
        return {"error": f"Connection error: {str(e)}"}
    except Exception as e:
        return {"error": f"{str(e)}"}