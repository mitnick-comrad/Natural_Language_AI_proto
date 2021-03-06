import nltk
nltk.download('punkt')
from nltk.stem.lancaster import LancasterStemmer
stemmer= LancasterStemmer()
from keras.datasets import imdb
import keras
import numpy
import tflearn
import tensorflow as tf
import random
import json
import os
import pandas as pd

import sqlite3
import psycopg2
import psycopg2.extras



conn= psycopg2.connect(dbname="dv6jrsqbauch3",user="pezqypcwxbbrku",password="password",host="ec2-52-202-22-140.compute-1.amazonaws.com",port="5432")
cur= conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
cur.execute("SELECT * FROM tag;")
tag=cur.fetchall()
cur.execute("SELECT * FROM patterns;")
pattern=cur.fetchall()
cur.execute("SELECT * FROM responses;")
response= cur.fetchall()
col=[]

#with open("C:\\Users\\Zayne\\Desktop\\Desktop-rest\\json file\\intents.json") as file :
#  data= json.load(file)
#dl= pd.read_json(conn)
#data= pd.DataFrame(dl.intents.values.tolist())['mark']
#data= pd.json_normalize(data).head()
#data=a

#print(data)
words =[]
lables = []
docs= []
docs_x=[]
docs_y=[]
i=0
#for intent in data:
for patterns in pattern:
  
  for pat in patterns[1:]:
    
    if pat != None:
      wrds = nltk.word_tokenize(pat)
      words.extend(wrds)
      docs_x.append(wrds)
      docs_y.append(tag[i][1])

      if tag[i] not in lables:
        lables.append(tag[i][1])
    else:
          continue
  i=i+1
  #i=i+1
words = [stemmer.stem(w.lower()) for w in words if w not in "?"]
words= sorted(list(set(words)))

lables = sorted(lables)

training =[]
output = []


out_empty= [0 for _ in range(len(lables))]



for x, doc  in enumerate(docs_x):
  bag = []

  wrds=[stemmer.stem(w) for w in doc]

  for w in words:
    if w in wrds:
      bag.append(1)
    else:
      bag.append(0)
  output_row = out_empty[:]
  output_row[lables.index(docs_y[x])] =1

  training.append(bag)
  output.append(output_row)

training = numpy.array(training)
output = numpy.array(output)

tf.reset_default_graph()
net = tflearn.input_data(shape= [None, len(training[0])])
net = tflearn.fully_connected(net,8)
net = tflearn.fully_connected(net,8)
net = tflearn.fully_connected(net,len(output[0]), activation="softmax")
net = tflearn.regression(net)


model = tflearn.DNN(net)

model.fit(training, output, n_epoch=1000, batch_size=8, show_metric=True)
model.save("model.tflearn")
checkpoint_dir = './training_checkpoints'
# Name of the checkpoint files
checkpoint_prefix = os.path.join(checkpoint_dir, "ckpt_{epoch}")

checkpoint_callback=tf.keras.callbacks.ModelCheckpoint(
    filepath=checkpoint_prefix,
    save_weights_only=True)
#chat()




def bag_of_words(s, words):
  bag = [0 for _ in range(len(words))]
  s_words = nltk.word_tokenize(s)
  s_words = [stemmer.stem(word.lower()) for word in s_words]

  for se in s_words:
    for i, w in enumerate(words):
      if w == se:
        bag[i]=1
  return numpy.array(bag)

def chat():
  
  
  
  while True:
    i=0
    inp = input("You: ")
    if inp.lower()=="quit":
      break
    results = model.predict([bag_of_words(inp, words)])
    results_index = numpy.argmax(results)
    tag1 = lables[results_index]
    #for d in data:
    for tg in tag:
      
      if tg[1]== tag1:
        responses = response[i]
      
    
        #print(responses[random.choice(range(0,len(responses)))])
        print(random.choice([k for k in responses[1:] if k!=None]))
        break
      i=i+1

chat()
