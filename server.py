from flask import Flask, request, jsonify
from client import logger, gcAuth, ENVIRONMENT, CLIENT_ID, CLIENT_SECRET, integrationId
import json
from datetime import datetime
import requests

app = Flask(__name__)
auth = gcAuth() #Get Auth token

@app.route('/webhook', methods=['POST']) # Defines the path for the webhook request eg. https://server.github.dev/webhook
def webhook():
    # Get the JSON data sent in the POST request
    data = request.get_json()
    type = data.get('type', 'Field Not Found')


    if type == "Text":
        logger("RECV Text", data)
        logger("RECV Text - Raw Message", data.get('text', "Field Not Found"))
        sendReceipt(data.get('id'), auth)
    
    else:
        logger("RECV Event", data)


    # Respond with a success message
    return jsonify({"status": "success"}), 200

#Sends receipt message to GC from incoming WebHook 
def sendReceipt(messageId, auth):
    current_date = datetime.now()
    dateTimeUTC = current_date.strftime('%Y-%m-%dT%H:%M:%SZ')
    request_headers = {
        "Authorization": f"{ auth['token_type'] } { auth['access_token']}",
        "Content-Type": "application/json"
    }

    request_body = {
        "id": messageId,
        "channel": {
            "to": {
            "id": "open-message@dummyuser.com",
            "idType": "email"
            },
            "time": dateTimeUTC
        },
        "status": "Delivered",
        "direction": "Outbound",
        "isFinalReceipt": True
    }

    # Send Message to Open Messaging endpoint
    response = requests.post(f"https://api.{ENVIRONMENT}/api/v2/conversations/messages/{integrationId}/inbound/open/receipt", json=request_body, headers=request_headers)

    # Check response
    if response.status_code == 200 or response.status_code == 202 :
        logger(f"SEND RECEIPT - CorrelationID - {response.headers.get('inin-correlation-id')}", request_body)
    else:
        print(f"Failure: { str(response.status_code) } - { response.reason } - CorrelationID - {response.headers.get('inin-correlation-id')}")
        sys.exit(response.status_code)

app.run()