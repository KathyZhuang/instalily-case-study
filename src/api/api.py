from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["http://127.0.0.1:5000", "http://localhost:3000"])

from backend_url_selector import extract_url_from_page
from backend_test import backend_test_llm

@app.route('/api', methods=['POST', 'GET'])
def get_question_from_frontend():
    if request.method == 'POST':
        data = request.get_json() # retrieve the data sent from JavaScript 
        question = data['value']
        answer = get_answer_from_llm(question)
        data = {"value": answer}
        return jsonify(data)
    data = {"value": "Nothing"}
    return jsonify(data)

def get_answer_from_llm(question):
    # call the llm function to get an answer
    answer = backend_test_llm(question)
    return "answer: " + answer

if __name__ == '__main__': 
    app.run(host='localhost', port=5000, debug=True) 
