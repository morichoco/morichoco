import os
from time import time
from flask import Flask, request, abort
import openai

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage
)

main = Flask(__name__)

# OpenAI APIキー
#openai.api_key = "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"
openai.api_key = "myAPI"

# LINEチャンネルアクセストークン
#LINE_CHANNEL_ACCESS_TOKEN = "ZJdyFcNiO+8dIBzAe+xP9QnaJFKmsv66XDEStB8PjacvhBVcEfwmYFHERQz3++zJbtmFmkV1NdKolkTtyw1QdIJJtKNAY8FEm8bPvNagje6+lqDk02RA5vZS4UuQ1RA8d8V1zY6bl0an4KhYSHzTDAdB04t89/1O/w1cDnyilFU="
LINE_CHANNEL_ACCESS_TOKEN = "lineChannel"

# LINEチャンネルシークレット
#LINE_CHANNEL_SECRET ='3df9df4ea226c2f147a38efe66b34c0f'
LINE_CHANNEL_SECRET ='lineSecret'

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@main.route("/")
def test():
    return "OK"

@main.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]

    # リクエストを取得
    body = request.get_data(as_text=True)
    main.logger.info("Request body: " + body)

    # 署名を検証
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"

users={}
# ユーザーごとの会話履歴を保存する辞書
conversations = {}

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    #ユーザーid情報
    userId=event.source.user_id
    # ユーザーごとの会話履歴を初期化
    if userId not in conversations:
        conversations[userId] = []

    #時間計測機能
    if event.message.text=="計測開始":
        answer="計測を開始しました。"

        if not userId in users:
            users[userId]={}
            users[userId]["total"]=0

        users[userId]["start"]=time()

    elif event.message.text=="計測終了":
        end=time()
        difference=int(end-users[userId]["start"])
        users[userId]["total"]+=difference
        #経過時間
        hour=difference//3600
        minute=(difference%3600)//60
        second=difference%60
        #合計時間
        sum_hour=users[userId]["total"]//3600
        sum_minute=(users[userId]["total"]%3600)//60
        sum_second=users[userId]["total"]%60
        answer=f"経過時間は{hour}時間{minute}分{second}秒です。合計時間は{sum_hour}時間{sum_minute}分{sum_second}秒です。"
        
    #会話機能
    else:
        # ユーザーの入力を保存
        conversations[userId].mainend(event.message.text)

        response =generate_response(conversations[userId])

        answer=response

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=answer)
    )

def generate_response(conversation):

    response=openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                #ふるまい方
                #{"role": "system", "content": "アシスタントは、「AI太郎」という男性のチャットボットです。\
                # 指示は以下の通りです：\
                # - 答えには、必ず「そうですねぇ～」と言ってから、回答します。\
                # - 答えに迷った場合は「さっぱりわかりませんねぇ～」言ってください。さらに「違うかもしれませんけどぉ～」と言って答えてください。"},
                {"role": "user", "content": conv} for conv in conversation
            ]
    )
    
    # 生成された応答を返す
    return response['choices'][0]['message']['content'].strip()

if __name__ == "__main__":
    main.run(debug=True)
