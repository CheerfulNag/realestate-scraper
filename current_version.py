import random
from bs4.element import Script
from requests_html import HTMLSession,AsyncHTMLSession
import csv
import time

def detailed_links_scraper(url):
    global links
    links = []
    with HTMLSession() as session:
        an = random.randint(0,19)
        proxy = proxies[an]
        s = session.get(url,proxies={'http': proxy})
        s.html.render()
        objects = list(s.html.find("div#properties div.property-box a[href*='https://palace-invest.ro']"))
        n = 0
        for object in objects:
            object = object.attrs
            link = object['href']
            links.append(link)


async def detailed_link_reader_child(url):
    a = random.randint(0,1)
    time.sleep(a)
    an = random.randint(0,19)
    proxy = proxies[an]

    done = False
    while not done:
        try: 
            r = await asession.get(url,proxies={'http': proxy})
            await r.html.arender(timeout = 100)
            done = True     
        except:
            print(proxy)
            time.sleep(30)

    object_id = None
    try:
        object_id = ((r.html.find('div.display-table-cell span.property-id',first = True).text).split(" "))[1]
    except:
        pass
    rent_price = None
    sell_price = None
    rent_price_parrent = (r.html.find('div.price',first = True).text)
    try:
        if ("lună" in rent_price_parrent) and ("Vanzare" not in rent_price_parrent):
            rent_price = rent_price_parrent.split("€")[0].replace(",","")
        elif ("Vanzare" in rent_price_parrent) and ("Inchiriere" in rent_price_parrent):
            rent_price_parrent = rent_price_parrent.replace("\n",'').split(")")
            first_price = ((rent_price_parrent[0]).split("€"))[0]
            second_price=((rent_price_parrent[1]).split("€"))[0]
            if ("Vanzare" in first_price):
                sell_price = ((first_price.split(" "))[1]).replace(",","")
            elif("Inchiriere" in first_price):
                rent_price = ((first_price.split(" "))[1]).replace(",","")
            if ("Vanzare" in second_price):
                sell_price = ((second_price.split(" "))[1]).replace(",","")
            elif("Inchiriere" in second_price):
                rent_price = ((second_price.split(" "))[1]).replace(",","")
        elif ("lună" not in rent_price_parrent) and ("Vanzare" not in rent_price_parrent) and ("Inchiriere" not in rent_price_parrent):
            sell_price = rent_price_parrent.split("€")[0].replace(",","")
    except:
        print(url)
    area_name = None
    try:
        area_name = r.html.find("div.display-table-cell span.region",first= True).text
    except:
        pass
    stats_objects = r.html.find("div.property-info-section ul li")
    whole_area = None
    usable_area = None
    construction_year = None
    rooms = None
    floor = None
    floors_in_building = None
    for x in stats_objects:
        x = x.text
        try:
            if ("utilă" in x):
                usable_area = (((x.split(":")[1]).replace(" ",'')).split("m"))[0]
        except:
            print("Utila   ", url)
        try:
            if ("totală" in x):
                whole_area = (((x.split(":")[1]).replace(" ",'')).split("m"))[0]
        except:
            print("Totala   ", url)

        if ("Anul constructiei" in x):
            construction_year = ((x.split(":")[1])).replace(" ",'')
        elif ("Camere" in x):
            rooms = ((x.split(":")[1])).replace(" ",'')

        if ("Regim" in x):
            parrent_floors = x.replace(" ","").split(":")[1].split("/")
            floor = parrent_floors[0]
            floors_in_building = "1"
            for d in range(0,101):
                d = str(d)
                if d in parrent_floors[1]:
                    floors_in_building = d


    title = r.html.find("div.display-table-cell h1.title",first= True).text
    description = r.html.find("div.property-info-section p",first=True).text
    img_links_parrent = r.html.find("div#property-carousel a")
    img_links = ''
    for x in img_links_parrent:
        x = x.attrs
        x = x['href']
        img_links+=(f"{x}; ")
    agent_name = r.html.find("div#agent span.name",first = True).text
    agent_numb_parrent = r.html.find("div#agent div.agent-contact a")
    try:
        agent_numb = (f"{(agent_numb_parrent[0]).text};{(agent_numb_parrent[1]).text}")
    except:
        agent_numb = (f"{(agent_numb_parrent[0]).text}")

    if ("penthouse" in title) or ("Penthouse" in title):
        object_type = "penthouse"
    elif ("Penthouse" not in title and 'penthouse' not in title) and ('duplex' in title or 'Duplex' in title):
        object_type = "duplex"
    else:
        object_type = "apartament"

    for_none = None
    sell_tax = None
    teresse_area = None

    record = (for_none,object_id,"apartament","activa",for_none,object_type,for_none,for_none,"finalizata",for_none,sell_price,sell_tax,rent_price,for_none,for_none,rooms,construction_year,whole_area,usable_area,teresse_area,for_none,for_none,for_none,for_none,area_name,"1",for_none,for_none,'1',floor,floors_in_building,for_none,"bucuresti","bucuresti",area_name,agent_name,for_none,for_none,title,description,agent_numb,for_none,for_none,for_none,for_none,img_links)
    if (record not in records):
        records.append(record)


def detailed_links_reader():
    global headers
    headers = {
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Encoding':'gzip, deflate, br',
        'Accept-Language':'en-US,en;q=0.5',
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:93.0) Gecko/20100101 Firefox/93.0'
    }

    global asession 
    for d in range(0,len(links),5):
        links1 = []
        asession = AsyncHTMLSession()
        for x in range(d,d+5):
            try:
                links1.append(links[x])
            except:
                pass
            all_responses = asession.run(*[lambda url=url: detailed_link_reader_child(url) for url in links1])
            n = random.randint(1,5)
            time.sleep(n) 
        print(f"{d+5} complete.")



import random

def csv_saver():
    with open("results.csv","w",newline="",encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(['ID',"ID intern","Tip proprietate","Valabilitate","Status palnie","Tip apartament","Tip vila","Compartimentare","Stadiu constructie",'Orientare','Pret vanzare','TVA Vanzare','Pret inchiriere','TVA Inchiriere','Inchiriat pana la','Nr. camere','An constr.',"S. construita",'S. utila','S. balcoane','S. terasa','S. totala','S. teren','Deschidere','Strada','Nr. strada','Bloc','Scara','Nr. apartament','Etaj','Nr. et. Cladire','Reper','Judet','Localitate','Zona','Agent','Ansamblu rezidential','Model apartament','Titlu','Descriere','Contact','Dotari: Dotari','Dotari: Sistem incalzire','Dotari: Bucatarie','Dotari: (nume grup dotari)','POZE PROPRIETATI'])
        writer.writerows([x for x in records])


def main(url):
    print("Scraping")
    detailed_links_scraper(url)
    print("Detailed links scraped")
    detailed_links_reader()
    print("Complete")


proxies = ["185.76.215.54:80","108.21.233.5:8888","144.76.116.242:80","165.227.71.60:80","176.110.166.82:8080","23.102.102.218:80","93.158.214.156:3128","93.158.214.154:3128","87.255.13.217:8080","104.233.204.77:88","104.233.204.73:82","104.233.204.75:82","154.16.63.16:3128","104.233.204.76:82","143.198.77.84:9300","115.79.198.18:55443","176.9.75.42:8080","158.69.27.94:5566","66.183.100.156:3128","95.216.194.46:1081"]

url_rent = "https://palace-invest.ro/ro/results/?id-keyword=&type%5B%5D=382&contract_type=for-rent&submit=Filtreaza"
url_sell = "https://palace-invest.ro/ro/results/?id-keyword=&type%5B%5D=382&contract_type=for-sale&submit=Filtreaza"
records = []


main(url_rent)
main(url_sell)
csv_saver()