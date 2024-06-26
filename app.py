from flask import Flask, render_template,request,flash,redirect ,url_for, session ,make_response
import os
import google.generativeai as genai
import firebase_admin 
import json
from firebase_admin import credentials
from firebase_admin import firestore
from google.cloud.firestore_v1.base_query import FieldFilter


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

userID =  ''
setAI = """ Only asnwer if the question is related to medical,
If the question is not medical-related tell the user that the question is not medical related 
and respond I'm sorry, but I'm not able to answer your question. It does not appear to be medical-related"""


# Landing Page
@app.route('/')
def landing():
  return render_template('landing.html')

# Login Page 
@app.route('/login')
def login():
  return render_template('login.html')

# Signup Page 
@app.route('/signup',methods = ['POST', 'GET'])
def signup():   
  return render_template('signup.html')


# Homepage 
@app.route('/homepage')
def home():
  if session.get('userID') is None:
    return redirect(url_for('login'))
  
  print(session['userID'])
  # setUpAi(setAI)
  doc_ref = db.collection('user_chat_instance').document(session['userID']).collection('chat_rooms')
  data = doc_ref.get()

  user = db.collection('users').document(session['userID'])
  profile = user.get()

  print(user)
  if not data:
      return render_template('index.html',data = {},profile = profile)
  else:
    return render_template('index.html',data = data, profile=profile)

# Login Submit post 
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

    credential = []
    for doc in result:
       credential = doc.to_dict()
    
    if credential['password'] != password:
      flash('Incorrect Password', 'error')
      return redirect(url_for('login'))
    
  session['userID'] = credential['id']
  global userID 
  userID = session['userID']

  return redirect(url_for('home'))


# logout 
@app.route('/logout')
def logout():
    session.pop('userID', None)
    return redirect(url_for('login'))

# logout 
@app.route('/changepassword',methods = ['POST', 'GET'])
def changepassword():
  newpassword = request.json['password']
  db.collection('users').document(userID).update({'password':newpassword})

  return json.dumps({'newPassword':newpassword})
  
  

# Signup submit Post 
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




# Delete Chat Room
@app.route('/chat/delete/<chatRoomID>/', methods=['GET','POST'])
def delete(chatRoomID):
    chatRoom = db.collection('user_chat_instance').document(userID).collection('chat_rooms').document(chatRoomID)
    chatRoom.delete() 
 
    return redirect(url_for('home'))


# Query Model 
def get_AI_response(text,chatRoomID,chatRoomTitle):
    convo.send_message(text)
    responseText = convo.last.text
    convoDetails = {
        'sender': text,
        'response': responseText,
    }

    result = db.collection('user_chat_instance').document(userID).collection('chat_rooms').document(chatRoomID).collection('messages').document()
    result.set(convoDetails)
    titleDef = 'New chat'
    if text.strip(chatRoomTitle) == text.strip(titleDef):
        print('runthis')
        db.collection('user_chat_instance').document(userID).collection('chat_rooms').document(chatRoomID).update({'title':(' '.join(responseText.split()[:3])).replace("*","") + ' . . . .'})

    return json.dumps({'title':(' '.join(responseText.split()[:3])).replace("*","") + ' . . . .','response':responseText,'messageId':result.id})

@app.route('/regenerateResponse',methods=['POST','GET'])
def regenerateResponse():
    sender = 'Regenerate your last reponse'
    messageResponseID = request.json['messageResponseID']
    chatRoomID = request.json['chatRoomID']

    convo.send_message(sender)
    responseText = convo.last.text

    db.collection('user_chat_instance').document(userID).collection('chat_rooms').document(chatRoomID).collection('messages').document(messageResponseID).update({'reponse':responseText})


    return json.dumps({'response':responseText,})



def setUpAi(query):
  convo.send_message(query)
  print(convo.last.text)
  return convo.last.text

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response
  
if __name__ == '__main__':
   app.run() #host='0.0.0.0', port=5000