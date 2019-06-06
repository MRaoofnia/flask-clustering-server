from flask import Flask
import multiprocessing
from Article import Article
from XMLReader import Reader
import math
import json
import sys


#app definition
app = Flask(__name__)


#global variables definition
counter = 0


#algorithms
def max(sims):
    max = 0
    ij = {'i':0, 'j':0}
    for i in range(len(sims)):
        for j in range(i):
            if sims[i][j] > max:
                max = sims[i][j]
                ij = {'i':i, 'j':j}
    return ij

def process_status(id,stat):
    with open("%d.stat"%id, 'w') as status:
        status.write(stat)


def clustering(inurl, inthreshold, id):
    process_status(id,'reading articles.')
    reader = Reader(inurl) #Reader reads all XML documents from 'jad' and returns an array of articles
    articles = reader.articles #Article class tokenizes and lemmatizes tokens itself
    
    process_status(id,"calculating idfs...")
    wordsdf = {}
    for article in articles: #finding dfs
        tfmap = {}
        tfmap = article.tf
        for word in tfmap:
            if word in wordsdf:
                wordsdf[word] += 1
            else:
                wordsdf[word] = 1
    
    wordsidf = {}
    for word in wordsdf: #finding idfs
        wordsidf[word] = math.log(len(articles)/wordsdf[word], 2)
    
    for article in articles: #setting tfidfs
        for word in article.tf:
            article.tfidf[word] = article.tf[word] * wordsidf[word]
    
    process_status(id,"calculating cosine similarities...")
    #now clustering -----------------------------------------------
    #calculating cosine similarity
    similarities = []
    for i in range(len(articles)):
        similarities.append([])
        a = articles[i]
        for j in range(len(articles)):
            b = articles[j]
            similarity = 0
            for word in b.tfidf:
                if word in a.tfidf:
                    similarity += a.tfidf[word] * b.tfidf[word]
            similarity = similarity / (a.vectorlength * b.vectorlength)
            similarities[i].append(similarity)
        similarities[i][i] = 0

    process_status(id,"clustering...")
    flag = 1
    for article in articles:
        article.flag = flag
        flag += 1

    threshold = int(inthreshold)
    if threshold == 0:
        threshold = 550

    while similarities[max(similarities)['i']][max(similarities)['j']] > threshold:
        ij = max(similarities)
        i = ij['i']
        j = ij['j']
        currentflag = articles[j].flag
        for iterator in range(len(articles)):
            if articles[iterator].flag == articles[i].flag:
                articles[iterator].flag = articles[j].flag
        similarities[i][j] = 0
        similarities[j][i] = 0

    process_status(id,"making clusters")
    clusters = []
    while flag > 0:
        currentcluster = []
        for article in articles:
            if article.flag == flag:
                currentcluster.append(article)
        if len(currentcluster) > 0:
            clusters.append(currentcluster)
        flag -= 1

    print(clusters)
    serializableClusters = []
    for cl in clusters:
        templc = []
        for artic in cl:
            templc.append(artic.todict())
        serializableClusters.append(templc)

    with open("%d.json"%id, "w") as f:
        f.write(json.dumps(serializableClusters, ensure_ascii=False, indent=4))
    
    process_status(id,"finished")



#routes definition
@app.route('/')
def hello_world():
    return 'server is working!'

@app.route('/query/<website>/<int:threshold>')
def get_id(website, threshold):
    global counter
    global process_stat
    counter += 1
    clustering_process = multiprocessing.Process(target = clustering, args = (website, threshold, counter, ) )
    process_status(counter,"starting")
    clustering_process.start()
    return "id = %d" %counter

'''
@app.route('/usage')
def get_usage():
    global process_stat
    print(process_stat)
'''

@app.route('/check_stat/<int:id>')
def check(id):
    with open("%d.stat"%id) as status:
        return status.read()


@app.route('/result/<int:id>')
def result(id):
    with open("%d.stat"%id) as status:
        if status.read() == "finished":
            with open("%d.json"%id,'r') as res:
                json_context = res.read()
                return json_context
        