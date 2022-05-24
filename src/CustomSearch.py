#!/usr/bin/env python
# coding: utf-8

# import webbrowser
import requests
from bs4 import BeautifulSoup as BS
import mysql.connector
import re
import sys
import json
from cleantext import clean
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


# OCR
import pytesseract
from pytesseract import Output
import PIL
from PIL import Image
import requests
import urllib.request
import io
from io import BytesIO, StringIO
import sys
from pdf2image import convert_from_bytes
import PyPDF2



mydb = mysql.connector.connect(
  host = "localhost",
  port = 8889,
  user = "root",
  password = "root",
  database = "MY_CUSTOM_BOT"
)

####################
# Input
####################
# term = input("Enter search query: ")
# pages = input("Enter number of pages :")

term = sys.argv[1]
pages = 1
new = 2
bterm = term.replace(" ","+")

####################
# Set up URLs
####################
google = "http://google.com"
google_url = google+"/search?q="+term
# webbrowser.open(google_url,new=new);


headers = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}
bing = 'https://www.bing.com'
bing_url = 'https://www.bing.com/search?q={}'.format(bterm)
# webbrowser.open(bing_url,new=new);

yahoo = "https://search.yahoo.com/search?p="+term;
yahoo_url = "https://search.yahoo.com/search?p="+term;
# webbrowser.open(yahoo_url,new=new);


########################
# OCR class
########################

class OCRConvertor():

  def ocr_image(self, url):
    response = requests.get(url)
    image_bytes = BytesIO(response.content)
    img = Image.open(image_bytes)
    text = pytesseract.image_to_string(img)
    return text
  
  def ocr_pdf(self, pdf_url):
    text = ''
    status = 'success'
    try:
        response = requests.head(pdf_url)
        header = response.headers
        # print(header)

        if header.get('Content-Type') is None:
            return text, "No content"
        elif header.get('Content-length') is None:
            return text, "Size not available"
        elif header['Content-Type'] != 'application/pdf': 
            return text, "Not PDF"

        size = int(response.headers['Content-length'])
        if size > 1000000:
            status = "Too heavy"
        else:
            response = requests.get(pdf_url)
            pages = convert_from_bytes(response.content)

            for page in pages:
                temp = str(pytesseract.image_to_string(page))
                text = text + temp
    except requests.exceptions.RequestException as error:
        status = "OCR error"

    return text, status


########################
# Webpage Scrape Method
########################

def get_text_contents(url):
    text = ''
    status = 'success'

    try:
        response = requests.head(url, timeout=10)
        header = response.headers

        if header.get('Content-Type') is None:
            status = "No content"
        elif 'text/html' in header['Content-Type']: 
            html_content = requests.get(url).text
            soup = BS(html_content, "html.parser")
            if soup.find("body") is None:
                status = "No body"
            else:
                text = soup.find("body").text
        else: 
            status = "Not web"
    except requests.exceptions.RequestException as error:
        status = "Timeout"

    return text, status


#######################
# Database connection
#######################
# Get engines data
mycursor = mydb.cursor()
mycursor.execute("SELECT * FROM engines")
myresult = mycursor.fetchall()
myengines = {i[0]: i[1] for i in myresult}


##############################
# 1. Insert keyword
##############################
# Check if the keyword already exist. If not, insert
mycursor.execute("SELECT * FROM keywords WHERE keyword = %s", (term,))
myresult = mycursor.fetchall()
    
if len(myresult)==0:
    mycursor.execute("INSERT INTO keywords (keyword) VALUES (%s)", (term,))
    keyword_id = mycursor.lastrowid
    mydb.commit()
else:
    keyword_id = myresult[0][0]


##############################
# 2. Retrieve search links
##############################
cnt = 0
bpage = 0
insert_values = []

for i in range(int(pages)):
    
    ##########
    # GOOGLE 
    ##########
    engine = 'Google'
    engine_id = list(myengines.keys())[list(myengines.values()).index(engine)]

    req = requests.get(google_url)
    soup = BS(req.text, 'html.parser')
    
    # Retrieve the result 
    results = soup.find_all("div", {"class": "ZINbbc luh4tb xpd O9g5cc uUPGi"})
    for div in results:
        header = div.find('div', {'class': 'egMi0 kCrYT'})
        title = header.find('div', {'class': 'BNeawe vvjwJb AP7Wnd'}).text
        path = header.find('div', {'class': 'BNeawe UPmit AP7Wnd'}).text
        description = div.find('div', {'class': 'BNeawe s3v9rd AP7Wnd'}).text
        href = header.find('a')['href']
        href = href.replace("/url?q=", "")
        link = href[0:href.index("&sa=U&ved=")]

        title = clean(title, no_emoji=True)
        insert_values.append((engine_id, keyword_id, title, link, path, description, 0, i+1))
      
    # Retrieve the ads
    ads = soup.find_all("div", {"class": "ZINbbc luh4tb O9g5cc uUPGi"})
    for div in ads:
        header = div.find('div', {'class': 'v5yQqb jqWpsc'})
        title = header.find('div', {'class': 'CCgQ5 MUxGbd v0nnCb aLF0Z OSrXXb'}).text
        path = header.find('span', {'class': 'qzEoUe'}).text
        description = div.find('div', {'class': 'w1C3Le'}).text
        link = header.find('a')['href']

        title = clean(title, no_emoji=True)
        insert_values.append((engine_id, keyword_id, title, link, path, description, 1, i+1))

    # Create next page url
    nextpage = soup.find("a", {"class": "nBDE1b G5eFlf"})['href']
    google_url = google+nextpage
    
    ##########
    # Yahoo 
    ##########
    engine = 'Yahoo'
    engine_id = list(myengines.keys())[list(myengines.values()).index(engine)]

    req = requests.get(yahoo_url)
    soup = BS(req.text, 'html.parser')

    # Retrieve the result 
    results = soup.find_all("div",attrs={'class': re.compile('^dd algo algo-sr relsrch.*')})
    for j in results:
        header = j.find("div", {"class": "compTitle options-toggle"})
        path = j.find("span",{"class":"d-ib p-abs t-0 l-0 fz-14 lh-20 fc-obsidian wr-bw ls-n pb-4"}).text
        title_tag = j.find("a",{"class":"d-ib ls-05 fz-20 lh-26 td-hu tc va-bot mxw-100p"})
        children = title_tag.findChildren('span')
        title = title_tag.text
        for child in children:
            title = title.replace(child.text, '')

        description = j.find("div",{"class":["compText","compList"]}).text
        link = header.find('a')['href']

        title = clean(title, no_emoji=True)
        insert_values.append((engine_id, keyword_id, title, link, path, description, 0, i+1))

    # Retrieve the ads
    ads = soup.find_all("div",attrs={'class': re.compile('^dd ads.*')})
    for j in ads:
        header = j.find("div", {"class": "compTitle mb-3"})
        path = j.find("span",{"class":"ad-domain fz-14 lh-20 s-url fc-obsidian d-ib pb-4"}).text
        title = j.find("span",{"class":"ls-05 fz-20 lh-26 d-b tc"}).text
        description = j.find("span",{"class":"fc-falcon"}).text
        link = header.find('a')['href']

        title = clean(title, no_emoji=True)
        insert_values.append((engine_id, keyword_id, title, link, path, description, 1, i+1))

    # Create next page url
    yahoo_url = yahoo+"&pz=7&b="+str((i+1)*7+1)
    
    
    ##########
    # Bing 
    ##########
    engine = 'Bing'
    engine_id = list(myengines.keys())[list(myengines.values()).index(engine)]

    req = requests.get(bing_url,headers = headers)
    soup = BS(req.text, 'html.parser')
    
    nextpage = soup.find('a',{'title' : 'Next page'})
    if nextpage is not None:
        nextpage = nextpage['href']
        # Retrieve the result 
        results = soup.find_all('li',{'class':'b_algo'})
        for j in results:
            header = j.find('h2')
            path = j.find(class_ = 'b_attribution').find('cite').text
            caption = j.find('div', {'class': 'b_caption'}).text
            title = header.text
            link = header.find('a')['href']
            description = caption.replace(path, '')

            title = clean(title, no_emoji=True)
            insert_values.append((engine_id, keyword_id, title, link, path, description, 0, bpage+1))

        # Retrieve the ads
        ads = soup.find_all('div',{'class':'sb_add sb_adTA'})
        for j in ads:
            header = j.find('h2')
            path = j.find(class_ = 'b_attribution').find('cite').text
            caption = j.find('div', {'class': 'b_caption'}).text
            title = header.text
            links = header.find('a')['href']
            description = caption.replace(path, '')

            title = clean(title, no_emoji=True)
            insert_values.append((engine_id, keyword_id, title, link, path, description, 1, bpage+1))

        # Create next page url
        bing_url = bing+nextpage
        bpage = bpage + 1

#########################
# 3. Insert search result
#########################
# Insert search result
try:
    sql = "INSERT INTO stg_results (engine_id, keyword_id, title, link, path, description, ad_flag, page) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    mycursor.executemany(sql, insert_values)        
    mydb.commit()
    # print(mycursor.rowcount, "Record inserted successfully")
except mysql.connector.Error as error:
    print("Failed to insert record into MySQL table {}".format(error))


# Get rid of result duplicate without ads
mycursor.execute("SELECT * FROM stg_results WHERE ad_flag = 0 ORDER BY created_at DESC, id DESC LIMIT %s", (len(insert_values),))
myresult = mycursor.fetchall()

for x in myresult:
    sql = "SELECT COUNT(id) FROM pub_results WHERE keyword_id = %s and link = %s"
    val = (x[2], x[6])
    mycursor.execute(sql, val)
    pubresult = mycursor.fetchone()
    if pubresult[0] == 0: 
        sql = "INSERT INTO pub_results (keyword_id, title, link, path, description) VALUES (%s, %s, %s, %s, %s)"
        val = (x[2], x[5], x[6], x[7], x[8])
        mycursor.execute(sql, val)
mydb.commit()


#################################
# 4. Extracting each contents
#################################

# Select non duplicate result for the search query
mycursor.execute("SELECT * FROM pub_results WHERE keyword_id = %s", (keyword_id,))
myresult = mycursor.fetchall()

# Delete stopwords from keyword
stop_words = set(stopwords.words('english'))
word_tokens = word_tokenize(term)
filtered_keyword = [w for w in word_tokens if not w.lower() in stop_words]

ocr = OCRConvertor()

insert_values = []
for x in myresult:
    # Check if result_id already exist in table
    mycursor.execute("SELECT COUNT(result_id) FROM result_details WHERE result_id = %s", (x[0],))
    pubresult = mycursor.fetchone()
    if pubresult[0] == 0:
        ####################
        # Process OCR
        ####################
        url = x[3]
        text = ''
        status = 'success'
        # print(url)
        if url.endswith('.pdf'):
            text, status = ocr.ocr_pdf(url)
            link_type = 'PDF'
            info_type = 'OCR_text'

        elif (url.endswith('.jpg')) | (url.endswith('.jpeg')) | (url.endswith('.png')):
            text = ocr.ocr_image(url)
            link_type = 'image'
            info_type = 'OCR_text'

        #################################
        # Process web content
        #################################
        else:
            if 'ebay.com' in url:
                status = 'Timeout'
            else:
                text, status = get_text_contents(url)
                text = clean(text, no_emoji=True)
            link_type = 'webpage'
            info_type = 'text'


        frequency = 0
        each_word = []
        for word in filtered_keyword:
            num = text.lower().count(word.lower())
            each_word.append(word + ': ' + str(num))
            frequency += num

        insert_values.append((x[0], link_type, info_type, text, frequency, ", ".join(each_word), status))

#################################
# 5. Insert extracted contents
#################################
try:
    sql = "INSERT INTO result_details (result_id, link_type, info_type, content_details, frequency, each_frequency, status) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    mycursor.executemany(sql, insert_values)
    mydb.commit()
except mysql.connector.Error as error:
    print("Failed to insert record into MySQL table {}".format(error))


# #################################
# # 6. Get search result
# #################################
mycursor.execute("SELECT r.title, r.link, r.description, d.frequency, d.each_frequency, d.status FROM pub_results r, result_details d WHERE r.id = d.result_id AND r.keyword_id = %s AND d.status = 'success' ORDER BY d.frequency DESC, r.created_at", (keyword_id,))
myresult = mycursor.fetchall()

row_headers=[x[0] for x in mycursor.description]
json_data = []
for result in myresult:
    json_data.append(dict(zip(row_headers,result)))

mycursor.execute("SELECT r.title, r.link, r.description, d.frequency, d.each_frequency, d.status FROM pub_results r, result_details d WHERE r.id = d.result_id AND r.keyword_id = %s AND d.status != 'success' ORDER BY d.frequency DESC, r.created_at", (keyword_id,))
myresult = mycursor.fetchall()

for result in myresult:
    json_data.append(dict(zip(row_headers,result)))

print(json.dumps(json_data))

mycursor.close()
