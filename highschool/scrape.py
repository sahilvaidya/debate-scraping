import json
import urllib.request
from bs4 import BeautifulSoup
import csv
import xlsxwriter
import pandas
import time


def getRoundNumber(roundHTML):
    roundNumberHTML = roundHTML.find('span', attrs = {'class': 'tenth semibold'})
    roundText = roundNumberHTML.text
    roundText = roundText.replace('\t','')
    roundText = roundText.replace('\n','')
    return roundText

def getSide(roundHTML):
    sidesHTML = roundHTML.find_all('span',attrs={'class':'tenth'})

    for side in sidesHTML:
        attrs = side['class']
        if 'semibold' in attrs:
            continue
        sideText = side.text
        sideText = sideText.replace('\t','')
        sideText = sideText.replace('\n','')
        return sideText


def getOpponent(roundHTML):
    opponentHTML = roundHTML.find('a', attrs = {'class': 'white padtop padbottom'})
    opponentText = opponentHTML.text
    opponentText = opponentText.replace('\t','')
    opponentText = opponentText.replace('\n','')
    opponentText = opponentText.replace('vs ', '')
    return opponentText

def getJudges(roundHTML):
    judgesHTML = roundHTML.find_all('a', attrs = {'class': 'white padtop padbottom'})
    judges = []
    for judgeHTML in judgesHTML:
        if '\t' in judgeHTML.text:
            continue
        judgeText = judgeHTML.text
        judgeText = judgeText.strip(" ")
        judges.append(judgeText)
    return judges

def getDecisions(roundHTML):
    decisionHTML = roundHTML.find_all('span', attrs = {'class' : 'tenth centeralign semibold'})
    decisions = []

    for decision in decisionHTML:
        decisionText = decision.text
        decisionText = decisionText.replace('\t','')
        decisionText = decisionText.replace('\n','')
        decisions.append(decisionText)
    return decisions

def getResults(roundHTML):
    return getRoundNumber(roundHTML),getSide(roundHTML),getOpponent(roundHTML),getJudges(roundHTML),getDecisions(roundHTML)

def addURL(roundHTML):
    urlHTML = roundHTML.find('a', attrs = {'class': 'white padtop padbottom'})
    urlText = 'https://www.tabroom.com/index/tourn/postings/'+urlHTML['href']
    if not urlText in next_urls:
        next_urls.append(urlText)

# Tournament to scrape -- needs results page for any random team and tournament name
tournaments = [('https://www.tabroom.com/index/tourn/postings/entry_record.mhtml?tourn_id=10550&entry_id=1953803','UMW')]

# Initial URL
start_url = 'http://www.tabroom.com/index/tourn/postings/entry_record.mhtml?tourn_id=13038&entry_id=2719614'

# urllib variables
user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'

# url list
next_urls = [start_url,]
url_location = 0

with xlsxwriter.Workbook('speaks.xlsx', {'strings_to_numbers': True}) as workbook:
    worksheet = workbook.add_worksheet('TOC')
    rowCount = 1
    while len(next_urls) > url_location:
        # Get results webpage
        request = urllib.request.Request(next_urls[url_location], headers={'User-Agent': user_agent})
        html = urllib.request.urlopen(request).read()

        # Add headers
        headers = ['Round','Side', 'Opponent', 'Judge','Result','Debater','Speaks','Team Code']
        worksheet.write_row(0,0,headers)

        # Use BeautifulSoup to parse page html
        soup = BeautifulSoup(html,'html.parser')

        allRoundHTML = soup.find_all('div', {"class": "row"})
        for roundHTML in allRoundHTML:
            roundNumber,side,opponent,judges,decisions = getResults(roundHTML)
            addURL(roundHTML)
            # print(roundNumber)
            # print(side)
            # print(opponent)
            # print(judges)
            # print(decisions)
            if len(judges) == 0:
                entry = (roundNumber,side,opponent,"N/A","N/A")
                worksheet.write_row(rowCount,0,entry)
                rowCount += 1
                continue
            
            for i in range(0,len(judges)):
                entry = (roundNumber,side,opponent,judges[i],decisions[i])
                print(entry)
                worksheet.write_row(rowCount,0,entry)
                rowCount += 1

            
        
        url_location += 1

