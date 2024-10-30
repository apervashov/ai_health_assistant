from elasticsearch import Elasticsearch
from transformers import AutoTokenizer, AutoModel
import os
import torch

# Настройки подключения к Elasticsearch Cloud
CLOUD_ID = "My_deployment:ZXVyb3BlLXdlc3Q0LmdjcC5lbGFzdGljLWNsb3VkLmNvbTo0NDMkZjA5OGZlOTllY2VkNDRjNzgzM2Y1ZjZiNjk4NzU5MGMkZjEwNmIzYWEzODYxNDQ2ZGE4YjU1M2RmNjgzNmQ2MmI="  # Замените своим Cloud ID
USERNAME = "elastic"  # Обычно это 'elastic'
PASSWORD = "jBcHF3sxIac7n3ITmylfcZo9"  # Замените своим паролем
INDEX_NAME = "vector_text_documents"  # Название индекса для векторной базы данных

# Инициализация клиента Elasticsearch
es = Elasticsearch(
    cloud_id=CLOUD_ID,
    basic_auth=(USERNAME, PASSWORD)
)

# Подготовка модели для векторизации текста
tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
model = AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')

# Функция для получения векторного представления текста
def get_text_vector(text):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).squeeze().detach().numpy()

# Создание индекса с векторным полем
def create_vector_index():
    if not es.indices.exists(index=INDEX_NAME):
        # Определяем настройки индекса с векторным полем
        index_settings = {
            "mappings": {
                "properties": {
                    "file_name": {"type": "keyword"},
                    "content": {"type": "text"},
                    "content_vector": {
                        "type": "dense_vector",
                        "dims": 384  # Размерность вектора модели
                    }
                }
            }
        }
        es.indices.create(index=INDEX_NAME, body=index_settings)
        print(f"Created index: {INDEX_NAME}")

# Функция для индексирования документа с вектором
def index_document_with_vector(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Получение вектора для текста
    content_vector = get_text_vector(content)

    # Формируем тело документа
    doc = {
        "file_name": os.path.basename(file_path),
        "content": content,
        "content_vector": content_vector.tolist()  # Преобразуем вектор в список
    }

    # Индексирование документа
    response = es.index(index=INDEX_NAME, document=doc)
    print(f"Indexed {file_path} with ID {response['_id']}")

# Функция для обработки всех файлов в директории и индексирования их векторов
def index_all_files_with_vectors(directory_path):
    create_vector_index()
    
    # Проход по всем .txt файлам в папке
    for filename in os.listdir(directory_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(directory_path, filename)
            index_document_with_vector(file_path)

# Укажите путь к папке с текстовыми файлами
directory_path = "C:/Users/1/Documents/GitHub/team-coconuts/datasetTXT"

# Запуск индексации
index_all_files_with_vectors(directory_path)
