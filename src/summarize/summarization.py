# Importing the Libraries
import re
import heapq
import bs4 as bs
import matplotlib.pyplot as plt

from nltk.corpus import stopwords
from nltk.probability import FreqDist
from nltk import word_tokenize, sent_tokenize, download
from flask_restful import Resource

class Summarization(Resource):
    def __init__(self):
        super().__init__()
        print("Text Summarization Module\n")
        download('stopwords')
        download('punkt')

    def get(self, text: str, sentenceCount: int = 5):
        # Cleaning Data
        text = re.sub(r'\[[0-9]*\]',' ',text)    
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


        # Separating Words and it's count for plotting

        count=list(word2count.values())
        words=list(word2count.keys())

        # Plotting Unprocessed Data with frequency

        plt.figure(1, figsize=(20, 20))
        fdist = FreqDist(tokenized_words)
        fdist.plot(show=False)
        plt.savefig('data-frequency.png', bbox_inches='tight')
        plt.close()

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

        # Plotting bar plot after processing
        plt.figure(1, figsize=(20, 20))
        plt.bar(words, count, width=0.7)
        plt.xticks(rotation=90)
        plt.title('Words Count Plot')
        plt.savefig('word-count.png', bbox_inches='tight')
        plt.close()

        return best_sentences