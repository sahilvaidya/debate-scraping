import json
import urllib.request
from bs4 import BeautifulSoup
import csv
import xlsxwriter
import pandas
import time

# Remove tabs and new lines
def clean(string):
    string = string.replace('\t','')
    string = string.replace('\n','')
    return string

# Get the round name/number
def getRoundNumber(roundHTML):
    roundNumberHTML = roundHTML.find('span', attrs = {'class': 'tenth semibold'})
    roundText = roundNumberHTML.text
    roundText = clean(roundText)
    return roundText

# Get the side (aff/neg)
def getSide(roundHTML):
    sidesHTML = roundHTML.find_all('span',attrs={'class':'tenth'})

    for side in sidesHTML:
        attrs = side['class']
        if 'semibold' in attrs:
            continue
        sideText = side.text
        sideText = clean(sideText)
        return sideText

# Get team code for opponent
def getOpponent(roundHTML):
    opponentHTML = roundHTML.find('a', attrs = {'class': 'white padtop padbottom'})
    opponentText = opponentHTML.text
    opponentText = clean(opponentText)
    opponentText = opponentText.replace('vs ', '')
    return opponentText

# Return array of judges (allows same code to work for multiple judges/out rounds)
def getJudgeDecisions(roundHTML):
    judgeDecisionsHTML = roundHTML.find_all('div', attrs = {'class': 'padless full marno borderbottom'})
    print(judgeDecisionsHTML)
    judgesHTML = roundHTML.find_all('a', attrs = {'class': 'white padtop padbottom'})
    judges = []
    for judgeHTML in judgesHTML:
        if '\t' in judgeHTML.text:
            continue
        judgeText = judgeHTML.text
        judgeText = judgeText.strip(" ")
        judges.append(judgeText)
    return judges

# Get W or L for each judge
def getDecisions(roundHTML):
    decisionHTML = roundHTML.find_all('span', attrs = {'class' : 'tenth centeralign semibold'})
    decisions = []

    for decision in decisionHTML:
        decisionText = decision.text
        decisionText = clean(decisionText)
        decisions.append(decisionText)
    return decisions

# Get debater names and speaker points
# Returns null if nothing there (out rounds)
def getSpeakers(roundHTML):
    debaterHTML = roundHTML.find_all('span',attrs = {'class':'threefifths nowrap marvertno'})
    speaksHTML = roundHTML.find_all('span',attrs = {'class':'fifth marno'})
    if len(debaterHTML) != 0:
        debater1HTML = debaterHTML[0]
        debater2HTML = debaterHTML[1]
        speaks1HTML = speaksHTML[0]
        speaks2HTML = speaksHTML[1]
        debater1 = debater1HTML.text
        debater2 = debater2HTML.text
        speaks1 = speaks1HTML.text
        speaks2 = speaks2HTML.text
        debater1 = clean(debater1)
        debater2 = clean(debater2)
        speaks1 = clean(speaks1)
        speaks2 = clean(speaks2)
        return [(debater1,speaks1),(debater2,speaks2)]
    return None

# Call all methods to get data
def getResults(roundHTML):
    return getRoundNumber(roundHTML),getSide(roundHTML),getOpponent(roundHTML),getJudgeDecisions(roundHTML)

# Adds a url to the total list
def addURL(team):
    urlText = 'https://www.tabroom.com'+team['href']
    if not urlText in urls:
        urls.append(urlText)

# Tournament to scrape -- needs results page for any random team and tournament name
tournaments = [('https://www.tabroom.com/index/tourn/postings/entry_record.mhtml?tourn_id=10550&entry_id=1953803','UMW')]

# Initial URL
start_url = 'http://www.tabroom.com/index/tourn/results/ranked_list.mhtml?event_id=111719&tourn_id=13327'

# urllib variables
user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'

# url list
urls = []
url_location = 0

# Load results page
request = urllib.request.Request(start_url, headers={'User-Agent': user_agent})
html = urllib.request.urlopen(request).read()

soup = BeautifulSoup(html, 'html.parser')

# Get all entries on the results page and get their results URLs
resultsPage = soup.find_all('a', attrs={'class': 'white'})
for team in resultsPage:
    addURL(team)

# Get the tournament name
tournamentName = soup.find('h2').text
tournamentName = clean(tournamentName)


with xlsxwriter.Workbook('speaks.xlsx', {'strings_to_numbers': True}) as workbook:
    worksheet = workbook.add_worksheet(tournamentName)
    rowCount = 1
    while len(urls) > url_location:
        # Get results webpage
        request = urllib.request.Request(urls[url_location], headers={'User-Agent': user_agent})
        html = urllib.request.urlopen(request).read()

        # Add headers
        headers = ['Round','Side', 'Opponent', 'Judge','Result','DebaterA','SpeaksA','DebaterB','SpeaksB','Team Code']
        worksheet.write_row(0,0,headers)


        # Use BeautifulSoup to parse page html
        soup = BeautifulSoup(html,'html.parser')

        # Grab team code
        teamCodeHTML = soup.find('h2')
        teamCode = teamCodeHTML.text
        teamCode = clean(teamCode)

        # Dummy variables to store debater names if they are not available later
        debaterA = ""
        debaterB = ""

        # Grab each div which contains a single round of data and iterate through
        allRoundHTML = soup.find_all('div', {"class": "row"})
        for i,roundHTML in enumerate(reversed(allRoundHTML)):
            roundNumber,side,opponent,judgesDecisions = getResults(roundHTML)

            # Store debater names in case not present later
            if i == 0:
                debaterA = speakers[0][0]
                debaterB = speakers[1][0]
            
            # Check if speaker name was present
            if not speakers:
                speakers = [(debaterA, "N/A"),(debaterB,"N/A")]

            # When there is no judge it is a BYE
            if len(judges) == 0:
                entry = (roundNumber,"BYE",opponent,"N/A","N/A","N/A","N/A",teamCode)
                worksheet.write_row(rowCount,0,entry)
                rowCount += 1
                continue
            
            # Iterate through each judge and make a seperate entry
            for i in range(0,len(judges)):
                entry = (roundNumber,side,opponent,judges[i],decisions[i],speakers[0][0],speakers[0][1],speakers[1][0],speakers[1][1],teamCode)
                worksheet.write_row(rowCount,0,entry)
                rowCount += 1

            
        url_location += 1

