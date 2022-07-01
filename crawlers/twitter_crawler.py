import tweepy
import csv
import pandas as pd
import sys

api_key = 'I0JNGPSGmYmeoEjAba2stcS2H'
api_secret = 'PzqjkNTXAcBWVZxcRKXIEVQrVQwpjsPKHv4Deh8vJAu6DBtguR'
access_token = '813145671020773377-u5aut1X7L2Ab0gokoT37xLUDNVCbeEv'
access_token_secret = 'BW5uHBqPzsjgD0NJ5jEXCsdC4KZM0HuKadjovl7iBrwjl'

auth = tweepy.OAuthHandler(api_key, api_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

HashValue = "سامسونگ"

csvFile = open(HashValue+'.csv', 'a')

csvWriter = csv.writer(csvFile)

i = 1
for tweet in tweepy.Cursor(api.search, q=HashValue, count=20, lang="fa").items():
    print(tweet.created_at, i)
    csvWriter.writerow([tweet.created_at, tweet.full_text.encode('utf-8')])
    i += 1

print("Scraping finished and saved to "+HashValue+".csv")
