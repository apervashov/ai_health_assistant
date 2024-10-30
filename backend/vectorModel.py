from elasticsearch import Elasticsearch
from dotenv import load_dotenv
import requests
import json
import os

load_dotenv()

# Load Elasticsearch Cloud connection settings from environment variables
CLOUD_ID = os.getenv("ELASTIC_CLOUD_ID")
USERNAME = os.getenv("ELASTIC_USERNAME")
PASSWORD = os.getenv("ELASTIC_PASSWORD")
INDEX_NAME = os.getenv("ELASTIC_INDEX_NAME", "vector_text_documents")

# Load Mistral API connection settings from environment variables
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
ENDPOINT_URL = os.getenv("MISTRAL_ENDPOINT_URL", "https://api.mistral.ai/v1/chat/completions")
MODEL_NAME = os.getenv("MISTRAL_MODEL_NAME", "mistral-large-latest")

# Initialize Elasticsearch client
es = Elasticsearch(
    cloud_id=CLOUD_ID,
    basic_auth=(USERNAME, PASSWORD)
)

# Function to search the index
def search_documents(query, index_name=INDEX_NAME, size=5):
    search_body = {
        "query": {
            "match": {
                "content": query  # Search in the 'content' field
            }
        },
        "size": size  # Limit the number of returned documents
    }

    response = es.search(index=index_name, body=search_body)
    results = []
    for hit in response['hits']['hits']:
        results.append({
            "id": hit['_id'],
            "file_name": hit['_source']['file_name'],
            "content": hit['_source']['content']
        })

    return results

# Function to call the Mistral API
def generate_answer(prompt):
    headers = {
        'Authorization': f'Bearer {MISTRAL_API_KEY}',
        'Content-Type': 'application/json'
    }

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(ENDPOINT_URL, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        response_data = response.json()
        return response_data['choices'][0]['message']['content']
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return "Sorry, an error occurred while generating the answer."

# Chat loop
if __name__ == "__main__":
    print("Welcome to the chat! Type 'exit' to quit.")
    
    context = None  # Variable to store context between questions
    sources = []     # Variable to store sources for the first question

    while True:
        user_query = input("You: ")  # Prompt for user input
        
        if user_query.lower() == "exit":
            print("Chat ended.")
            break
        
        # Check if context exists (no need to search again if it's a follow-up question)
        if context is None:
            # First query, search in the database
            search_results = search_documents(user_query, size=5)
            
            if search_results:
                max_content_length = 500
                context = "\n".join([doc["content"][:max_content_length] for doc in search_results])
                sources = [f"Source: {doc['file_name']} (ID: {doc['id']})" for doc in search_results]
                
                # Create a prompt for the generative model with the saved context
                prompt = f"User question: {user_query}\n\nInformation from documents:\n{context}\n\nAnswer:"
                
                # Generate the answer via Mistral API
                answer = generate_answer(prompt)
                answer_lines = answer.splitlines()
                formatted_answer = []
                
                # Ensure each answer line is matched with a source
                for i, line in enumerate(answer_lines):
                    if line.strip():
                        source = sources[i % len(sources)]
                        formatted_answer.append(f"{i + 1}) {line} ({source})")

                final_answer = "\n".join(formatted_answer)
            else:
                print("Unfortunately, no relevant documents were found for your query.")
                continue  # Skip to the next iteration if no documents were found
        else:
            print("Using previous context for clarification.")
            # Create a prompt for follow-up questions using the previous context
            prompt = f"User question: {user_query}\n\nContext information:\n{context}\n\nAnswer:"
            # Generate the answer via Mistral API
            answer = generate_answer(prompt)
        
            # Output the answer without formatting sources
            final_answer = answer

        print("Assistant:", final_answer)
