from flask import Flask, request, jsonify
from flask_cors import CORS
from model import create_answer, chat_loop

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})


# Эндпоинт для функции create_answer
@app.route('/create-answer', methods=['POST'])
def create_answer_endpoint():
    data = request.json
    user_input = data.get("userInput", "")
    print("Received data from frontend:", data)
    answer = create_answer(data, user_input)
    print(answer)
    return jsonify({"response": answer})


# Эндпоинт для функции chat_loop
@app.route('/chat', methods=['POST'])
def chat_endpoint():
    data = request.json
    message = data.get("message", "")
    context = data.get("context")  # Получаем контекст из запроса
    sources = data.get("sources", [])  # Получаем источники из запроса

    # Пример данных пользователя
    user_data = {
        "age": 30,
        "height": 170,
        "weight": 70,
        "healthGoal": "weight_loss",
        "dietType": "keto",
        "exerciseLevel": "beginner",
        "hydrationGoal": "2_liters"
    }

    # Обрабатываем запрос с использованием chat_loop
    context, sources, response = chat_loop(message, user_data, context, sources)

    # Возвращаем ответ, а также обновленный контекст и источники
    return jsonify({
        "response": response,
        "context": context,
        "sources": sources
    })


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)