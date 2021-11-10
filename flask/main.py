from flask import Flask
from flask_restful import Api
from transcribeAudio.googleSpeechToText import LongSpeechToText
from summarize.summarization import Summarization
from flask_cors import CORS
import os

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "transcribeAudio/input-audios")

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
CORS(app)
api = Api(app)

api.add_resource(LongSpeechToText, '/transcribe/')
api.add_resource(Summarization, '/summarize/')

if __name__ == '__main__':
    app.run(debug=True)