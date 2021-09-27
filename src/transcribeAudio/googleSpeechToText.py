from google.cloud import speech_v1p1beta1 as speech
from google.protobuf.json_format import MessageToJson, MessageToDict
import io, os, json

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "auth.json"

class SpeechToText:
    # Instantiates a client
    client = speech.SpeechClient()

    def __init__(self):
        super().__init__()
        print("Speech to Text Module\n")

    # transcribes short audio file into text
    def transcribe_short_audio(self):
        # The name of the audio file to transcribe
        file_name = os.path.join(os.path.dirname(__file__),'../../audio-files/sample-audios/59second-audio.wav')

        # Loads the audio into memory
        with io.open(file_name, 'rb') as audio_file:
            content = audio_file.read()
            audio = speech.RecognitionAudio(content=content)

        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=44100,
            language_code='en-US',
            # enable_speaker_diarization=True,
            # diarization_speaker_count=3,
            # enable_word_time_offsets=True,
            audio_channel_count=2,
            # enable_separate_recognition_per_channel=True
        )

        # Detects speech in the short audio file(less than 1 min)
        response = self.client.recognize(config=config, audio=audio)

        compiledResponse = ''
        for result in response.results:
            compiledResponse = compiledResponse+"\n"+result.alternatives[0].transcript

        return compiledResponse

    # transcribes long audio file from cloud (gcs_uri) into text
    def transcribe_gcs(self, gcs_uri: str, speakerCount: int = 2):

        audio = speech.RecognitionAudio(uri=gcs_uri)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            # sample_rate_hertz=44100,
            language_code="en-US",
            enable_word_time_offsets= True,
            enable_automatic_punctuation= True,
            audio_channel_count= 2,
            enable_separate_recognition_per_channel= True,
            # enable_word_confidence=True,
            enable_speaker_diarization= True,
            diarization_speaker_count= speakerCount,
        )

        operation = self.client.long_running_recognize(config=config, audio=audio)

        print('Waiting for operation to complete...')
        response = operation.result(timeout=90)

        result = response.results[-1]

        words_info = result.alternatives[0].words

        sentenceInfo = []
        speaker = words_info[0].speaker_tag
        sentenceNo = 1
        for word_info in enumerate(words_info, 1):
            currentSpeaker = word_info[1].speaker_tag
            currentWord = word_info[1].word
            if(speaker == currentSpeaker):
                key = 'speaker'+str(currentSpeaker)+'_sentence'+str(sentenceNo)
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
                key = 'speaker'+str(currentSpeaker)+'_sentence'+str(sentenceNo)
                speaker = currentSpeaker
                sentenceObj = {}
                sentenceObj[key] = currentWord
                sentenceInfo.append(sentenceObj)

        return sentenceInfo
    # [END speech_transcribe_async_gcs]
