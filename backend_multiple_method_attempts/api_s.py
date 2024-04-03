from flask import Flask, request, jsonify, Response
import logging
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["http://127.0.0.1:5000", "http://localhost:3000"])

@app.route('/api', methods=['POST', 'GET'])
def my_profile():
    print("request", request)
    if request.method == 'POST':
    # print("json", json.dumps(request))
        data = request.get_json() # retrieve the data sent from JavaScript 
    # data = request.get_json().get("value")
        print("data POST", data)
    data = {"value": "One possible solution is to check the water filter, as a clogged filter can prevent the ice maker from working properly. You may also want to refer to the installation instructions and owner's manual for troubleshooting tips."}
    app.logger.info("input_value" +  data['value'])
    return jsonify(data)

    # return Response(data, mimetype='application/json')
    # jsonify(data) # return the result to JavaScript 
    # return { 'value': 'backend value' }
    # response_body = {
    #     "name": "Nagato",
    #     "about" :"Hello! I'm a full stack developer that loves python and javascript"
    # }
    # print("response_body",response_body)
    # return response_body
# def predict():
#     return {'accuracy': 100}
if __name__ == '__main__': 
    app.run(host='127.0.0.1', port=5000, debug=True) 
