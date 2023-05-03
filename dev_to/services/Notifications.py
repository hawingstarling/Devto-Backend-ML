import os
import json
import firebase_admin
from .. import db
from typing import Any
from bson.objectid import ObjectId
from firebase_admin import credentials, messaging

print(os.path.abspath(os.path.join('serviceAccountKey.json')))

# Import json serviceAccountKey
# D:/SAVE.VSCODE/Learn Language Programming/Dev.to/backend/serviceAccountKey.json
with open(os.path.abspath(os.path.join('serviceAccountKey.json')), 'r') as f:
    serviceAccount = json.load(f)   


class Notification:
    def __init__(self):
        firebaseCred = credentials.Certificate(serviceAccount)
        firebaseApp = firebase_admin.initialize_app(firebaseCred)
        
    def SendToToken(self, registrationToken, title, body, data=None) -> Any:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body
            ),
            data=data,
            token=registrationToken
        )
        response = messaging.send(message)
        print(response)
        return response
    
