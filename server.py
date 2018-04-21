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
    if request.content_type == 'application/json':
        try:
            data = request.get_json()
            print("data recieved : {}".format(data))
            dest_number = data.get('destination')

            if dest_number:
                call_result = originate_call(dest_number)
                status = call_result.pop('status')
                response = app.response_class(
                    response = json.dumps(call_result),
                    status = status,
                    mimetype='application/json',
                )
            else:
                # if destination number is not provided the ask to put in request Json
                message = 'Please provide destination number to initiate the call , eg : {"destination" : "1001"}'
                status = 400
                return make_error(status, message)
            return response

        except Exception as e:
            message = "No Data in request found!!!"
            status = 400
            return make_error(status, message)

    else:
        # if destination number is not provided the ask to put in request Json
        message = "Unsupported Media Type, content Type should be application/json"
        status = 415
        return make_error(status, message)

def make_error(status, message):
    response = app.response_class(
                response = json.dumps({'error':message}),
                status = status,
                mimetype='application/json',
    )
    return response

if __name__ == "__main__":
    app.run(host= '0.0.0.0', port=8000)

