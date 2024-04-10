from flask import Flask, render_template,request,flash,redirect ,url_for
import os
import google.generativeai as genai
import firebase_admin 
from firebase_admin import credentials
from firebase_admin import firestore
from google.cloud.firestore_v1.base_query import FieldFilter
import re
import json

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SESSION_TYPE'] = 'filesystem'
# Auto apply UI changes 
app.config['TEMPLATES_AUTO_RELOAD'] = True 

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


userID = ''
setAI = """ Only asnwer if the question is related to medical,
If the question is not medical-related tell the user that the question is not medical related 
and respond I'm sorry, but I'm not able to answer your question. It does not appear to be medical-related"""

@app.route('/homepage')
def home():
  setUpAi(setAI)
  print('here')
  print(userID)
  # createChatInstance(userID)
  data = db.collection('user_chat_instance').document(userID).collection('chat_rooms').get()
  return render_template('index.html',data = data)

@app.route('/login')
def login():
  return render_template('login.html')


@app.route('/signup',methods = ['POST', 'GET'])
def signup():
    
  return render_template('signup.html')

@app.route('/login/submit',methods = ['POST', 'GET'])
def loginCheck():
  if request.method == 'POST':
    username = request.form['username']
    password = request.form['password']

    if not (username and password):
      flash('Empty input field', 'error')
      return redirect(url_for('login'))
    
    result = db.collection("users").where(filter=FieldFilter("username", "==", username))
    result = result.get()

    if not result:
      flash('User does not exist.', 'error')
      return redirect(url_for('login'))

    credential =[]
    for doc in result:
       credential = doc.to_dict()
    
    if credential['password'] != password:
      flash('Incorrect Password', 'error')
      return redirect(url_for('login'))
  global userID
  userID = credential['id']
  return redirect(url_for('home'))
  


@app.route('/signup/submit',methods = ['POST', 'GET'])
def signupSubmit():
  if request.method == 'POST':
    email = request.form['email']
    username = request.form['username']
    password = request.form['password']
    passwordConfirm = request.form['passwordConfirm']


    if not (email and username and password and passwordConfirm):
      flash('Empty input field', 'error')
      return redirect(url_for('signup'))
    

    result = db.collection('users').where('email','==',email)
    result = result.get()


    if result:
      flash('Email already taken.', 'error')
      return redirect(url_for('signup'))
    
    if password != passwordConfirm:
      flash('Password does not Match.', 'error')
      return redirect(url_for('signup'))
    
    insertUser = db.collection('users').document()
    insertUser.set({
       'email':email,
       'username':username,
       'password':password,
       'id':insertUser.id
    })
    
  return redirect(url_for('login'))

@app.route('/')
def landing():
  return render_template('landing.html')

# Get List of Chat rooms
@app.route('/get',methods=['POST','GET'])
def chat():
    sender = request.json['query']
    chatRoomTitle= request.json['topicTitle']
    chatRoomID = request.json['chatRoomID']
    return get_AI_response(sender,chatRoomID,chatRoomTitle)

# Get Specific chatroom convertsation
@app.route('/get/topic',methods=['POST','GET'])
def getMessages():
    chatRoomID = request.json['chatRoomID']
    data = db.collection('user_chat_instance').document(userID).collection('chat_rooms').document(chatRoomID).collection('messages').stream()
    messages_list = []
    for doc in data:
        messages_list.append(doc.to_dict())

    return json.dumps(messages_list)

# Get Specific chatroom convertsation
@app.route('/create/chatroom',methods=['POST','GET'])
def createRoom():
    chatDetails = {
        'title': 'New chat',
    } 
    data = db.collection('user_chat_instance').document(userID).collection('chat_rooms').document()
    data.set(chatDetails)

    print(data.id)
    return json.dumps({'id':data.id})


def get_AI_response(text,chatRoomID,chatRoomTitle):
    convo.send_message(text)
    responseText = convo.last.text
    convoDetails = {
        'sender': text,
        'response': responseText,
    }

    db.collection('user_chat_instance').document(userID).collection('chat_rooms').document(chatRoomID).collection('messages').document().set(convoDetails)
    
    titleDef = 'New chat'
    if text.strip(chatRoomTitle) == text.strip(titleDef):
        print('runthis')
        db.collection('user_chat_instance').document(userID).collection('chat_rooms').document(chatRoomID).update({'title':(' '.join(responseText.split()[:3])).replace("*","") + ' . . . .'})

    return json.dumps({'title':(' '.join(responseText.split()[:3])).replace("*","") + ' . . . .','response':responseText})


def setUpAi(query):
  convo.send_message(query)
  print(convo.last.text)
  return convo.last.text
  
  
if __name__ == '__main__':
   app.run()