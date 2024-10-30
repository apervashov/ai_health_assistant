from elasticsearch import Elasticsearch
import os

# Настройки подключения к Elasticsearch Cloud
CLOUD_ID = "My_deployment:ZXVyb3BlLXdlc3Q0LmdjcC5lbGFzdGljLWNsb3VkLmNvbTo0NDMkZjA5OGZlOTllY2VkNDRjNzgzM2Y1ZjZiNjk4NzU5MGMkZjEwNmIzYWEzODYxNDQ2ZGE4YjU1M2RmNjgzNmQ2MmI="  # Cloud ID из вашего Elasticsearch Cloud Console
USERNAME = "elastic"  # Обычно это 'elastic', но зависит от вашей настройки
PASSWORD = "jBcHF3sxIac7n3ITmylfcZo9"  # Пароль к вашему Elasticsearch кластеру
INDEX_NAME = "text_documents"  # Название индекса, в который будем загружать документы

# Инициализация клиента Elasticsearch
es = Elasticsearch(
    cloud_id=CLOUD_ID,
    basic_auth=(USERNAME, PASSWORD)
)

# Функция для индексирования документа в Elasticsearch
def index_document(file_path, index_name=INDEX_NAME):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Формируем тело документа
    doc = {
        "file_name": os.path.basename(file_path),
        "content": content
    }

    # Индексирование документа
    response = es.index(index=index_name, document=doc)
    print(f"Indexed {file_path} with ID {response['_id']}")

# Функция для обработки всех файлов в директории
def index_all_files(directory_path):
    # Проверка, что индекс существует
    if not es.indices.exists(index=INDEX_NAME):
        # Создаем индекс с базовыми настройками
        es.indices.create(index=INDEX_NAME, ignore=400)
        print(f"Created index: {INDEX_NAME}")
    
    # Проход по всем .txt файлам в папке
    for filename in os.listdir(directory_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(directory_path, filename)
            index_document(file_path)

# Укажите путь к папке с текстовыми файлами
directory_path = "datasetTXT"

# Запуск индексации
index_all_files(directory_path)
