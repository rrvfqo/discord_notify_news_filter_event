'''
從公開資訊觀測站的rss xml截取即時重大訊息，並過濾出特定關鍵字的訊息
'''

import requests
from datetime import datetime, timezone
from bs4 import BeautifulSoup 
import re  
import json
import os

# 關鍵字
keywords_big_news = ['併購', '擴廠', '增資', '發債', '擴廠', '減資', '合併', '分割', '重組', '購買', 
                    '出售', '收購', '取得' ,'處分' ,'澄清媒體報導', '自結', '受惠', '減產', '通過投資',
                    '合作備忘錄', '申報轉讓', '變更每股面額', '第一期', '第二期', '第三期', '盈餘分配']

keywords_outoftheRed = ['自結', '由虧轉盈']

keywords_supervisor_change = ['董事長異動', '總經理異動', '董事異動']

# 公開資訊觀測站、即時重大訊息網站
big_news_url = "https://mopsov.twse.com.tw/nas/rss/mopsrss201001.xml"

# 紀錄已發送的重大訊息
sent_big_news_file = 'sent_big_news.json'
visited_links_file = 'visited_links.json'
last_checked_date_file = 'last_checked_date.txt'

# 讀取已發送的重大訊息
if os.path.exists(sent_big_news_file):
    try:
        with open(sent_big_news_file, 'r') as f:
            sent_big_news = set(json.load(f))
            print(f"sent_big_news = {sent_big_news}")
    except json.JSONDecodeError:
        print(f"Warning: {sent_big_news_file} is empty or invalid. Initializing empty set.")
        sent_big_news = set()
else:
    sent_big_news = set()

# 讀取已訪問的連結
if os.path.exists(visited_links_file):
    try:
        with open(visited_links_file, 'r') as f:
            visited_links = set(json.load(f))
            # print(f"visited_links = {visited_links}")
    except json.JSONDecodeError:
        print(f"Warning: {visited_links_file} is empty or invalid. Initializing empty set.")
        visited_links = set()
else:
    visited_links = set()

# 讀取上次檢查日期
if os.path.exists(last_checked_date_file):
    with open(last_checked_date_file, 'r') as f:
        last_checked_date = f.read().strip()
        print(f"last_checked_date = {last_checked_date}")
else:
    last_checked_date = datetime.now(timezone.utc).strftime('%Y%m%d')
    with open(last_checked_date_file, 'w') as f:
        f.write(last_checked_date)

def check_new_big_news():
    global last_checked_date
    today = datetime.now(timezone.utc).strftime('%Y%m%d')
    
    # 如果跨日，清空 sent_announcements
    if today != last_checked_date:
        sent_big_news.clear()
        visited_links.clear()
        last_checked_date = today

         # 清空檔案內容
        with open(sent_big_news_file, 'w') as f:
            json.dump(list(sent_big_news), f)
        with open(visited_links_file, 'w') as f:
            json.dump(list(visited_links), f)
        with open(last_checked_date_file, 'w') as f:
            f.write(last_checked_date)

    new_big_news = analyze_big_news_page()
    # print(f"new_big_news = {new_big_news}")

    current_time = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
   
    if any(new_big_news[key] for key in new_big_news):
        # 處理新公告，例如發送通知
        print(f"有新的公告 - {current_time}")
        # for news in new_big_news:
        #     print(news)
    else:
        print(f"沒有新的公告 - {current_time}")

    # 將已發送的重大訊息和已訪問的連結存儲到檔案中
    with open(sent_big_news_file, 'w') as f:
        json.dump(list(sent_big_news), f)
        print(f"Updated {sent_big_news_file} with {list(sent_big_news)}")
    with open(visited_links_file, 'w') as f:
        json.dump(list(visited_links), f)
        print(f"Updated {visited_links_file} with {list(visited_links)}")

    return new_big_news

def analyze_big_news_page():
    # 取得今天的日期
    today = datetime.now(timezone.utc).date()

    # 發送請求並取得網頁內容
    response = requests.get(big_news_url)
    soup = BeautifulSoup(response.content, 'xml')

    # 初始化 分類結果
    big_news_list = []
    outoftheRed_list = []
    supervisor_change_list = []

    # 解析網頁中的每個 item
    items = soup.find_all('item')
    for item in items:
        title_tag = item.find('title')
        if title_tag and title_tag.get_text():
            title = title_tag.get_text()
        else:
            print("Warning: Missing or empty title in item")
            print(item)
            continue

        link_tag = item.find('link')
        if link_tag and link_tag.string:
            link = link_tag.string.strip()
        else:
            print(f"Warning: Missing or empty link in item")
            print(item)
            continue

        # 檢查是否已經訪問過該連結
        if link in visited_links:
            continue

        description_tag = item.find('description')
        if description_tag and description_tag.get_text():
            description = description_tag.get_text().strip()
        else:
            print("Warning: Missing or empty description in item")
            print(item)
            continue

        pub_date_tag = item.find('pubDate')
        if pub_date_tag and pub_date_tag.get_text():
            pub_date = pub_date_tag.get_text().strip()
            # 去掉 pub_date 中的 +0800
            pub_date = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %z').strftime('%a, %d %b %Y %H:%M:%S')
        else:
            print("Warning: Missing or empty pubDate in item")
            print(item)
            continue

        # 提取股票代碼和公司名稱
        try:
            stock_id, company_name = title.split(')')[0].split('(')[1], title.split(')')[1].split('-')[0].strip()
        except IndexError:
            print("Warning: Title format is incorrect")
            print(item)
            continue

        # 過濾時間不是今天的項目
        pub_date_obj = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S').date()
        if pub_date_obj != today:
            continue

        # 檢查 link 中 "TYPEK=" 之後到第一個 "&" 之間的文字
        typek_match = re.search(r'TYPEK=(.*?)&', link)
        if not typek_match or typek_match.group(1) not in ['otc', 'sii']:
            continue

        # 檢查是否已經發送過
        news_id = stock_id + description + pub_date
        if news_id in sent_big_news:
            continue

        # 訪問每個 link 的網址並檢查其說明項內容
        link_response = requests.get(link)
        link_soup = BeautifulSoup(link_response.content, 'lxml')
        link_description = link_soup.get_text()

        # 檢查是否符合關鍵字
        if any(keyword in link_description for keyword in keywords_big_news):
            big_news_list.append({
                'stock_id': stock_id,
                'name': company_name,
                'date': pub_date,
                'url': link,
                'title': description
            })
        if any(keyword in link_description for keyword in keywords_outoftheRed):
            outoftheRed_list.append({
                'stock_id': stock_id,
                'name': company_name,
                'date': pub_date,
                'url': link,
                'title': description
            })
        if any(keyword in link_description for keyword in keywords_supervisor_change):
            supervisor_change_list.append({
                'stock_id': stock_id,
                'name': company_name,
                'date': pub_date,
                'url': link,
                'title': description
            })

        # 記錄已發送的重大訊息
        sent_big_news.add(news_id)
        # 記錄已訪問的連結
        visited_links.add(link)

    # 倒轉列表順序
    big_news_list.reverse()
    outoftheRed_list.reverse()
    supervisor_change_list.reverse()

    print(f"big_news_list = {big_news_list}")
    print(f"outoftheRed_list = {outoftheRed_list}")
    print(f"supervisor_change_list = {supervisor_change_list}")

    return {
        'big_news': big_news_list,
        'outoftheRed': outoftheRed_list,
        'supervisor_change': supervisor_change_list
    }

if __name__ == '__main__':
    check_new_big_news()