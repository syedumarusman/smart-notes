from flask import Flask
from flask_restful import Api
from transcribeAudio.googleSpeechToText import LongSpeechToText
from summarize.summarization import Summarization
from flask_cors import CORS
import os

UPLOAD_AUDIOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "transcribeAudio/input-audios")
UPLOAD_SUMMARIES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "summarize/input-summaries")

app = Flask(__name__)
app.config['UPLOAD_AUDIOS'] = UPLOAD_AUDIOS
app.config['UPLOAD_SUMMARIES'] = UPLOAD_SUMMARIES
CORS(app)
api = Api(app)

api.add_resource(LongSpeechToText, '/transcribe/')
api.add_resource(Summarization, '/summarize/')

if __name__ == '__main__':
    app.run(debug=True)