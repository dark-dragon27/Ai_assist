from flask import Flask, render_template, request
from gtts import gTTS
from langdetect import detect
import time
import os
import openai
import firebase_admin
from firebase_admin import credentials, db

# Set your OpenAI API key here
openai.api_key = '' 

app = Flask(__name__)

short_prompt = "Answer very shortly"

ans = None

cred = credentials.Certificate('firebase.json')

firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://ai-assist-92751-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

ref = db.reference('/Search-History')

@app.route('/', methods=['GET', 'POST'])
def search():
    global ans
    result = None
    audio_url = None
    if request.method == 'POST':
        search_value = request.form['search']
        question = search_value + " " + short_prompt

        # Use the OpenAI API to get the answer
        ans = get_answer_from_gpt(question)
        result = f"{ans}!"
        lang = detect_language(ans)
        audio_url = generate_audio(ans, lang)
        database_update(search_value, ans)
    return render_template('index.html', result=result, audio_url=audio_url)

def get_answer_from_gpt(question):
    response = openai.Completion.create(
        engine="text-davinci-002",  # You can experiment with different engines
        prompt=question,
        max_tokens=150,
        stop=["\n", "!", "."]  # Control the length of the answer
    )
    return response.choices[0].text.strip()

def database_update(search_value, ans):
    currentdateandtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    ref.child(str(currentdateandtime)).set({
        'Search': search_value,
        'Answer': ans
    })
    print("Database Updated + " + currentdateandtime)

def detect_language(text):
    try:
        lang = detect(text)
        return lang
    except:
        print("I don't know this language")
        return None

def generate_audio(text, lang):
    timestamp = str(int(time.time()))
    filename = f'static/speech_{timestamp}.mp3'
    if lang == 'ta':
        tts = gTTS(text, lang='ta')
    else:
        tts = gTTS(text, lang='en')

    tts.save(filename)
    return filename

def delete_audio_files():
    folder = 'static'
    for filename in os.listdir(folder):
        if filename.endswith('.mp3'):
            filepath = os.path.join(folder, filename)
            os.remove(filepath)

delete_audio_files()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
