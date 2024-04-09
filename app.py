from flask import Flask, render_template,request
import google.generativeai as genai
import firebase_admin 
from firebase_admin import credentials
from firebase_admin import firestore
import re

app = Flask(__name__)

# For firebase 
cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

genai.configure(api_key="AIzaSyDgf7wDgi2Imz2mgmFzsn9Hnd6Uob8dv1Y")
#Set up the model
generation_config = {
  "temperature": 0.9,
  "top_p": 1,
  "top_k": 1,
  "max_output_tokens": 2048,
}

safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_NONE",
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_NONE",
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_NONE",
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_NONE",
  },
]

model = genai.GenerativeModel(model_name="gemini-1.0-pro",
                              generation_config=generation_config,
                              safety_settings=safety_settings)

convo = model.start_chat(history=[
])


userID = '1'
setAI = """ Only asnwer if the question is related to medical: 
Provide a medically accurate answer based on your knowledge and research. Ensure the information is evidence-based and up-to-date.
If the question is not medical-related:**
Notify the user that the question is not medical related"""

@app.route('/')
def home():
  # createChatInstance(userID)
  # get_AI_response(setAI)
  data = db.collection('user_chat_instance').document(userID).collection('chat_rooms').get()

  return render_template('index.html',data = data)

@app.route('/get',methods=['POST','GET'])
def chat():
    sender = request.json['query']
    chatRoomID = request.json['chatRoomID']
    return get_AI_response(sender,chatRoomID)

def get_AI_response(text,chatRoomID):
    convo.send_message(text)
    responseText = convo.last.text
    
    return responseText

def createChatInstance(userID):
  db.collection('user_chat_instance').document(userID).set({'userID':userID})


def createChatRoom(title):
    chatDetails = {
        'title': title,
    } 
    db.collection('user_chat_instance').document(userID).collection('chat_rooms').document().set(chatDetails)
  
if __name__ == '__main__':
   app.run()