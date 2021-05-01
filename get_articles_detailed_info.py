import re
import json
import time
import urllib.request
import requests
import csv
from bs4 import BeautifulSoup
from headers_config import headers

# write to csv file
def write_to_csv(filename, head_line, *info_list):
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(head_line.split('\t'))
        for row in info_list:
            row_list = row.split('\t')
            writer.writerow(row_list)


def get_article_detailed_info(url):
    article_info = {}
    print (url)
    r = session.get(url, headers=headers)
    r_soup = BeautifulSoup(r.text, "html.parser")
    re_pattern = "发表于 20[0-9]{2}"
    try:
        contents = []
        for sibling in r_soup.find_all("h3", text=re.compile(re_pattern))[0].next_sibling.next_sibling.next_siblings:
            soup = BeautifulSoup(str(sibling), 'lxml')
            if len(soup.find_all('p')) > 0:
                content = soup.find_all('p')[0].text.strip()
                if content is not None and content !='':
                    contents.append(content.strip())
        article_info['all_content'] = (" ".join(contents[0:100]).strip('\t'))
    except:
        article_info['all_content'] = 'N/A'
    try:
        article_info['author'] = r_soup.select('a[id="authorDisplayName"]')[0].text.strip() 
    except:
        article_info['author'] = 'N/A'
    try:
        article_info['city'] = r_soup.select('li[style="display: block;"]')[0].h4.text
    except:
        article_info['city'] = 'N/A'
    try:
        article_info['days'] = r_soup.find_all("i", class_="days")[0].next_sibling.replace("天数：","")
    except:
        article_info['days'] = 'N/A'
    try:
        article_info['times'] = r_soup.find_all("i", class_="times")[0].next_sibling.replace("时间：","")
    except:
        article_info['times'] = 'N/A'
    try:
        article_info['costs'] = r_soup.find_all("i", class_="costs")[0].next_sibling.replace("人均：","")
    except:
        article_info['costs'] = 'N/A'
    try:
        article_info['whos'] = r_soup.find_all("i", class_="whos")[0].next_sibling.replace("和谁：","")
    except:
        article_info['whos'] = 'N/A'
    try:
        article_info['plays'] = r_soup.find_all("i", class_="plays")[0].next_sibling.replace("玩法：","")
    except:
        article_info['plays'] = 'N/A'
    try:
        poi = [ x.text for x in r_soup.find("div", class_="author_poi").find_all("a") ]
        article_info['places'] = " ".join(poi)
    except:
        article_info['places'] = 'N/A'
    try:
        article_info['catalog'] = "".join([ x.text for x in r_soup.find_all("div", class_="ctd_yj_list route_bar")[0].find_all("a") ]) 
    except:
        article_info['catalog'] = 'N/A'
    return article_info
    

def get_articles():
    total_page = 200
    index = 1
    data = {}
    article_info_list = []

    for i in range(index, total_page+1):
        counter = 1

        json_url = "https://you.ctrip.com/searchsite/travels/?query=杭州&isRecommended=1&PageNo=" + str(i)

        res = session.get(json_url, headers=headers)

        res_soup = BeautifulSoup(res.text, "html.parser")
        main_contain = res_soup.find_all("li", class_="cf")

        for each in main_contain:
            articles_info = each.find_all("a")
            tag = str(index) + "-" + str(counter)
            data[tag] = {}
            data[tag]["url"] = "https://you.ctrip.com" + articles_info[1]["href"]
            data[tag]["title"] = articles_info[1].text
            data[tag]["date"] = re.findall(r"[0-9]+-[0-9]+-[0-9]+", str(articles_info[2].next_sibling))
            try:
                info = get_article_detailed_info(data[tag]["url"])
                article_info = "{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t{9}\t{10}\t{11}\t{12}" \
                                        .format(
                                            data[tag]["url"],data[tag]["date"],
                                            data[tag]["title"],info['author'],info['city'],
                                            info['days'],info['times'],info['costs'],info['whos'],
                                            info['places'],info['plays'],info['catalog'],info['all_content'])
            except Exception as e:
                print (e)
                article_info = "{0}\tinternal_running_error" .format(data[tag]["url"])
            article_info_list.append(article_info)
            #write_to_csv(f_csv, head_instruction, *article_info_list)
            #print (article_info_list)

            print("Progress: %d # %d" % (int(index), int(counter)))

            counter += 1

        index += 1
        time.sleep(1)

    f = open("articles_info", "a")
    try:
        f.write(json.dumps(data))
    except IndexError as e:
        pass
    except ValueError as e:
        pass
    finally:
        f.close()
    return article_info_list

if __name__ == '__main__':
    f_csv = 'article.csv'
    head_instruction = "页面网址\t发表时间\t标题\t作者\t城市\t天数\t旅游时间\t人均\t和谁\t作者去了这些地方\t玩法\t游记目录\t正文"
    with requests.Session() as session:
        articles_info_list = get_articles()
        write_to_csv(f_csv, head_instruction, *articles_info_list)
        #get_article_detailed_info("https://you.ctrip.com/travels/hangzhou14/2180442.html")
