from flask import Flask, request, jsonify
app = Flask(__name__)
from flask import json
from app import originate_call


"""
Main Server file run on port 8000
1. Routing
2. Response handling
"""

@app.route("/api/call/", methods = ['POST'])
def api_call():
    """
    API to originate call on given destination number and return the response of call
    Request :
          Header : content-type: application/json
          Body : {"destination":"1000"}

    Response :
         {"mesage": "OK" if call_executed else "Error" }
    """    
    data = request.get_json()
    dest_number = data.get('destination')

    if dest_number:
        call_result = originate_call(dest_number)
        result = {'message': call_result}
        response = app.response_class(
            response = json.dumps(result),
            status = 200,
            mimetype='application/json',
        )
    else:
        # if destination number is not provided the ask to put in request Json
        result = {'message': "Please provide destination number to initiate the call"}
        response = app.response_class(
            response = json.dumps(result),
            status = 400,
            mimetype='application/json',
        )
    return response

if __name__ == "__main__":
    app.run(host= '0.0.0.0', port=8000)

