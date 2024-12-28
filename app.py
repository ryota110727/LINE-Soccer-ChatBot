from flask import Flask
from flask import request
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (MessageEvent, TextMessage, TextSendMessage,TemplateSendMessage,CarouselTemplate)
import boto3
from src.service.handle_message_service import *

def get_ssm_parameter(parameter_name):
    ssm = boto3.client("ssm")
    # SSM clientを作成

    # パラメータを取得
    response = ssm.get_parameters(
          Names=[parameter_name,],
          WithDecryption=True
        )

    # パラメータの値を返す
    return response['Parameters'][0]['Value']

app=Flask(__name__)
token = get_ssm_parameter("ACCESS_TOKEN")
secret = get_ssm_parameter("CHANNEL_SECRET")
line_bot_api = LineBotApi(token)
handler = WebhookHandler(secret)

@app.route("/")
def hello():
     return "hello ryota"

# endpoint from linebot
@app.route("/callback", methods=['POST'])
def callback():
        signature = request.headers['X-Line-Signature']
        body=request.get_data(as_text=True)
        app.logger.info("Request body: " + body)
        try:
            handler.handle(body,signature)
        except InvalidSignatureError:
            print("Invalid signature. Please check your channel access token/channel secret.")
            abort(400)
        return "OK"

# handle message from LINE
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
        # メッセージ生成モジュールの呼び出し
        reply = handle_message_service.generate_reply_message(event.message.text)
        if reply == "新しいニュースはありません" or reply == "返信できない形です":
              line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text = reply)
              )
        else:
               carousel_template_message = TemplateSendMessage(
                     alt_text = "最新ニュースを通知しました",
                     template = CarouselTemplate(columns = reply)
               )
               line_bot_api.reply_message(
                     event.reply_token,
                     messages = carousel_template_message
               )

if __name__=="__main__":
      app.run(host='0.0.0.0',port=3000,debug=True)
