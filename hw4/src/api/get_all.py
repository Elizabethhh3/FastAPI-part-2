import os
from fastapi import APIRouter
from datetime import datetime, timedelta
from elasticsearch import Elasticsearch, NotFoundError

router = APIRouter(tags=["Last 5 days"])

es_url = os.environ.get("ES_URL")
es_token = os.environ.get("ES_TOKEN")
index_name = "cves"

if not (es_url and es_token): #помилка, якщо креди еластіксерчу не надано
    raise EnvironmentError("No provided Elasticsearch URL and/or Token")
else:
    client = Elasticsearch(es_url, api_key=es_token) #з'єднання з БД

@router.get('/get/all')
def get_cve():
    try:

        current_time = datetime.now().date() #визначаю поточну дату без часу
        last_five_days = current_time - timedelta(days=5)
        
        query = { #умови для даних, які витягую з БД
            "query": {
                "range": {
                    "dateAdded": {
                        "gte": last_five_days.strftime("%Y-%m-%d"), # дата >= минулих 5 днів (від минулих 5 днів)
                        "lte": current_time.strftime("%Y-%m-%d") # дата <= нинішній даті (до сьогодні)
                    }
                }
            },

            "size": 40 #витягувати лише перші 40 записів
        }

        response = client.search(index=index_name, body=query) #пошуковий запит до Elasticsearch

        return [
            doc["_source"] for doc in response.get("hits", {}).get("hits", []) #обробка виводу результатів без лишніх метаданих
        ]
    
    except ValueError:
        return {"error": "value error in data format"}
    except NotFoundError as e:
        return {"error": f"Index not found: {e}"}
    except Exception as e:
        return {f"Unexpected error: {str(e)}"}