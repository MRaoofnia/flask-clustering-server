#from nltk import
from nltk.stem.snowball import SnowballStemmer
from nltk.stem.wordnet import WordNetLemmatizer
import math

class Article:
    #article no nlp features
    abstract = ""
    title = ""
    context = ""

    #nlp features
    tokens = []
    tf = {}
    tfidf = {}
    vectorlength = 0
    flag = 0

    def todict(self):
        r = {}
        r['title'] = self.title
        r['abstract'] = self.abstract[:70] + "..."
        return r

    def __init__(self, abstract, title):
        self.abstract = abstract
        self.title = title
        self.context = abstract + (title + " ") * 3
        # normalizing, tokenizing, stemming, lemmatizing, and making tf vector
        puncts = '.,()\'"1234567890+-*/_!?;:&%$'
        for sym in puncts: #removing punctuations and numbers
            self.context= self.context.replace(sym,' ')
        self.context = self.context.lower()
        self.tokens = []
        self.tokens = self.context.split(' ') #tokenizing
        stemmer = SnowballStemmer('english')
        lemmatizer = WordNetLemmatizer()
        for token in self.tokens:
            self.tokens[self.tokens.index(token)] = lemmatizer.lemmatize(stemmer.stem(token)) #stemming and lemmatizing
        self.tf = {}
        self.idf = {}
        for token in self.tokens:
            if token in self.tf:
                self.tf[token] += 1
            else:
                self.tf[token] = 1
        size = 0
        for word in self.tf:
            size += (self.tf[word] * self.tf[word])
        self.vectorlength = math.sqrt(size)
        
        