import schedule
import time
# import threading
# import signal
import sys
import requests

from filter_news import check_new_big_news  # 匯入函式


def notify_discord_webhook_big_news(msg):
    url = 'https://discord.com/api/webhooks/1326482818431193173/dvmxfFzu_oYt-pi93nhN9ZTHMymV2AgAfD14B4eRmbbWbwJuSqrQW-hVuhEyl7UL2pUm'
    headers = {"Content-Type": "application/json"}
    data = {"content": msg, "username": "即時重大訊息通知"}
    res = requests.post(url, headers = headers, json = data) 
    if res.status_code in (200, 204):
            print(f"Request fulfilled with response: {res.text}")
    else:
            print(f"Request failed with response: {res.status_code}-{res.text}")

def notify_discord_webhook_supervisor_change(msg):
    url = 'https://discord.com/api/webhooks/1326838042979467295/2ITsRRjDEnCOEPuCvUQJYiB6m_k5N0IueIc4GoGbNd7BVvFPtC9dTSuSmBg7j3vwC1mf'
    headers = {"Content-Type": "application/json"}
    data = {"content": msg, "username": "稽核主管異動"}
    res = requests.post(url, headers = headers, json = data) 
    if res.status_code in (200, 204):
            print(f"Request fulfilled with response: {res.text}")
    else:
            print(f"Request failed with response: {res.status_code}-{res.text}")

def notify_discord_webhook_outoftheRed(msg):
    url = 'https://discord.com/api/webhooks/1326843756980338709/c0BI3FICRazJkbkjb02AKKdeLmtvQmdVD-GbDE-SsZClsWcjzmlyBWHGLlOH9Z1C9gHd'
    headers = {"Content-Type": "application/json"}
    data = {"content": msg, "username": "自結"}
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

    time.sleep(10)

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

    time.sleep(10)

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


# def job():
     
    # msg = generate_msg()
    # if msg is None:
    #     print("No new announcements.")
    #     return
    #   # 如果msg超過2000字元，分段發送
    # if len(msg) > 2000:
    #     msg_list = [msg[i:i+2000] for i in range(0, len(msg), 2000)]
    #     for msg in msg_list:
    #         notify_discord_webhook(msg)
    #     return
    # else:
    #     notify_discord_webhook(msg)

schedule.every(30).minutes.do(generate_msg)
# schedule.every(30).seconds.do(job)

def run_schedule():
    while True:
        try:
            schedule.run_pending()
        except Exception as e:
            print(f"Error running scheduled job: {e}")
        time.sleep(1)

def signal_handler(sig, frame):
    global running
    print('Stopping the scheduler...')
    running = False
    sys.exit(0)

if __name__ == "__main__":

    generate_msg()  # 執行一次

    # # 設定停止信號處理
    # signal.signal(signal.SIGINT, signal_handler)

    # # 初始化 running 變數
    # running = True

    # # 啟動定時任務的背景執行緒
    # schedule_thread = threading.Thread(target=run_schedule)
    # schedule_thread.start()
