'''
從公開資訊觀測站的rss xml截取即時重大訊息，並過濾出特定關鍵字的訊息
'''

import requests
from datetime import datetime, timezone
from bs4 import BeautifulSoup 
import re  
# import sys

# 關鍵字
keywords_big_news = ['併購', '擴廠', '增資', '發債', '擴廠', '減資', '合併', '分割', '重組', '購買', 
                    '出售', '收購', '取得' ,'處分' ,'澄清媒體報導', '自結', '受惠', '減產', '通過投資',
                    '合作備忘錄', '申報轉讓', '變更每股面額', '第一期', '第二期', '第三期', '盈餘分配']

keywords_outoftheRed = ['自結', '由虧轉盈']

keywords_supervisor_change = ['董事長異動', '總經理異動', '董事異動']

# 公開資訊觀測站、即時重大訊息網站
big_news_url = "https://mopsov.twse.com.tw/nas/rss/mopsrss201001.xml"

# 紀錄已發送的重大訊息
sent_big_news = set()

# 紀錄上次檢查日期
last_checked_date = datetime.now().strftime('%Y%m%d')

def check_new_big_news():
    global last_checked_date
    today = datetime.now(timezone.utc).strftime('%Y%m%d')
    
    # 如果跨日，清空 sent_announcements
    if today != last_checked_date:
        sent_big_news.clear()
        last_checked_date = today

    # new_big_news = get_big_news()
    new_big_news = analyze_big_news_page()

    current_time = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
   
    if new_big_news:
        # 處理新公告，例如發送通知
        print(f"有新的公告 - {current_time}")
        # for news in new_big_news:
        #     print(news)
    else:
        print(f"沒有新的公告 - {current_time}")

    return new_big_news

def analyze_big_news_page():
    # 取得今天的日期
    today = datetime.now().date()

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
        if title_tag:
            title = title_tag.get_text()
        else:
            print("Warning: Missing title in item")
            print(item)
            # sys.exit("Error: Missing title in item. Program terminated.")
            continue


        link_tag = item.find('link')
        if link_tag and link_tag.string:
            link = link_tag.string.strip()
            # print(link)
            # ...existing code...
        else:
            print(f"Warning: Missing link in item")
            print(item)
            # sys.exit("Error: Missing link in item. Program terminated.")
            continue

        description_tag = item.find('description')
        if description_tag:
            description = description_tag.get_text().strip()
        else:
            print("Warning: Missing description in item")
            print(item) 
            #sys.exit("Error: Missing description in item. Program terminated.")
            continue

        pub_date_tag = item.find('pubDate')
        if pub_date_tag:
            pub_date = pub_date_tag.get_text().strip()
            # 去掉 pub_date 中的 +0800
            pub_date = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %z').strftime('%a, %d %b %Y %H:%M:%S')
        else:
            print("Warning: Missing pubDate in item")
            print(item)
            #sys.exit("Error: Missing pubDate in item. Program terminated.")
            continue

        
        # 提取股票代碼和公司名稱
        stock_id, company_name = title.split(')')[0].split('(')[1], title.split(')')[1].split('-')[0].strip()

        # print(f"股票代碼: {stock_id}, 公司名稱: {company_name}, 發佈日期: {pub_date}, 主旨: {description}, 公告連結: {link}")

        # 過濾時間不是今天的項目
        pub_date_obj = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S').date()
        if pub_date_obj != today:
            continue

        # 檢查 link 中 "TYPEK=" 之後到第一個 "&" 之間的文字
        typek_match = re.search(r'TYPEK=(.*?)&', link)
        if not typek_match or typek_match.group(1) not in ['otc', 'sii']:
            continue

        # 檢查是否已經發送過
        news_id = stock_id + description
        if news_id in sent_big_news:
            continue

        # 訪問每個 link 的網址並檢查其說明項內容
        link_response = requests.get(link)
        link_soup = BeautifulSoup(link_response.content, 'html.parser')
        link_description = link_soup.get_text()
        # print(link_description)

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

    # print(f'big_news_list = {big_news_list}')
    # print(f'outoftheRed_list = {outoftheRed_list}') 
    # print(f'supervisor_change_list = {supervisor_change_list}')

    # 倒轉列表順序
    big_news_list.reverse()
    outoftheRed_list.reverse()
    supervisor_change_list.reverse()

    return {
        'big_news': big_news_list,
        'outoftheRed': outoftheRed_list,
        'supervisor_change': supervisor_change_list
    }

# def filter_big_news(news_list):
#     return

# def filter_outoftheRed(news_list):
#     return

# def filter_supervisor_change(news_list):
#     return

if __name__ == '__main__':
   
   analyze_big_news_page()
   
#    filter_big_news(news_list)