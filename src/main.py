from transcribeAudio.googleSpeechToText import SpeechToText
from summarize.summarization import Summarization

speechToText = SpeechToText()

response = speechToText.transcribe_gcs("gs://capstone-audio-bucket/sample-custom-audio.wav")

