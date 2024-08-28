from datetime import datetime
import uuid
import base64, requests, sys


# Define your Org region https://help.mypurecloud.com/articles/aws-regions-for-genesys-cloud-deployment/
ENVIRONMENT = "USW2"  #eg. USW2

# Define your OAuth client credentials 
CLIENT_ID = ""
CLIENT_SECRET = ""

# Define your Open Messaging IntegrationId here
integrationId = ""

#Fetch Token
def gcAuth(): 

    # Base64 encode the client ID and client secret
    authorization = base64.b64encode(bytes(CLIENT_ID + ":" + CLIENT_SECRET, "ISO-8859-1")).decode("ascii")

    # Prepare for POST /oauth/token request
    request_headers = {
        "Authorization": f"Basic {authorization}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    request_body = {
        "grant_type": "client_credentials"
    }

    # Get token
    response = requests.post(f"https://login.{ENVIRONMENT}/oauth/token", data=request_body, headers=request_headers)

    # Check response
    if response.status_code == 200:
        logger("INFO", "Token request successful")
    else:
        print(f"Failure: { str(response.status_code) } - { response.reason } - CorrelationID - {response.headers.get('inin-correlation-id')}")
        sys.exit(response.status_code)

    # Get JSON response body
    response_json = response.json()
    return response_json


def logger(state, data):
    current_date = datetime.now()
    dateTimeUTC = current_date.strftime('%Y-%m-%dT%H:%M:%SZ')
    print(f'{dateTimeUTC} - {state} -- {data}')
    

def main():
    #GC authentication
    auth = gcAuth()

    active = True

    # Asks user for input to be sent to GC as inbound open message
    while active:
        message = input("Enter your message (enter 'q' to exit program): ")
        if message == "q":
            active = False
        else:
            sendMessage(message, auth)

def sendMessage(message, auth):
    current_date = datetime.now()
    dateTimeUTC = current_date.strftime('%Y-%m-%dT%H:%M:%SZ')
    messageID = uuid.uuid4()
    request_headers = {
        "Authorization": f"{ auth['token_type'] } { auth['access_token']}",
        "Content-Type": "application/json"
    }

    # Request payload for the Open Messaging inbound request, edit as needed based on test requirements 
    # https://developer.genesys.cloud/commdigital/digital/openmessaging/inboundTextMessages

    request_body = {
        "channel": {
            "messageId": str(messageID),
            "from": {
                "nickname": "Open Messaging User",
                "id": "open-message@dummyuser.com",
                "idType": "email",
                "image": "https://externalservice.com/profiles/messaging-user.png",
                "firstName": "Middleware",
                "lastName": "Test Application"
            },
            "time": dateTimeUTC
        },
        "type": "Text",
        "text": message,
        "direction": "Inbound"
    }

    # Send Message to Open Messaging endpoint
    response = requests.post(f"https://api.{ENVIRONMENT}/api/v2/conversations/messages/{integrationId}/inbound/open/message", json=request_body, headers=request_headers)

    # Check response
    if response.status_code == 200 or response.status_code == 202 :
        logger(f"SEND - CorrelationID - {response.headers.get('inin-correlation-id')}", request_body)
    else:
        print(f"Failure: { str(response.status_code) } - { response.reason } - CorrelationID - {response.headers.get('inin-correlation-id')}")
        sys.exit(response.status_code)


if __name__ == "__main__":
    main()
