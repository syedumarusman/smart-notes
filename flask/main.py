from flask import Flask
from flask_restful import Api
from transcribeAudio.googleSpeechToText import LongSpeechToText
from summarize.summarization import Summarization

app = Flask(__name__)
api = Api(app)

api.add_resource(LongSpeechToText, '/transcribe/')
api.add_resource(Summarization, '/summarize/')

if __name__ == '__main__':
    app.run(debug=True)