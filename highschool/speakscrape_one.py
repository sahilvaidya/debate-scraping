import json
import urllib.request
from bs4 import BeautifulSoup
import csv
import xlsxwriter
import pandas
import time


def addurl(url):
    if url in next_urls:
        return
    next_urls.append('https://www.tabroom.com/index/tourn/postings/'+url['href'])

loop = True
#tournaments = [('https://www.tabroom.com/index/tourn/postings/entry_record.mhtml?tourn_id=10622&entry_id=1940454', 'Wichita State')]
tournaments = [('https://www.tabroom.com/index/tourn/postings/entry_record.mhtml?tourn_id=10550&entry_id=1953803','UMW')]
user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
next_urls = []
used_urls = []


def addurl(url):
    if url in next_urls:
        return
    next_urls.append('https://www.tabroom.com/index/tourn/postings/'+url['href'])

def findjudges(soup):
    j = soup.find_all('a',attrs = {'class': 'white padtop padbottom'})
    judges = []
    for js in j:
        judgename = js.text
        if('\t' in judgename):
            addurl(js)
        else:
            judgename.strip(" ")
            judges.append(judgename[1:len(judgename)-1])

    return judges

def findwins(soup):
    w = soup.find_all('span',attrs = {'class': 'tenth centeralign semibold'})


    wins = []

    for ws in w:
        temp = ws.text
        temp = temp.replace('\t','')
        temp = temp.replace('\n','')
        wins.append(temp)

    return wins

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

def findsides(soup):
    s = soup.find_all('span',attrs = {'class':'tenth'})

    sides = []

    for ss in s:
        attrs = ss['class']
        if 'semibold' in attrs:
            continue
        side = ss.text
        side = side.replace('\t','')
        side = side.replace('\n','')
        if side == 'Bye':
            continue
        sides.append(side)

    return sides

def findteamcode(soup):
    t = soup.find('h2')

    teamcode = t.text
    teamcode = teamcode.replace('\t','')
    teamcode = teamcode.replace('\n','')
    return teamcode


def findall(soup):
    return findjudges(soup),findwins(soup),finddebaters(soup),findsides(soup),findteamcode(soup)


tcount = 1

with xlsxwriter.Workbook('speaks.xlsx', {'strings_to_numbers': True}) as workbook:
    for torn in tournaments:
        print('Processing tournament ' + torn[1] + '. Number ' + str(tcount) + ' of ' + str(len(tournaments)))
        url = torn[0]
        worksheet = workbook.add_worksheet(torn[1])
        headers = ['Round','Side', 'Judge','Result','Debater','Speaks','Team Code']
        worksheet.write_row(0,0,headers)
        count = 0
        row = 1
        tcount+=1
        while loop:
            count += 1
            try:
                request = urllib.request.Request(url,headers={'User-Agent': user_agent})
                html = urllib.request.urlopen(request).read()
            except:
                time.sleep(1)
                request = urllib.request.Request(url,headers={'User-Agent': user_agent})
                html = urllib.request.urlopen(request).read()
            soup = BeautifulSoup(html,'html.parser')

            judges,wins,dp,sides,teamcode = findall(soup)

            
            dpindex = len(dp)-1
            jindex = len(judges)-1
            sindex = len(sides)-1
            dround = 1
            print(str(count) + " " + teamcode)

            try:
                while(dpindex > 0):
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

            used_urls.append(url)

            next_urls = [x for x in next_urls if x not in used_urls]

            if len(next_urls) == 0:
                break

            # while next_urls[0] in used_urls:
            #     del next_urls[0]
            #     print(len(next_urls))
            #     if len(next_urls) == 0:
            #         loop = False
            #         break
            url = next_urls[0]




