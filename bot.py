 # -*- coding: utf-8 -*-
import os
import requests
from flask import Flask, request, abort
from dotenv import load_dotenv

from linebot import WebhookParser
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    PushMessageRequest,
    TextMessage
)

# ====== 一、Flask & LINE Bot 基本設定 ======
app = Flask(__name__)

# LINE Channel Secret、Access Token以env檔載入
load_dotenv(load_dotenv(dotenv_path="./.env"))

CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")

# 初始化
parser = WebhookParser(CHANNEL_SECRET)
configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)

print("SECRET:", CHANNEL_SECRET)
print("TOKEN:", CHANNEL_ACCESS_TOKEN)

# 關鍵字設定
KEYWORD_RESPONSES = {
    "以前": "好了啦都2025了以前是多以前",
    "之前": "ㄏㄏ 又開始講古",
    "那個時候": "操勒都多久了",
    "那時候": "操勒都多久了",
    "年代": "幾歲了是在吵啥",
    "國小": "笑死還他媽國小",
    "國中": "煉銅癖沒人問你國中的事",
    "高中": "死老人幾歲了還在高中",
    "老了": "大家都知道老了不用講",
    "時代": "幾歲了是在吵啥"
}
#大小寫及部分關鍵字都觸發
IGNORE_CASE = True
PARTIAL_MATCH = True

def check_keywords(text: str) -> str | None:
    txt = text.lower() if IGNORE_CASE else text
    for kw, reply in KEYWORD_RESPONSES.items():
        key = kw.lower() if IGNORE_CASE else kw
        if (PARTIAL_MATCH and key in txt) or (not PARTIAL_MATCH and txt == key):
            return reply
    return None

# 私聊標記已讀
def mark_as_read(user_id: str):
    url = "https://api.line.me/v2/bot/message/markAsRead"
    headers = {
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    r = requests.post(url, json={"chat": {"userId": user_id}}, headers=headers)
    print("Mark as Read response:", r.status_code, r.text)

@app.route("/callback", methods=["POST"])
def callback():
    # 1. 讀原始 JSON 並印 debug
    data = request.get_json()
    print("🚀 收到原始 JSON：", data)

    # 2. 確保每個 event 都能被讀到
    events = data.get("events", [])
    print("解析到事件數量：", len(events))

    for idx, e in enumerate(events, start=1):
        print(f"◆ Event #{idx}：", e)

        # 3. 只處理文字訊息
        if e.get("type") == "message" and e["message"].get("type") == "text":
            text = e["message"]["text"]

            # 4. 關鍵字檢測
            resp = check_keywords(text)

            if resp:
                # 5. 直接用 reply_message 回覆（群組也適用）
                reply_token = e.get("replyToken")
                print("→ 嘗試回覆：", resp)
                try:
                    with ApiClient(configuration) as client:
                        MessagingApi(client).reply_message_with_http_info(
                            ReplyMessageRequest(
                                reply_token=reply_token,
                                messages=[TextMessage(text=resp)]
                            )
                        )
                    print("✅ 回覆成功")
                except Exception as ex:
                    print("❌ 回覆失敗：", ex)

    return "OK"

if __name__ == "__main__":
    print("📢 幹古精靈 啟動! (port 5000)，debug=True")
    app.run(host="0.0.0.0", port=5000, debug=True)