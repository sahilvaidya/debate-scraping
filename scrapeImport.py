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
    if opponentHTML:
        opponentText = opponentHTML.text
        opponentText = clean(opponentText)
        opponentText = opponentText.replace('vs ', '')
        return opponentText
    return None

# Return array of judges (allows same code to work for multiple judges/out rounds)
def getJudgeDecisions(roundHTML):
    judgeDecisionsHTML = roundHTML.find_all('div', attrs = {'class': 'padless full marno borderbottom'})
    # print(len(judgeDecisionsHTML))
    judgeDecisions = []
    for judgeDecision in judgeDecisionsHTML:
        judge = getJudge(judgeDecision)
        decision = getDecisions(judgeDecision)
        speakers = getSpeakers(judgeDecision)
        judgeDecisions.append((judge,decision,speakers))
    return judgeDecisions

def getJudge(judgeDecisionHTML):
    judgesHTML = judgeDecisionHTML.find_all('a', attrs = {'class': 'white padtop padbottom'})
    for judgeHTML in judgesHTML:
        if '\t' in judgeHTML.text:
            continue
        judgeText = judgeHTML.text
        judgeText = judgeText.strip(" ")
        return judgeText

# Get W or L for each judge
def getDecisions(judgeDecisionHTML):
    decisionHTML = judgeDecisionHTML.find('span', attrs = {'class' : 'tenth centeralign semibold'})

    decisionText = decisionHTML.text
    decisionText = clean(decisionText)
    return decisionText

# Get debater names and speaker points
# Returns null if nothing there (out rounds)
def getSpeakers(judgeDecisionHTML):
    debaterDivHTML = judgeDecisionHTML.find_all('div',attrs={'class':'full nospace smallish'})
    if len(debaterDivHTML) == 0:
        return None
    if len(debaterDivHTML) == 1:
        mavHTML = soup.find('h4', attrs = {'class':'nospace semibold'})
        mavName = mavHTML.text
        mavName = clean(mavName)
        speaksHTML = judgeDecisionHTML.find('span',attrs = {'class':'fifth marno'})
        speaks = speaksHTML.text
        speaks = clean(speaks)
        return [(mavName,speaks)]
    
    speakersToReturn = []
    for debater in debaterDivHTML:
        debaterHTML = debater.find('span',attrs = {'class':'threefifths nowrap marvertno'})
        speaksHTML = debater.find('span',attrs = {'class':'fifth marno'})
        debater = debaterHTML.text
        debater = clean(debater)
        speaks = ""
        if speaksHTML:
            speaks = speaksHTML.text
            speaks = clean(speaks)
        else:
            speaks = "N/A"
        speakersToReturn.append((debater,speaks))

    return speakersToReturn

# Call all methods to get data
def getResults(roundHTML):
    return getRoundNumber(roundHTML),getSide(roundHTML),getOpponent(roundHTML),getJudgeDecisions(roundHTML)

# Adds a url to the total list
def addURL(team):
    urlText = 'https://www.tabroom.com'+team['href']
    if not urlText in urls:
        urls.append(urlText)

def scrape(tournament):
    # Tournament to scrape -- needs results page for any random team and tournament name
    # tournaments = [('https://www.tabroom.com/index/tourn/postings/entry_record.mhtml?tourn_id=10550&entry_id=1953803','UMW')]

    # Initial URL
    start_url = tournament

    # urllib variables
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'

    # url list
    global urls 
    urls = []
    global url_location 
    url_location= 0

    # Load results page
    request = urllib.request.Request(start_url, headers={'User-Agent': user_agent})
    html = urllib.request.urlopen(request).read()

    global soup 
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

                # When there is no judge it is a BYE
                if len(judgesDecisions) == 0:
                    if not opponent:
                        opponent = "N/A"
                    entry = (roundNumber,"BYE",opponent,"N/A","N/A","N/A","N/A","N/A","N/A",teamCode)
                    worksheet.write_row(rowCount,0,entry)
                    rowCount += 1
                    continue

                # Store debater names in case not present later
                if i == 0 and len(judgesDecisions[0][2]) == 2:
                    # print(judgesDecisions)
                    debaterA = judgesDecisions[0][2][0][0]
                    debaterB = judgesDecisions[0][2][1][0]
                
                for judgeDecision in judgesDecisions:
                    if judgeDecision[2]:
                        speakers = judgeDecision[2]
                    else:
                        speakers = [(debaterA, "N/A"),(debaterB,"N/A")]
                    judge = judgeDecision[0]
                    decision = judgeDecision[1]
                    if len(speakers) == 2:
                        entry = (roundNumber,side,opponent,judge,decision,speakers[0][0], speakers[0][1],speakers[1][0],speakers[1][1],teamCode)
                    elif len(speakers) == 1:
                        entry = (roundNumber,side,opponent,judge,decision,speakers[0][0], speakers[0][1],"N/A","N/A",teamCode)
                    worksheet.write_row(rowCount,0,entry)
                    rowCount += 1
                    print(entry)



                # When there is no judge it is a BYE
                # if len(judges) == 0:
                #     entry = (roundNumber,"BYE",opponent,"N/A","N/A","N/A","N/A",teamCode)
                #     worksheet.write_row(rowCount,0,entry)
                #     rowCount += 1
                #     continue
                
                # Iterate through each judge and make a seperate entry
                # for i in range(0,len(judges)):
                #     entry = (roundNumber,side,opponent,judges[i],decisions[i],speakers[0][0],speakers[0][1],speakers[1][0],speakers[1][1],teamCode)
                #     worksheet.write_row(rowCount,0,entry)
                #     rowCount += 1

                
            url_location += 1

    return tournamentName
