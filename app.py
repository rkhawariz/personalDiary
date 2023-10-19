import os
from os.path import join, dirname
from dotenv import load_dotenv

from flask import Flask, render_template, jsonify, request
import certifi
ca = certifi.where()
from pymongo import MongoClient
from datetime import datetime

# menghubungkan file agar app.py dapat mengakses variable di file . env
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME =  os.environ.get("DB_NAME")


client = MongoClient(MONGODB_URI, tlsCAFile=ca)
db = client[DB_NAME]
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

# mengaktifkan fungsi show_diary() saat client melakukan ajax request dengan methods GET pada url /diary.
@app.route('/diary', methods=['GET'])
def show_diary():
    # mengambil data dari db, collection diary untuk dimasukkan ke dalam variable. data dalam variable dimasukkan ke dalam Object articles json
    articles = list(db.diary.find({},{'_id': False}))
    return jsonify({'articles': articles})

# mengaktifkan fungsi save_diary() saat client melakukan ajax request dengan methods GET pada url /diary.
@app.route('/diary', methods=['POST'])
def save_diary():
    # mengambil nilai yang ada pada variable tertentu yang sudah disimpan pada sisi client
    title_receive = request.form.get('title_give')
    content_receive = request.form.get('content_give')

    # variable untuk menampung data waktu pada saat ini
    today = datetime.now()
    mytime = today.strftime('%Y-%m-%d-%H-%M-%S')

    # variable untuk menampung nama file yang diinput oleh user, kemudian menggantinya dengan nama yang sudah kita tentukan
    file = request.files['file_give']
    # mengambil nilai dengan index paling akhir dari nama file yang diinput user
    extension = file.filename.split('.')[-1]
    file_name = f'static/post/post-{mytime}.{extension}'
    file.save(file_name)

    profile = request.files['profile_give']
    extension = profile.filename.split('.')[-1]
    profile_name = f'static/profile/profile-{mytime}.{extension}'
    profile.save(profile_name)

    time = today.strftime('%Y.%m.%d')

    # variabel untuk menampung data yang disusun dengan key value pair dictionary python yang berisi value yang sudah tersimpan pada masing masing variable
    doc = {
        'file': file_name,
        'profile': profile_name,
        'title': title_receive,
        'content': content_receive,
        'time': time,
    }
    db.diary.insert_one(doc)
    return jsonify({'msg': 'data tersimpan!'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)