import requests
import json
from pprint import pprint


import collections
import pandas as pd
import matplotlib.pyplot as plt

import time
import datetime


from textblob import TextBlob




# REDDIT AUTHORIZATION
_clientId = ""
_secret = ""
_username = ""
_password = ""




today = datetime.date.today()
print(today)



# finds all posts 
# "after" param is the full ID of the last post... that will be the next data set's first... 
def redditAuthorization():
    global  _clientId ,_secret ,_username ,_password
    
    # note that CLIENT_ID refers to 'personal use script' and SECRET_TOKEN to 'token'
    clientId = _clientId
    secret = _secret
    auth = requests.auth.HTTPBasicAuth(clientId, secret)

    # here we pass our login method (password), username, and password
    data = {
        'grant_type': 'password',
        'username': _username,
        'password': _password
    }

    # setup our header info, which gives reddit a brief description of our app
    headers = {'User-Agent': 'Trapistan/0.0.1'}

    # send our request for an OAuth token
    res = requests.post('https://www.reddit.com/api/v1/access_token', auth=auth, data=data, headers=headers)

    # convert response to JSON and pull access_token value
    TOKEN = res.json()['access_token']

    # add authorization to our headers dictionary
    headers = {**headers, **{'Authorization': f"bearer {TOKEN}"}}

    # while the token is valid (~2 hours) we just add headers=headers to our requests
    myAccount = requests.get('https://oauth.reddit.com/api/v1/me', headers=headers)
    print('Authorized')
    return headers
def getPost(subRedit , auth , *B_A):
  if len(B_A) == 0:
    # last page
    urlLink = 'https://oauth.reddit.com/r/' + subRedit + '/new'
    res = requests.get(
      urlLink,
      headers=auth,
      params={'limit' : '100'}
    )
    sample = json.loads(res.text)

    return sample

  else:
    # next page
    urlLink = 'https://oauth.reddit.com/r/' + subRedit + '/new'
    res = requests.get(
      urlLink,
      headers=auth,
      params={'limit' : '100' , 'after' : str(B_A[0])  }
    )
    sample = json.loads(res.text)
  return sample
def redditData(subRedit ):
  headers = redditAuthorization()

  relevant_Data = []
  relevant_Data_IMAGES = []


  sample = getPost( subRedit , headers)

  while  len( sample['data']['children'] ) > 0:
    if len( sample['data']['children'] ) < 100:
      print("last page...")

    for i in range(0,len(sample['data']['children']) , 1): # <--- build data
      dictionary = sample['data']['children'][i]['data']

      #check for images or no words
      if dictionary['selftext'] != '':

        relevant_Data.append(
          {
            'title' : dictionary['title'],
            'text' : dictionary['selftext'],
            'author' : dictionary['author'],
            'text_html' : dictionary['selftext_html'],
            'upvote_ratio' : dictionary['upvote_ratio'],
            'ups' : dictionary['ups'],
            'downs' : dictionary['downs'],
            'total_awards_received' : dictionary['total_awards_received'],
            'score' : dictionary['score'],
            'num_comments' : dictionary['num_comments'],
            'comments_link' : dictionary['permalink'],
            'post_link' : dictionary['url'],
          }
        )
      else:
        # handle images
        relevant_Data_IMAGES.append(
        { 
          'title' : dictionary['title'],
          'upvote_ratio' : dictionary['upvote_ratio'],
          'comments_link' : dictionary['permalink'],
          }
        )


    LastUniqueID = sample['data']['children'][i]['kind']  +  '_' + sample['data']['children'][i]['data']['id']
    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(sample['data']['children'][i]['data']['created_utc'])))
    print("Relevant data gathered: " , len(relevant_Data))
    sample = getPost(subRedit , headers , (  LastUniqueID )   )


  return relevant_Data , relevant_Data_IMAGES

def find_Common_Stock(subRedit):
  print("find_Common_Stock(subRedit)")

  mentions = {}
  
  with open('all_stocks.txt' , 'r') as f:
    list_of_tickers = f.readlines()
    text_data , image_data =  redditData( subRedit )

    print(len(text_data))
    print(len(image_data))

    # CLEAN NO \n IN all_stocks.txt / add all stocks to mentions dict
    for x in range(len(list_of_tickers)):
      list_of_tickers[x] =  list_of_tickers[x][:-1] 
      mentions.update(  { list_of_tickers[x] : { 'MENTIONED' : 0 , 'polarity' : [] , 'opinionated' : []    } }  )
    



    # # ALL GRABBED DATA
    # for x in text_data:
    #   print(x['text'])
    # exit()


    #finds all post with mentioned list of words
    for x in text_data:
      # text
      parsed_data = x['text'].split()
      for word in parsed_data:
        word = replaceChars(word)
        word = word.lower()
        if 'http' in word:
          continue
        elif word == 'a':
          continue
        elif word == 'of':
          continue
        elif word == 'can':
          continue
        elif word == 'by':
          continue
        elif word == 'at':
          continue
        elif word == 'or':
          continue
        elif word == 'so':
          continue
        elif word == 'an':
          continue
        elif word == 'an':
          continue
        elif word == 'he':
          continue
        elif word == 'be':
          continue
        elif word == 'on':
          continue
        elif word == 'am':
          continue
        elif word == 'go':
          continue
        elif word == 'it':
          continue
        else:
          for stock in list_of_tickers:
            amountMentioned = 0
            if word == stock.lower():
              amountMentioned +=1
              wiki = TextBlob(str(x['text']))
              value = (wiki.sentiment.polarity , wiki.sentiment.subjectivity)
              mentions[stock]['polarity'].append(value[0])
              mentions[stock]['opinionated'].append(value[1])

              if amountMentioned == 1:
                mentions[stock]['MENTIONED'] +=1


    for stock in list_of_tickers:
      try:
        mentions[stock]['polarity'] = sum(mentions[stock]['polarity']) / len(mentions[stock]['polarity'])
        mentions[stock]['opinionated'] = sum(mentions[stock]['opinionated']) / len(mentions[stock]['opinionated'])
      except ZeroDivisionError:
        if mentions[stock]['MENTIONED'] < 1 :
          mentions.pop(stock)
        else:
          mentions[stock]['polarity'] = 'N/A'
          mentions[stock]['opinionated'] =  'N/A'

    # DEBUG
    # pprint(mentions)
    # print(len(mentions))


    return mentions

# FIND MOST COMMON WORD
def reddit_RelevantData_analysis(relevant_Data , imageData):
  topOfEachPost = []
  for post in relevant_Data: # each item in relevant_data is a dictionary
    if post['text']  == '':
      continue
    else:
      postAssorted = FindCommonWord( post['text'] )
      if postAssorted[0][0] == '':
        topOfEachPost.append( (postAssorted[1] , post['title'] ) )
      else:
        topOfEachPost.append( (postAssorted[0] , post['title'] ) )
  
  pprint(topOfEachPost)
  return topOfEachPost
def FindCommonWord(a):
    # Stopwords
    stopwords = set(line.strip() for line in open('stopwords.txt'))
    stopwords = stopwords.union(set(['mr','mrs','one','two','said']))

    # Instantiate a dictionary, and for every word in the file, 
    # Add to the dictionary if it doesn't exist. If it does, increase the count.
    wordcount = {}

    # To eliminate duplicates, remember to split by punctuation, and use case demiliters.
    for word in a.lower().split():
      word = replaceChars(word)
        
      if 'http' in word: # remove links 
        word = ''

      if word not in stopwords: #if word is not in blocked words list, make a new key or add to existing
          if word not in wordcount:
              wordcount[word] = 1
          else:
              wordcount[word] += 1


    distinguished_WordsAmount = len(wordcount.keys())
    word_counter = collections.Counter(wordcount)



    sorted_TopWords = word_counter.most_common(distinguished_WordsAmount)
    return sorted_TopWords

    
    # Create a data frame of the most common words 
    # Draw a bar chart
    # lst = word_counter.most_common(n_print)
    # df = pd.DataFrame(lst, columns = ['Word', 'Count'])
    # df.plot.bar(x='Word',y='Count')

# helper functions
def replaceChars(word):
  word = word.replace(".","")
  word = word.replace(",","")
  word = word.replace(":","")
  word = word.replace("\"","")
  word = word.replace("!","")
  word = word.replace("â€œ","")
  word = word.replace("â€˜","")
  word = word.replace("*","")
  word = word.replace("[","")
  word = word.replace("]","")
  word = word.replace("/","")
  word = word.replace("^","")
  word = word.replace("|","")
  word = word.replace("-","")
  word = word.replace("@","")
  word = word.replace("#","")
  word = word.replace("$","")
  word = word.replace("(","")
  word = word.replace(")","")
  word = word.replace("~","")
  word = word.replace("{","")
  word = word.replace("}","")
  word = word.replace("*","")
  word = word.replace('"',"")
  word = word.replace('?',"")
  word = word.replace('>',"")
  word = word.replace('<',"")
  word = word.replace('%',"")
  word = word.replace('&',"")
  word = word.replace('”',"")
  word = word.replace(',',"")
  word = word.replace('.',"")
  word = word.replace('.',"")
  word = word.replace('\n',"")
  return word



def TextBlob_Frequency(textData , imageData):
  pass










# MAIN

# internal functions
# text_data , image_data  = redditData(  'wallstreetbets' )   # building data by looping time segments
# reddit_RelevantData_analysis(text_data , image_data)        # utilizing built data in analysis




# BUILD SENTIMENT ANALYSIS & FREQUENCY COUNTER
output = find_Common_Stock('wallstreetbets')




# TODO TEXT BLOB FUNCTIONS (unfinished)
# text_data , image_data  = redditData(  'wallstreetbets' )  
# TextBlob_Frequency(text_data , image_data)





'''
NOTES
4/17/2021

Look into textblock word and phase frequencies...
https://textblob.readthedocs.io/en/dev/

'''






