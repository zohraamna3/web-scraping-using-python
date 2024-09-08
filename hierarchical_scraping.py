import requests
from bs4 import BeautifulSoup
import pandas as pd
from googletrans import Translator
import json
translator = Translator()
url="https://codigo-postal.co/eeuu/"
r=requests.get(url)
print(r)
source=BeautifulSoup(r.text,"lxml")
#print(soup.prettify())
country_table=source.find("table",class_="table table-responsive table-striped table-condensed table-hover")
#print(table)
country_table_thead=country_table.find("thead")
columns=country_table_thead.find_all("th")
col=[]

for i in columns[1:]:
    tem=i.text
    try:
        translated_text = translator.translate(tem.strip(), dest='en').text
        col.append(translated_text)
    except Exception as e:
        print(f"Translation error: {e}")
        tem="state abbreviation"
        col.append(tem)



df=pd.DataFrame(columns=col)

tbody=country_table.find("tbody")
rows=tbody.find_all("tr")
for i in rows:
    data = i.find_all("td")
    row = [tr.text for tr in data]

    l=len(df)
    df.loc[l]=row[1:]


#collecting states urls in urls[]
urls=[]
for i in range(len(rows)):
    row = rows[i]
    row=row.find_all("td")
    ro=[tr.text for tr in row]
    if " " in ro[2]:
        ro[2]=ro[2].replace(" ","-")
        url1 = "https://codigo-postal.co/eeuu/"+ro[2].lower()+"/"
    else:
        url1 = "https://codigo-postal.co/eeuu/" + ro[2].lower() + "/"
    urls.append(url1)


main_city=[]
cities=[]
links=[]
city_col=[]
city_col_results=[]

#print(urls)
flag=True
flag2=True
last_col=[]
last_rows=[]
last_detail={}
for i in urls[43:44]:
    print(i)
    r = requests.get(i)
    print(r)
    source1 = BeautifulSoup(r.text, "lxml")
    ul=source1.find("ul",class_="column-list")
    li=ul.find_all("li")

    for element in li:
        city=element.text
        cities.append(city)
        links.append(element.find("a").get('href'))
    #print(len(links))
    print(len(links))
    for link in range(0,586 ):

        r1 = requests.get(links[link])
        print(r1)
        soup1 = BeautifulSoup(r1.text, "lxml")
        table=soup1.find("table",class_="table table-responsive table-striped table-condensed table-hover")
        if table is None:
            print(f"Warning: No table found for URL {links[link]}")
            with open("not working links.txt","a")as file:
                file.write(links[link]+"\n")
            continue
        thead = table.find("thead")
        city_columns = thead.find_all("th")
        if flag:
            for i in city_columns:
                tem = i.text
                city_col.append(translator.translate(tem,dest='en').text)
            flag=False
        tbody = table.find("tbody")
        city_rows = tbody.find_all("tr")

        for i in city_rows:
            data = i.find_all("td")
            row = [tr.text for tr in data]
            c_link=i.find("a").get('href')
            print(c_link)

            city_link="https://codigo-postal.co/eeuu/cp/"+str(row[2])+"/"
            city_detail=dict(zip(city_col,row))
            #main_city.append(city_detail)


            r2=requests.get(city_link)
            print(city_link)
            print(r2)
            soup2=BeautifulSoup(r2.text,"lxml")
            table2=soup2.find("table",class_="table table-responsive table-striped table-condensed table-hover")
            if table2 is None:
                print(f"Warning: No detailed table found for URL {city_link}")
                continue
            thead2 = table2.find("thead")
            columns2 = thead2.find_all("th")
            detail_table=soup2.find("table",class_="table table-condensed table-striped")
            if detail_table:
                    detail_tbody_th=detail_table.find_all("th")

                    if flag2:
                        for i in columns2:
                            tem = i.text
                            last_col.append(translator.translate(tem,dest='en').text)
                        for th in detail_tbody_th[4:]:
                            last_col.append(translator.translate(th.text,dest='en').text)
                        flag2=False
                    tbody2 = table2.find("tbody")
                    rows2 = tbody2.find_all("tr")
                    last_detail = {col: [] for col in last_col}
                    detail_tbody_td = detail_table.find_all("td")



                    for row in rows2:
                        data = row.find_all("td")
                        row = [tr.text for tr in data]

                        for col, value in zip(last_col, row):
                            last_detail[col].append(value)
                    detail_td = [td.text for td in detail_tbody_td[4:]]
                    for col,value in zip(last_col[4:],detail_td):
                        last_detail[col].append(value)

            else:
                    if flag2:
                        for i in columns2:
                            tem = i.text
                            last_col.append(translator.translate(tem,dest='en').text)
                        flag2 = False
                    tbody2 = table2.find("tbody")
                    rows2 = tbody2.find_all("tr")
                    last_detail = {col: [] for col in last_col}
                    for row in rows2:
                        data = row.find_all("td")
                        row = [tr.text for tr in data]

                        for col, value in zip(last_col, row):
                            last_detail[col].append(value)

            city_detail["Postal code"] = last_detail
            main_city.append(city_detail)



#print(main_city)
#print(city_links)
df["cities"]=pd.NA
df.at[5,"cities"]=main_city
records = df.to_dict(orient='records')


nested_json = {
    'Data': records
}

# Convert to JSON string
json_str = json.dumps(nested_json, indent=4)

with open('united states zip codes.json', 'w') as file:
    file.write(json_str)

