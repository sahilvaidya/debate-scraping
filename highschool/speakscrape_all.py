import json
import urllib.request
from bs4 import BeautifulSoup
import csv
import xlsxwriter
import time
import re
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from time import sleep

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


def findpage(url):
    add = 1
    odd = True
    while add < 10:
        number = url[len(url)-5:]
        print(number)
        if odd:
            number = int(number) - add
            odd = False
        else:
            number = int(number) + add
            add = add + 1
            odd = True

        newurl = url[:len(url)-5] + str(number)

        print(newurl)

        try:
            request = urllib.request.Request(newurl,headers={'User-Agent': user_agent})
            tournament_html = urllib.request.urlopen(request).read()
        except:
            time.sleep(1)
            request = urllib.request.Request(newurl,headers={'User-Agent': user_agent})
            tournament_html = urllib.request.urlopen(request).read()
        soup = BeautifulSoup(tournament_html,'html.parser')
        skip = True
        title = soup.find_all('h4')
        try:
            page = title[2]
        except:
            continue
        print(page.text)

        if 'Open' in page.text or 'OPEN' in page.text or 'CX-O' in page.text or re.search(r'\bO\b', page.text) or 'OCX' in page.text or 'open' in page.text or 'SHIR' in page.text and not 'LD' in page.text:
            return soup
        if 'RR' in page.text:
            return "fail"

    return "fail"




workbook = xlsxwriter.Workbook('speaks.xlsx', {'strings_to_numbers': True})




url = 'https://www.tabroom.com/index/results/circuit_tourney_portal.mhtml?circuit_id=&year=2018'
user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
next_urls = []
used_urls = []



request = urllib.request.Request(url,headers={'User-Agent': user_agent})
tournament_list = urllib.request.urlopen(request).read()
tournament_soup = BeautifulSoup(tournament_list,'html.parser')

torn = tournament_soup.find_all('a',attrs = {'class':'white full block padless'})

tournament_urls = []
tournaments = []

for t in torn:
    tournaments.append(t.text)
    tournament_urls.append('https://www.tabroom.com'+t['href'])



for tournament,tournament_url in zip(tournaments,tournament_urls):
    if 'test' in tournament or 'Scrimmage' in tournament:
        print('Skipped ' + tournament)
        continue
    print('Processing tournament ' + tournament)
    try:
        request = urllib.request.Request(tournament_url,headers={'User-Agent': user_agent})
        tournament_html = urllib.request.urlopen(request).read()
    except:
        time.sleep(1)
        request = urllib.request.Request(tournament_url,headers={'User-Agent': user_agent})
        tournament_html = urllib.request.urlopen(request).read()
    soup = BeautifulSoup(tournament_html,'html.parser')
    skip = True
    title = soup.find_all('h4')
    page = title[2]
    print(page.text)

    options = webdriver.ChromeOptions()
    #options.add_argument("--window-size=1920x1080")
    options.add_argument('headless')
    driver = webdriver.Chrome(executable_path='C:/chromedriver_win32/chromedriver.exe', chrome_options = options)

    driver.get(tournament_url)
    currenturl = driver.current_url

    driver.quit()



    if not 'Open' in page.text and not 'OPEN' in page.text and not 'CX-O' in page.text and not re.search(r'\bO\b', page.text) and not 'OCX' in page.text and not 'open' in page.text and not 'SHIR' in page.text or 'LD' in page.text:
        soup = findpage(currenturl)
    
    if soup == "fail":
        continue


    # element = driver.find_element_by_xpath("//select[@name='event_id']")
    # element.click()
    # all_options = element.find_elements_by_tag_name("option")
    # for option in all_options:
    #     print("Value is: %s" % option.get_attribute("text"))
    #     option.click()

    # el = driver.find_element_by_name('event_id')
    # for option in el.find_elements_by_tag_name('option'):
    #     print(option.text)
    #     print("1")
    #     if option.text == 'OPEN':
    #         option.click() # select() in earlier versions of webdriver
    #         break

    # driver.find_element_by_xpath("//select[@name='event_id']/options[text()='OPEN']").click()
    # options = dropdown.options
    # try:
    #     dropdown.select_by_value(86916)
    # except:
    #     dropdown.select_by_visible_text("OPEN")


    


    links = soup.find_all('a', attrs = {'blue full nowrap'})
    
    round_url = 'https://www.tabroom.com'+links[len(links)-1]['href']
    try:
        request = urllib.request.Request(round_url,headers={'User-Agent': user_agent})
        round_html = urllib.request.urlopen(request).read()
    except:
        time.sleep(1)
        request = urllib.request.Request(round_url,headers={'User-Agent': user_agent})
        round_html = urllib.request.urlopen(request).read()
    soup = BeautifulSoup(round_html,'html.parser')
    team = soup.find_all('a', attrs = {'class':'white'})
    url = 'https://www.tabroom.com'+team[0]['href']
    worksheet = workbook.add_worksheet(tournament[29:])
    headers = ['Round','Side', 'Judge','Result','Debater','Speaks','Team Code']
    worksheet.write_row(0,0,headers)
    row = 1


    count = 0
    loop = True

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
    


workbook.close()

