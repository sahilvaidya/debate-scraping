import json
import urllib.request
from bs4 import BeautifulSoup
import csv


tournaments = [('Tournament of Champions','Policy Debate')]

def addurl(url):
    if url in next_urls:
        return
    next_urls.append('https://www.tabroom.com/index/tourn/postings/'+url['href'])

loop = True
url = 'https://www.tabroom.com/index/results/'
user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
next_urls = []
used_urls = []

count = 0

with open('speaks.csv',mode = 'w') as speaks_file:
    fieldnames = ['Round','Side', 'Judge','Result','Debater','Speaks','Team Code']
    writer = csv.DictWriter(speaks_file,fieldnames = fieldnames,lineterminator = '\n')
    writer.writeheader()
    while loop:
        count += 1
        print(count)
        try:
            request = urllib.request.Request(url,headers={'User-Agent': user_agent})
            html = urllib.request.urlopen(request).read()
        except:
            time.sleep(1)
            request = urllib.request.Request(url,headers={'User-Agent': user_agent})
            html = urllib.request.urlopen(request).read()
        soup = BeautifulSoup(html,'html.parser')

        j = soup.find_all('a',attrs = {'class': 'white padtop padbottom'})

        judges = []


        for js in j:
            judgename = js.text
            if('\t' in judgename):
                addurl(js)
            else:
                judgename.strip(" ")
                judges.append(judgename[1:len(judgename)-1])



        w = soup.find_all('span',attrs = {'class': 'tenth centeralign semibold'})


        wins = []

        for ws in w:
            temp = ws.text
            temp = temp.replace('\t','')
            temp = temp.replace('\n','')
            wins.append(temp)



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


        t = soup.find('h2')

        teamcode = t.text
        teamcode = teamcode.replace('\t','')
        teamcode = teamcode.replace('\n','')

        
        dpindex = len(dp)-1
        jindex = len(judges)-1
        sindex = len(sides)-1
        dround = 1
        while(dpindex > 0):
            writer.writerow({'Round':dround, 'Side':sides[sindex], 'Judge':judges[jindex],'Result':wins[jindex],'Debater':dp[dpindex-1]['debater'],'Speaks':dp[dpindex-1]['speaks'],'Team Code':teamcode})
            writer.writerow({'Round':dround, 'Side':sides[sindex], 'Judge':judges[jindex],'Result':wins[jindex],'Debater':dp[dpindex]['debater'],'Speaks':dp[dpindex]['speaks'],'Team Code':teamcode})
            dpindex -= 2
            jindex -= 1
            dround += 1
            sindex -= 1

        used_urls.append(url)

        while next_urls[0] in used_urls:
            del next_urls[0]
            if len(next_urls) == 0:
                loop = False
                break
        url = next_urls[0]




