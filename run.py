
import time
import os
import sys
import requests

from filter_news import check_new_big_news  # 匯入函式


def notify_discord_webhook_big_news(msg):
    url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not url:
        print("錯誤：找不到 DISCORD_WEBHOOK_URL 環境變數或網址為空，無法發送 Discord 通知。")
        return
    headers = {"Content-Type": "application/json"}
    data = {"content": msg, "username": "即時重大訊息通知"}
    res = requests.post(url, headers = headers, json = data) 
    if res.status_code in (200, 204):
            print(f"Request fulfilled with response: {res.text}")
    else:
            print(f"Request failed with response: {res.status_code}-{res.text}")

def notify_discord_webhook_supervisor_change(msg):
    url = os.environ.get("DISCORD_WEBHOOK_URL_SUPERVISOR")
    if not url:
        print("錯誤：找不到 DISCORD_WEBHOOK_URL_SUPERVISOR 環境變數或網址為空，無法發送 Discord 通知。")
        return
    headers = {"Content-Type": "application/json"}
    data = {"content": msg, "username": "稽核主管異動"}
    res = requests.post(url, headers = headers, json = data) 
    if res.status_code in (200, 204):
            print(f"Request fulfilled with response: {res.text}")
    else:
            print(f"Request failed with response: {res.status_code}-{res.text}")

def notify_discord_webhook_outoftheRed(msg):
    url = os.environ.get("DISCORD_WEBHOOK_URL_OUTOFRED")
    if not url:
        print("錯誤：找不到 DISCORD_WEBHOOK_URL_OUTOFRED 環境變數或網址為空，無法發送 Discord 通知。")
        return
    headers = {"Content-Type": "application/json"}
    data = {"content": msg, "username": "自結"}
    res = requests.post(url, headers = headers, json = data) 
    if res.status_code in (200, 204):
            print(f"Request fulfilled with response: {res.text}")
    else:
            print(f"Request failed with response: {res.status_code}-{res.text}")

def notify_discord_webhook_mou(msg):
    # 優先從環境變數讀取，若無則使用預設網址
    url = os.environ.get("DISCORD_WEBHOOK_URL_MOU")
    if not url:
        print("錯誤：找不到 DISCORD_WEBHOOK_URL_MOU 環境變數或網址為空，無法發送 Discord 通知。")
        return
    headers = {"Content-Type": "application/json"}
    data = {"content": msg, "username": "MOU/合作備忘錄"}
    res = requests.post(url, headers = headers, json = data) 
    if res.status_code in (200, 204):
            print(f"Request fulfilled with response: {res.text}")
    else:
            print(f"Request failed with response: {res.status_code}-{res.text}")



def generate_msg():
    new_announcements = check_new_big_news()  # 呼叫函式取得新公告

    if new_announcements['big_news']:
        msg_big_news = '\n\n'.join(
            f"{announcement['date']}\n{announcement['stock_id']} {announcement['name']}\n{announcement['title']}\n{announcement['url']}"
            for announcement in new_announcements['big_news']
        )
        
        # 如果msg超過2000字元，分段發送
        if len(msg_big_news) > 2000:
            msg_big_news_list = [msg_big_news[i:i+2000] for i in range(0, len(msg_big_news), 2000)]
            for msg_big_news in msg_big_news_list:
                notify_discord_webhook_big_news(msg_big_news)
        else:
            notify_discord_webhook_big_news(msg_big_news)
    else:
        print("重大 is none.")

    time.sleep(3)

    if new_announcements['mou_news']:
        msg_mou = '\n\n'.join(
            f"{announcement['date']}\n{announcement['stock_id']} {announcement['name']}\n{announcement['title']}\n{announcement['url']}"
            for announcement in new_announcements['mou_news']
        )
        
        # 如果msg超過2000字元，分段發送
        if len(msg_mou) > 2000:
            msg_mou_list = [msg_mou[i:i+2000] for i in range(0, len(msg_mou), 2000)]
            for msg_mou in msg_mou_list:
                notify_discord_webhook_mou(msg_mou)
        else:
            notify_discord_webhook_mou(msg_mou)
    else:
        print("MOU is none.")

    time.sleep(3)

    if new_announcements['outoftheRed']:
        msg_outoftheRed = '\n\n'.join(
            f"{announcement['date']}\n{announcement['stock_id']} {announcement['name']}\n{announcement['title']}\n{announcement['url']}"
            for announcement in new_announcements['outoftheRed']
        )

        # 如果msg超過2000字元，分段發送
        if len(msg_outoftheRed) > 2000:
            msg_outoftheRed_list = [msg_outoftheRed[i:i+2000] for i in range(0, len(msg_outoftheRed), 2000)]
            for msg_outoftheRed in msg_outoftheRed_list:
                notify_discord_webhook_outoftheRed(msg_outoftheRed)
        else:
            notify_discord_webhook_outoftheRed(msg_outoftheRed)
    else:
        print("自結 is none.")

    time.sleep(3)

    if new_announcements['supervisor_change']:
        msg_supervisor_change = '\n\n'.join(
            f"{announcement['date']}\n{announcement['stock_id']} {announcement['name']}\n{announcement['title']}\n{announcement['url']}"
            for announcement in new_announcements['supervisor_change']
        )

        # 如果msg超過2000字元，分段發送
        if len(msg_supervisor_change) > 2000:
            msg_supervisor_change_list = [msg_supervisor_change[i:i+2000] for i in range(0, len(msg_supervisor_change), 2000)]
            for msg_supervisor_change in msg_supervisor_change_list:
                notify_discord_webhook_supervisor_change(msg_supervisor_change)
        else:
            notify_discord_webhook_supervisor_change(msg_supervisor_change)
    else:
        print("主管異動 is none.")





def signal_handler(sig, frame):
    global running
    print('Stopping the scheduler...')
    running = False
    sys.exit(0)

if __name__ == "__main__":

    generate_msg()  # 執行一次
