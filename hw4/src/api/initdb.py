from fastapi import APIRouter
import json, os
from elasticsearch import Elasticsearch

router = APIRouter(tags=["Init Elasticsearch database"])
path = "cve_json.json"
es_url = os.environ.get("ES_URL")
es_token = os.environ.get("ES_TOKEN")
index_name = "cves"

@router.get('/init-db')

def init_database():
    try:    
        with open(path, 'r') as file: #читаю файл, з якого ініціалізовуватимуться дані в бд
            cve_data = json.load(file)

        if not (es_url and es_token): #помилка, якщо креди еластіксерчу не надано
            print("No provided Elasticsearch URL and/or Token")
            return "Error. Uncorrect Elasticsearch credentials"
        
        client = Elasticsearch(es_url, api_key=es_token) #з'єднання з БД

        if not client.indices.exists(index=index_name): #якщо індекса ще не існує, то він створюється
            response = client.indices.create(index = index_name)

            if response.meta.status == 200:
                print("Index created successfully")
            else:
                print("Index creating failed")
                return "Error, creating index failed"
        else:
            print("This index already exists")

        skipped_docs = 0
        successed_docs = 0

        for vuln in cve_data.get("vulnerabilities", []): #перебираю дані в файлі
            cve_id = vuln.get("cveID")
        
            if client.exists(index=index_name, id=cve_id): #якщо документ вже існує, то він скіпається
                print(f"Document {cve_id} already exists, skip")
                skipped_docs += 1
                continue
            else:
                response_creation = client.create(index=index_name, id=cve_id, body=vuln) #якщо документа ще не існує, то він створюється

                if response_creation.get("result") == "created":
                    successed_docs += 1

        return { #вивід кількості доданих і пропущених документів
            "message": "Initialization of Elasticsearch database was successful",
            "details": {
                "documents_added": successed_docs,
                "documents_skipped": skipped_docs,
            }
        }

    except FileNotFoundError: #перехоплення помилки, якщо шлях файлу задано неправильно
        return {"message": f"Error. File for init not found: {path}"}
    except Exception as e: #перехоплення загальних помилок
        return {"message": f"Unexpected error: {str(e)}"}

if __name__ == "__main__":
    init_database()