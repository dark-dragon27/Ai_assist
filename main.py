from flask import Flask, render_template, request
from bardapi import Bard
from gtts import gTTS
from langdetect import detect
import time
import os
import firebase
import firebase_admin
from firebase_admin import credentials, db

cred = credentials.Certificate('firebase.json')

firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://ai-assist-92751-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

ref = db.reference('/Search-History')

app = Flask(__name__)

# Set your bard API key here
token = '' 

bard = Bard(token=token)
short_prompt = "Answer very shortly"

ans = None


@app.route('/', methods=['GET', 'POST'])
def search():
    global ans
    result = None
    audio_url = None
    if request.method == 'POST':
        search_value = request.form['search']
        question = search_value + " " + short_prompt
        ans = bard.get_answer(question)['content']
        result = f"{ans}!"
        lang = detect_language(ans)
        audio_url = generate_audio(ans, lang)
        database_update(search_value, ans)
    return render_template('index.html', result=result, audio_url=audio_url)


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
