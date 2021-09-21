from google.cloud import speech_v1p1beta1 as speech
from google.protobuf.json_format import MessageToJson, MessageToDict
import io, os, json

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "auth.json"

# Instantiates a client
client = speech.SpeechClient()

# transcribes short audio file into text
def transcribe_short_audio():
    # The name of the audio file to transcribe
    file_name = os.path.join(os.path.dirname(__file__),'audio-files/sample-audios/59second-audio.wav')

    # Loads the audio into memory
    with io.open(file_name, 'rb') as audio_file:
        content = audio_file.read()
        audio = speech.RecognitionAudio(content=content)

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        # sample_rate_hertz=48000,
        sample_rate_hertz=44100,
        language_code='en-US',
        # enable_word_confidence=True,
        # enable_speaker_diarization=True,
        # diarization_speaker_count=3,
        # enable_word_time_offsets=True,
        # enable_automatic_punctuation=True,
        # audio_channel_count=2,
        # enable_separate_recognition_per_channel=True
    )

    # Detects speech in the short audio file(less than 1 min)
    response = client.recognize(config=config, audio=audio)

    # Detects speech in the short audio file(more than 1 min)
    # response = client.long_running_recognize(config=config, audio=audio)

    for result in response.results:
        print(result.alternatives[0].transcript)

# transcribes long audio file from cloud (gcs_uri) into text
def transcribe_gcs(gcs_uri):
    client = speech.SpeechClient()

    audio = speech.RecognitionAudio(uri=gcs_uri)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        # sample_rate_hertz=44100,
        language_code="en-US",
        enable_word_time_offsets=True,
        enable_automatic_punctuation=True,
        audio_channel_count=2,
        enable_separate_recognition_per_channel=True,
        # enable_word_confidence=True,
        enable_speaker_diarization=True,
        diarization_speaker_count=3,
    )

    operation = client.long_running_recognize(config=config, audio=audio)

    print('Waiting for operation to complete...')
    response = operation.result(timeout=90)

    result = response.results[-1]

    words_info = result.alternatives[0].words

    # Printing out the output:
    for word_info in words_info:
        print(u"word: '{}', speaker_tag: {}".format(word_info.word, word_info.speaker_tag))

    # for result in response.results:
    #     print(result.alternatives[0].transcript)
    # response = MessageToJson(response)
    # response = MessageToDict(response)
    # print(response)
    # with open('data.json', 'w') as outfile:
    #     json.dump(response, outfile)

# [END speech_transcribe_async_gcs]

transcribe_gcs("gs://capstone-audio-bucket/sample-custom-audio.wav")