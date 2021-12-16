from google.cloud import speech_v1p1beta1 as speech, storage
from flask_restful import Resource, request
from flask import current_app as app
from pydub import AudioSegment
from werkzeug.utils import secure_filename
import wave
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "auth.json"

class LongSpeechToText(Resource):
    bucket_name = "capstone-audios"
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "input-audios")

    def __init__(self):
        super().__init__()
        # Instantiates a client
        print("Speech to Text Module\n")

    def upload_blob(self, bucket_name, source_file_name, destination_blob_name):
        """Uploads a file to the bucket."""
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(source_file_name)
    
    def stereo_to_mono(self, audio_file_name):
        sound = AudioSegment.from_wav(audio_file_name)
        sound = sound.set_channels(1)
        sound.export(audio_file_name, format="wav")

    def frame_rate_channel(self, audio_file_name):
        with wave.open(audio_file_name, "rb") as wave_file:
            frame_rate = wave_file.getframerate()
            channels = wave_file.getnchannels()
            return frame_rate,channels

    def get_blob_url(self, bucket_name, blob_name):
        return f'gs://{bucket_name}/{blob_name}'

    def download_blob(self, bucket_name, source_blob_name, destination_file_name):
        storage_client = storage.Client()
        bucket=storage_client.bucket(bucket_name)
        blob = bucket.blob(source_blob_name)
        blob.download_to_filename(destination_file_name)

    def get(self):
        gcs_uri = request.args.get("gcs_uri")
        min_speakers = 1
        max_speakers = 2

        # store blob locally
        strSplit = gcs_uri.split("/")
        filename = strSplit[len(strSplit)-1]
        file_path = os.path.join(app.config['UPLOAD_AUDIOS'], filename)
        self.download_blob(self.bucket_name, filename, file_path)
        frame_rate, channels = self.frame_rate_channel(file_path)

        if channels > 1:
            self.stereo_to_mono(file_path)

        # Initialize speech client
        client = speech.SpeechClient()
        audio = speech.RecognitionAudio(uri=gcs_uri)

        diarization_config = speech.SpeakerDiarizationConfig(
            enable_speaker_diarization=True,
            min_speaker_count=min_speakers,
            max_speaker_count=max_speakers,
        )

        # Setting speech recognition config
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz= frame_rate,
            language_code= 'en-US',
            enable_automatic_punctuation= True,
            diarization_config=diarization_config
            )

        # Detects speech in the audio file
        operation = client.long_running_recognize(config=config, audio=audio)
        response = operation.result(timeout=10000)

        result = response.results[-1]
        words_info = result.alternatives[0].words
        
        sentenceInfo = []
        speaker = words_info[0].speaker_tag
        sentenceNo = 1

        for word_info in enumerate(words_info, 1):
            currentSpeaker = word_info[1].speaker_tag
            currentWord = word_info[1].word
            if(speaker == currentSpeaker):
                key = 'Speaker'+str(currentSpeaker)+'_Sentence'+str(sentenceNo)
                flagList = [i for i,x in enumerate(sentenceInfo) if key in x]
                if len(flagList) > 0:
                    newWord = " " + currentWord
                    sentenceInfo[ flagList[0] ][key] += newWord
                else:
                    sentenceObj = {}
                    sentenceObj[key] = currentWord
                    sentenceInfo.append(sentenceObj)
            else:
                sentenceNo+=1
                key = 'Speaker'+str(currentSpeaker)+'_Sentence'+str(sentenceNo)
                speaker = currentSpeaker
                sentenceObj = {}
                sentenceObj[key] = currentWord
                sentenceInfo.append(sentenceObj)

        response = { 
            "gcs_uri": gcs_uri,
            "transcript": sentenceInfo
        }
        return response



    def post(self):
        file = request.files["file"]
        speakerCount = request.form.get("speakerCount")
        min_speakers = 1
        max_speakers = 2
        if(speakerCount != None):
            min_speakers = int(speakerCount)
            max_speakers = int(speakerCount)
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_AUDIOS'], filename)
        file.save(file_path)
        frame_rate, channels = self.frame_rate_channel(file_path)

        if channels > 1:
            self.stereo_to_mono(file_path)

        # upload blob to cloud
        self.upload_blob(self.bucket_name, file_path, filename)

        # get gcs_uri of the audio file (blob) 
        gcs_uri = self.get_blob_url(self.bucket_name, filename)

        # Initialize speech client
        client = speech.SpeechClient()
        audio = speech.RecognitionAudio(uri=gcs_uri)

        diarization_config = speech.SpeakerDiarizationConfig(
            enable_speaker_diarization=True,
            min_speaker_count=min_speakers,
            max_speaker_count=max_speakers,
        )

        # Setting speech recognition config
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz= frame_rate,
            language_code= 'en-US',
            enable_automatic_punctuation= True,
            diarization_config=diarization_config
            )

        # Detects speech in the audio file
        operation = client.long_running_recognize(config=config, audio=audio)
        response = operation.result(timeout=10000)

        result = response.results[-1]
        words_info = result.alternatives[0].words
        
        sentenceInfo = []
        speaker = words_info[0].speaker_tag
        sentenceNo = 1

        for word_info in enumerate(words_info, 1):
            currentSpeaker = word_info[1].speaker_tag
            currentWord = word_info[1].word
            if(speaker == currentSpeaker):
                key = 'Speaker'+str(currentSpeaker)+'_Sentence'+str(sentenceNo)
                flagList = [i for i,x in enumerate(sentenceInfo) if key in x]
                if len(flagList) > 0:
                    newWord = " " + currentWord
                    sentenceInfo[ flagList[0] ][key] += newWord
                else:
                    sentenceObj = {}
                    sentenceObj[key] = currentWord
                    sentenceInfo.append(sentenceObj)
            else:
                sentenceNo+=1
                key = 'Speaker'+str(currentSpeaker)+'_Sentence'+str(sentenceNo)
                speaker = currentSpeaker
                sentenceObj = {}
                sentenceObj[key] = currentWord
                sentenceInfo.append(sentenceObj)

        response = { 
            "gcs_uri": gcs_uri,
            "transcript": sentenceInfo
        }
        return response
