import re
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
import os
import requests
import json
import logging
from sentence_transformers import SentenceTransformer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv()

# Настройки Elasticsearch
CLOUD_ID = os.getenv("ELASTIC_CLOUD_ID")
USERNAME = os.getenv("ELASTIC_USERNAME")
PASSWORD = os.getenv("ELASTIC_PASSWORD")
INDEX_NAME = os.getenv("ELASTIC_INDEX_NAME", "text_documents")

# Настройки Mistral API
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
ENDPOINT_URL = os.getenv("MISTRAL_ENDPOINT_URL", "https://api.mistral.ai/v1/chat/completions")
MODEL_NAME = os.getenv("MISTRAL_MODEL_NAME", "mistral-large-latest")

# Инициализация клиента Elasticsearch
es = Elasticsearch(
    cloud_id=CLOUD_ID,
    basic_auth=(USERNAME, PASSWORD)
)

# Инициализация модели для векторизации текста
model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')


# Функция для получения векторного представления текста
def get_query_vector(text):
    return model.encode(text).tolist()


# Функция поиска по тексту и вектору
def search_documents(query, vector=None, index_name=INDEX_NAME, size=5):
    if vector:
        search_body = {
            "query": {
                "bool": {
                    "must": [
                        {"exists": {"field": "content_vector"}},
                        {
                            "script_score": {
                                "query": {"match_all": {}},
                                "script": {
                                    "source": "cosineSimilarity(params.query_vector, 'content_vector') + 1.0",
                                    "params": {"query_vector": vector}
                                }
                            }
                        }
                    ]
                }
            },
            "size": size
        }
    else:
        search_body = {
            "query": {
                "match": {"content": query}
            },
            "size": size
        }

    try:
        response = es.search(index=index_name, body=search_body)
        results = []
        for hit in response['hits']['hits']:
            results.append({
                "id": hit['_id'],
                "file_name": hit['_source'].get('file_name', ''),
                "content": hit['_source'].get('content', '')
            })
        return results
    except Exception as e:
        logger.error(f"Ошибка поиска в Elasticsearch: {e}")
        return []


# Функция для оценки результатов
def evaluate_results(results):
    return sum(len(doc["content"]) for doc in results)


# Функция для вызова Mistral API
def generate_answer(prompt):
    headers = {
        'Authorization': f'Bearer {MISTRAL_API_KEY}',
        'Content-Type': 'application/json'
    }
    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}]
    }
    response = requests.post(ENDPOINT_URL, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        response_data = response.json()
        answer_content = response_data['choices'][0]['message']['content']
        cleaned_answer = re.sub(r'[*#]', '', answer_content)
        return cleaned_answer
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return "An error occurred while generating the answer."


# Основная функция чата
# Основная функция чата с обновленным параметризованным подходом
def chat_loop(user_query, user_data, context=None, sources=[]):
    # Если контекста нет, выполняем первый запрос и создаем его
    if context is None:
        search_results = search_documents(user_query, size=5)
        if search_results:
            max_content_length = 500
            context = "\n".join([doc["content"][:max_content_length] for doc in search_results])
            sources = [f"Source: {doc['file_name']} (ID: {doc['id']})" for doc in search_results]
            prompt = f"User question: {user_query}\n\nInformation from documents:\n{context}\n\nAnswer:"
            answer = generate_answer(prompt)
            answer_lines = answer.splitlines()
            formatted_answer = "\n".join(
                [f"{i + 1}) {line} ({sources[i % len(sources)]})" for i, line in enumerate(answer_lines) if line.strip()]
            )
        else:
            return context, sources, "Unfortunately, no relevant documents were found for your query."
    else:
        prompt = f"User question: {user_query}\n\nContext information:\n{context}\n\nAnswer:"
        answer = generate_answer(prompt)
        formatted_answer = answer

    return context, sources, formatted_answer

# Функция для создания ответа с учетом данных пользователя и контекста поиска
def create_answer(data, user_input):
    age = data.get("age", "unknown")
    height = data.get("height", "unknown")
    weight = data.get("weight", "unknown")
    health_goal = data.get("healthGoal", "not specified")
    diet_type = data.get("dietType", "not specified")
    exercise_level = data.get("exerciseLevel", "not specified")
    hydration_goal = data.get("hydrationGoal", "not specified")

    user_profile = (
        f"Age: {age}\n"
        f"Height: {height} cm\n"
        f"Weight: {weight} kg\n"
        f"Health Goal: {health_goal}\n"
        f"Diet Type: {diet_type}\n"
        f"Exercise Level: {exercise_level}\n"
        f"Hydration Goal: {hydration_goal}\n"
    )

    vector = get_query_vector(user_input)
    text_search_results = search_documents(query=user_input, size=5)
    vector_search_results = search_documents(query=user_input, vector=vector, size=5)

    text_score = evaluate_results(text_search_results)
    vector_score = evaluate_results(vector_search_results)

    if text_score >= vector_score:
        best_results = text_search_results
        search_type = "Текстовый поиск"
    else:
        best_results = vector_search_results
        search_type = "Векторный поиск"

    logger.info(f"Выбранный тип поиска: {search_type}")

    context = f"{search_type}:\n" + "\n".join(
        [f"Document {i + 1}: {doc['file_name']}\n> {doc['content'][:200]}..." for i, doc in enumerate(best_results)]
    )
    sources = [f"Source: {doc['file_name']} (ID: {doc['id']})" for doc in best_results]

    prompt = (
        f"User question: {user_input}\n\n"
        f"User profile:\n{user_profile}\n\n"
        f"Information from documents:\n{context}\n\nAnswer:"
    )

    answer = generate_answer(prompt)
    answer_lines = answer.splitlines()

    # Перевірка, чи список sources не порожній перед форматуванням відповіді
    if sources:
        formatted_answer = "\n".join(
            [f"{i + 1}) {line} ({sources[i % len(sources)]})" for i, line in enumerate(answer_lines) if line.strip()]
        )
    else:
        formatted_answer = "\n".join(
            [f"{i + 1}) {line}" for i, line in enumerate(answer_lines) if line.strip()]
        )

    return formatted_answer



# Запуск chat_loop из main