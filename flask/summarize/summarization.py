# Importing the Libraries
import re
import heapq
import bs4 as bs
import matplotlib.pyplot as plt

from nltk.corpus import stopwords
from nltk.probability import FreqDist
from nltk import word_tokenize, sent_tokenize, download, data
from flask_restful import Resource, request
from flask import current_app as app
from werkzeug.utils import secure_filename
from google.cloud import storage
import os

class Summarization(Resource):
    bucket_name = "capstone-summaries"

    def __init__(self):
        super().__init__()
        print("Text Summarization Module\n")
        try:
            data.find('tokenizers/punkt')
        except LookupError:
            download('punkt')

        try:
            data.find('corpora/stopwords')
        except LookupError:
            download('stopwords')

    def upload_blob(self, bucket_name, source_file_name, destination_blob_name):
        """Uploads a file to the bucket."""
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(source_file_name)
 
    def get_blob_url(self, bucket_name, blob_name):
        return f'gs://{bucket_name}/{blob_name}'

    def download_blob(self, bucket_name, source_blob_name, destination_file_name):
        storage_client = storage.Client()
        bucket=storage_client.bucket(bucket_name)
        blob = bucket.blob(source_blob_name)
        blob.download_to_filename(destination_file_name)

    def get(self):
        # download file using gcs_uri
        gcs_uri = request.args.get("gcs_uri")
        # store blob locally
        strSplit = gcs_uri.split("/")
        filename = strSplit[len(strSplit)-1]
        file_path = os.path.join(app.config['UPLOAD_SUMMARIES'], filename)
        self.download_blob(self.bucket_name, filename, file_path)
        # import text file extracted that was downloaded
        text = open(file_path,"r").read() 
        sentenceCount = 5
        # get summarized sentences
        sentences = self.summarize_text(text, sentenceCount)
        return sentences

    def post(self):
        # File parsing
        file = request.files["file"]
        sentenceCount = request.form.get("sentenceCount")
        if(sentenceCount != None):
            sentenceCount = int(sentenceCount)
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_SUMMARIES'], filename)
        file.save(file_path)
        # Reading Data
        text = open(file_path,"r").read() # import text file extracted from audio
        if sentenceCount == None:
            sentenceCount = 3
        sentences = self.summarize_text(text, sentenceCount)

        # upload blob to cloud
        self.upload_blob(self.bucket_name, file_path, filename)

        # get gcs_uri of the audio file (blob) 
        gcs_uri = self.get_blob_url(self.bucket_name, filename)

        response = {
            "gcs_uri": gcs_uri, 
            "sentences": sentences
        }
        return response

    def summarize_text(self, text, sentenceCount):
        # Cleaning Data
        text = re.sub(r'\[[0-9]*\]',' ', text)    
        text = re.sub(r'\s+',' ',text)
        clean_text = text.lower()
        clean_text = re.sub(r'\W',' ',clean_text)
        clean_text = re.sub(r'\d',' ',clean_text)
        clean_text = re.sub(r'\s+',' ',clean_text)

        stop_words = stopwords.words('english')

        tokenized_sentences = sent_tokenize(text)
        tokenized_words = word_tokenize(clean_text)

        # Generating Dictionary for plotting
        word2count = {}

        for word in tokenized_words:
            if word not in stop_words:
                if word not in word2count.keys():
                    word2count[word]=1
                else:
                    word2count[word]+=1

        # Weighted Histogram

        for key in word2count.keys():
            word2count[key]=word2count[key]/max(word2count.values())
        
        # Calculate the score

        sent2score = {}
        for sentence in tokenized_sentences:
            for word in word_tokenize(sentence.lower()):
                if word in word2count.keys():
                    if len(sentence.split(' '))<30:
                        if sentence not in sent2score.keys():
                            sent2score[sentence]=word2count[word]
                        else:
                            sent2score[sentence]+=word2count[word]

        # Top n Sentences

        best_sentences = heapq.nlargest(sentenceCount,sent2score,key=sent2score.get)                    

        return best_sentences
