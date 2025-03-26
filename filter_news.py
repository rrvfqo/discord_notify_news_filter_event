'''
從公開資訊觀測站的rss xml截取即時重大訊息，並過濾出特定關鍵字的訊息
'''

import requests
from datetime import datetime, timezone, timedelta
from bs4 import BeautifulSoup
import re

# 關鍵字
keywords_big_news = ['併購', '擴廠', '增資', '發債', '擴廠', '減資', '合併', '分割', '重組', '購買',
                     '出售', '收購', '取得', '處分', '澄清媒體報導', '自結', '受惠', '減產', '通過投資',
                     '合作備忘錄', '申報轉讓', '變更每股面額', '第一期', '第二期', '第三期', '盈餘分配']

keywords_outoftheRed = ['自結', '由虧轉盈']

keywords_supervisor_change = ['董事長異動', '總經理異動', '董事異動']

# 公開資訊觀測站、即時重大訊息網站
big_news_url = "https://mopsov.twse.com.tw/nas/rss/mopsrss201001.xml"


def check_new_big_news():
    new_big_news = analyze_big_news_page()

    current_time = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

    if any(new_big_news[key] for key in new_big_news):
        # 處理新公告，例如發送通知
        print(f"有新的公告 - {current_time}")
    else:
        print(f"沒有新的公告 - {current_time}")

    return new_big_news


def analyze_big_news_page():
    # 取得當前時間和一小時前的時間
    now = datetime.now(timezone.utc)
    one_hour_ago = now - timedelta(hours=1)

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
        pub_date_tag = item.find('pubDate')
        if pub_date_tag and pub_date_tag.get_text():
            pub_date = pub_date_tag.get_text().strip()
            pub_date_obj = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %z')

            # 過濾時間不在最近一小時內的項目
            if pub_date_obj < one_hour_ago or pub_date_obj > now:
                continue
        else:
            print("Warning: Missing or empty pubDate in item")
            print(item)
            continue

        link_tag = item.find('link')
        if link_tag and link_tag.string:
            link = link_tag.string.strip()
        else:
            print(f"Warning: Missing or empty link in item")
            print(item)
            continue

        title_tag = item.find('title')
        if title_tag and title_tag.get_text():
            title = title_tag.get_text()
        else:
            print("Warning: Missing or empty title in item")
            print(item)
            continue

        description_tag = item.find('description')
        if description_tag and description_tag.get_text():
            description = description_tag.get_text().strip()
        else:
            print("Warning: Missing or empty description in item")
            print(item)
            continue

        # 提取股票代碼和公司名稱
        try:
            stock_id, company_name = title.split(')')[0].split('(')[1], title.split(')')[1].split('-')[0].strip()
        except IndexError:
            print("Warning: Title format is incorrect")
            print(item)
            continue

        # 檢查 link 中 "TYPEK=" 之後到第一個 "&" 之間的文字
        typek_match = re.search(r'TYPEK=(.*?)&', link)
        if not typek_match or typek_match.group(1) not in ['otc', 'sii']:
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