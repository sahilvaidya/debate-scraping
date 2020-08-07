import json
import urllib.request
from bs4 import BeautifulSoup
import csv
import xlsxwriter
import pandas
import time

# Adds url to next_urls list (Requires html input with href as the url)
def addurl(url):
    if url in next_urls:
        return
    next_urls.append('https://www.tabroom.com/index/tourn/postings/'+url['href'])

loop = True
#tournaments = [('https://www.tabroom.com/index/tourn/postings/entry_record.mhtml?tourn_id=10622&entry_id=1940454', 'Wichita State')]

# Tournament to scrape -- needs results page for any random team and tournament name
tournaments = [('https://www.tabroom.com/index/tourn/postings/entry_record.mhtml?tourn_id=10550&entry_id=1953803','UMW')]

# urllib variables
user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
next_urls = []
used_urls = []

# Gets judges from page and adds new urls
def findjudges(soup):
    # Find all "a" elements with white padtop padbottom (this includes the opposing teams)
    j = soup.find_all('a',attrs = {'class': 'white padtop padbottom'})
    judges = []
    for js in j:
        judgename = js.text
        # If the name has a tab, the element is a team name
        # The url for that team's results is added
        if('\t' in judgename):
            addurl(js)
        
        # Otherwise add the judge
        else:
            judgename.strip(" ")
            judges.append(judgename[1:len(judgename)-1])

    return judges


# Find the result
def findwins(soup):
    w = soup.find_all('span',attrs = {'class': 'tenth centeralign semibold'})


    wins = []

    for ws in w:
        temp = ws.text
        temp = temp.replace('\t','')
        temp = temp.replace('\n','')
        wins.append(temp)

    return wins

# Find the debater names and speaker points
def finddebaters(soup):
    d = soup.find_all('span',attrs = {'class':'threefifths nowrap marvertno'})
    p = soup.find_all('span',attrs = {'class':'fifth marno'})

    dp = []

    for ds,ps in zip(d,p):
        t1 = ds.text
        t1 = t1.replace('\t','')
        t1 = t1.replace('\n','')
        t1 = t1[:t1.rfind(' ')] + ',' + t1[t1.rfind(' '):]
        t2 = ps.text
        t2 = t2.replace('\t','')
        t2 = t2.replace('\n','')
        record = {'debater':t1,'speaks':t2}
        dp.append(record)

    return dp

# Find if they were aff or neg
def findsides(soup):
    # Also gets Round and Win/Loss
    s = soup.find_all('span',attrs = {'class':'tenth'})

    sides = []

    for ss in s:
        attrs = ss['class']
        # Weeds out Round and Win/Loss
        if 'semibold' in attrs:
            continue
        side = ss.text
        side = side.replace('\t','')
        side = side.replace('\n','')
        if side == 'Bye':
            continue
        sides.append(side)

    return sides

# Get the team code
def findteamcode(soup):
    t = soup.find('h2')

    teamcode = t.text
    teamcode = teamcode.replace('\t','')
    teamcode = teamcode.replace('\n','')
    return teamcode


def findall(soup):
    return findjudges(soup),findwins(soup),finddebaters(soup),findsides(soup),findteamcode(soup)


tcount = 1

# Use a XLSX workbook -- allows for more customization
with xlsxwriter.Workbook('speaks.xlsx', {'strings_to_numbers': True}) as workbook:
    # Loop through all tournaments in list
    for torn in tournaments:
        # Console logging info
        print('Processing tournament ' + torn[1] + '. Number ' + str(tcount) + ' of ' + str(len(tournaments)))

        # Grab URL from user array
        url = torn[0]

        # Create excel sheet with name passed in user array
        worksheet = workbook.add_worksheet(torn[1])

        # Add headers
        headers = ['Round','Side', 'Judge','Result','Debater','Speaks','Team Code']
        worksheet.write_row(0,0,headers)

        # Number of teams entered
        count = 0

        # Row to add round
        row = 1

        # number of tournaments processed
        tcount+=1
        while loop:
            count += 1

            # Get results webpage
            try:
                request = urllib.request.Request(url,headers={'User-Agent': user_agent})
                html = urllib.request.urlopen(request).read()
            except:
                # If attempt fails waiting a second usually fixes
                time.sleep(1)
                request = urllib.request.Request(url,headers={'User-Agent': user_agent})
                html = urllib.request.urlopen(request).read()
            
            # Use BeautifulSoup to parse page html
            soup = BeautifulSoup(html,'html.parser')

            # Parse page for important data
            judges,wins,dp,sides,teamcode = findall(soup)

            # Start indexing at the last element
            dpindex = len(dp)-1
            jindex = len(judges)-1
            sindex = len(sides)-1
            dround = 1
            print(str(count) + " " + teamcode)

            try:
                # For each debater on the team loop
                while(dpindex > 0):
                    # ??? What is torn[2]
                    for i in range(0,torn[2]):
                        data = (dround,sides[sindex],judges[jindex],wins[jindex],dp[dpindex-1]['debater'],dp[dpindex-1]['speaks'],teamcode)
                        worksheet.write_row(row,0,data)
                        row+=1
                        data = (dround,sides[sindex],judges[jindex],wins[jindex],dp[dpindex]['debater'],dp[dpindex]['speaks'],teamcode)
                        worksheet.write_row(row,0,data)
                        row+=1
                        dpindex -= 2
                        jindex -= 1
                    dround += 1
                    sindex -= 1
            except IndexError:
                 while(dpindex > 0):
                    data = (dround,sides[sindex],judges[jindex],wins[jindex],dp[dpindex-1]['debater'],dp[dpindex-1]['speaks'],teamcode)
                    worksheet.write_row(row,0,data)
                    row+=1
                    data = (dround,sides[sindex],judges[jindex],wins[jindex],dp[dpindex]['debater'],dp[dpindex]['speaks'],teamcode)
                    worksheet.write_row(row,0,data)
                    row+=1
                    dpindex -= 2
                    jindex -= 1
                    dround += 1
                    sindex -= 1

            #Add this url to used URLs
            used_urls.append(url)

            # Create set of URLs which have not been used
            next_urls = [x for x in next_urls if x not in used_urls]

            # Quit when there are no new urls
            if len(next_urls) == 0:
                break

            # while next_urls[0] in used_urls:
            #     del next_urls[0]
            #     print(len(next_urls))
            #     if len(next_urls) == 0:
            #         loop = False
            #         break
            url = next_urls[0]




