import os
from flask import Flask, request, redirect, url_for, render_template, send_from_directory, flash, jsonify
from werkzeug.utils import secure_filename
import cv2
import numpy as np
import json
import requests
import tempfile, shutil, os
from PIL import Image
from io import BytesIO

from linebot.models import (
    TemplateSendMessage, AudioSendMessage,
    MessageEvent, TextMessage, TextSendMessage,
    SourceUser, PostbackEvent, StickerMessage, StickerSendMessage, 
    LocationMessage, LocationSendMessage, ImageMessage, ImageSendMessage
)
from linebot.models.template import *
from linebot import (
    LineBotApi, WebhookHandler
)

app = Flask(__name__, static_url_path="/static")

UPLOAD_FOLDER ='static/uploads/'
DOWNLOAD_FOLDER = 'static/downloads/'
ALLOWED_EXTENSIONS = {'jpg', 'png','.jpeg'}

lineaccesstoken = 'wGff8+NiX4eTzzC5gC88FFmZKsTNUDOZYd9wntQ5fKohqronZf9tU9088yYjJ69JADf2RR8At/NzeUeTUczxrbF12s0oEgzJicHEdM54x5sijac69BA2Uq/XuwWUX9SfOBPg+oFwEcY4ATBg0ofRvgdB04t89/1O/w1cDnyilFU='

line_bot_api = LineBotApi(lineaccesstoken)

# APP CONFIGURATIONS
app.config['SECRET_KEY'] = 'opencv'  
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
# limit upload size upto 6mb
app.config['MAX_CONTENT_LENGTH'] = 6 * 1024 * 1024

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file attached in request')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            process_file(os.path.join(UPLOAD_FOLDER, filename), filename)
            data={
                "processed_img":'static/downloads/'+filename,
                "uploaded_img":'static/uploads/'+filename
            }
            return render_template("index.html",data=data)  
    return render_template('index.html')


def process_file(path, filename):
    detect_object(path, filename)
    
def detect_object(path, filename):    
    CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
        "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
        "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
        "sofa", "train", "tvmonitor"]
    COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))
    prototxt="ssd/MobileNetSSD_deploy.prototxt.txt"
    model ="ssd/MobileNetSSD_deploy.caffemodel"
    net = cv2.dnn.readNetFromCaffe(prototxt, model)
    image = cv2.imread(path)
    image = cv2.resize(image,(480,360))
    (h, w) = image.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 0.007843, (300, 300), 127.5)
    net.setInput(blob)
    detections = net.forward()
    for i in range(0, detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > 0.60:
            idx = int(detections[0, 0, i, 1])
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")

            # display the prediction
            label = "{}: {:.2f}%".format(CLASSES[idx], confidence * 100)
            # print("[INFO] {}".format(label))
            cv2.rectangle(image, (startX, startY), (endX, endY),
                COLORS[idx], 2)
            y = startY - 15 if startY - 15 > 15 else startY + 15
            cv2.putText(image, label, (startX, y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)

    cv2.imwrite(f"{DOWNLOAD_FOLDER}{filename}",image)

@app.route('/callback', methods=['POST'])
def callback():
    json_line = request.get_json(force=False,cache=False)
    json_line = json.dumps(json_line)
    decoded = json.loads(json_line)
    
    # เชื่อมต่อกับ line 
    no_event = len(decoded['events'])
    for i in range(no_event):
            event = decoded['events'][i]
            event_handle(event,json_line)

    # เชื่อมต่อกับ dialogflow
    #intent = decoded["queryResult"]["intent"]["displayName"] 
    #text = decoded['originalDetectIntentRequest']['payload']['data']['message']['text'] 
    #reply_token = decoded['originalDetectIntentRequest']['payload']['data']['replyToken']
    #id = decoded['originalDetectIntentRequest']['payload']['data']['source']['userId']
    #disname = line_bot_api.get_profile(id).display_name
    #reply(intent,text,reply_token,id,disname)

    return '',200

def reply(intent,text,reply_token,id,disname):
    text_message = TextSendMessage(text="ทดสอบ")
    line_bot_api.reply_message(reply_token,text_message)

def event_handle(event,json_line):
    print(event)
    try:
        userId = event['source']['userId']
    except:
        print('error cannot get userId')
        return ''

    try:
        rtoken = event['replyToken']
    except:
        print('error cannot get rtoken')
        return ''
    try:
        msgId = event["message"]["id"]
        msgType = event["message"]["type"]
    except:
        print('error cannot get msgID, and msgType')
        sk_id = np.random.randint(1,17)
        replyObj = StickerSendMessage(package_id=str(1),sticker_id=str(sk_id))
        line_bot_api.reply_message(rtoken, replyObj)
        return ''

    if msgType == "text":
        msg = str(event["message"]["text"])
        if msg == "คณิตศาสตร์พื้นฐาน 1 ค31101 ภาคเรียนที่1":
            replyObj = TextSendMessage(text="คณิตศาสตร์พื้นฐาน 1 ค31101 ภาคเรียนที่ 1
บทที่ 1 เซต
- เซต คือลักษณะนามใช้เรียกกลุ่มสิ่งของต่างๆ สิ่งที่อยู่ในกลุ่มเรียกว่า สมาชิกของเซต เขียนเซตได้ 2 แบบ คือ แบบแจกแจงสมาชิกกับแบบบอกเงื่อนไขสมาชิก
- เซตมี 3 ชนิด คือเซตจำกัด (ระบุจำนวนสมาชิกได้), เซตอนันต์ (ไม่สามารถระบุจำนวน​สมาชิกได้)​ และเซตว่าง (ไม่มีสิ่งใดที่เป็นสมาชิกของเซต)​
- เอกภพสัมพัทธ์ คือเซตที่กำหนดขึ้นมาหนึ่งเซต ไม่กล่าวถึงสิ่งอื่นนอกจากสมาชิกที่กำหนด แทนด้วย U และแผนภาพเวนน์-ออยเลอร์ คือแผนภาพที่เขียนแสดงความสัมพันธ์ของเซตต่าง ๆ
- ยูเนียน คือเซตที่มีสมาชิกร่วมกัน ส่วนอินเตอร์เซ็กชัน คือเซตที่มีสมาชิกเหมือนกัน
- คอมพลีเมนต์ของเซต A คือเซตของทุกสมาชิกในเอกภพสัมพัทธ์ U ที่ไม่อยู่ใน A ส่วนผลต่างของเซต A และ B คือเซตของทุกสมาชิกเซต A ที่ไม่เป็นสมาชิกของเซต B
บทที่ 2 ตรรกศาสตร์ (Logic)
- ตรรกศาสตร์ หมายถึงวิชาที่ว่าด้วยการให้เหตุผล
- ประพจน์ หมายถึงข้อความที่เป็นประโยคบอกเล่าหรือปฏิเสธที่บอกได้ว่าจริงหรือเท็จ ส่วนข้อความที่ไม่เป็นประพจน์ หมายถึงข้อความที่ไม่สามารถบอกได้ว่าจริงหรือเท็จ เช่น คำถาม, คำสั่ง, ขอร้อง, อุทาน, อวยพร, มีตัวแปร, สุภาษิต เป็นต้น
- ค่าความจริงมี 2 ชนิด คือจริง (T)​ กับเท็จ (F)​
- ตัวเชื่อมของประพจน์มี 5 คำ คือและ ∧ , หรือ ∨ , ถ้า...แล้ว → , ก็ต่อเมื่อ ⇔ และไม่/ไม่ใช่ ~
- นิเสธของประพจน์ หมายถึงข้อความที่ปฏิเสธข้อความเดิม
- สัจนิรันดร์ คือรูปแบบของประพจน์ที่มีค่าความจริงเป็นจริงทุกกรณี ส่วนการขัดแย้ง คือรูปแบบของประพจน์ที่มีค่าความจริงเป็นเท็จทุกกรณี
- ประโยคเปิด คือประโยคบอกเล่าหรือปฏิเสธที่กล่าวถึงสมาชิกในเอกภพสัมพัทธ์ในรูปของตัวแปร ซึ่งประโยคเปิดไม่เป็นประพจน์ เพราะบอกไม่ได้ว่าจริงหรือเท็จ")
            line_bot_api.reply_message(rtoken, replyObj)
        elif msg == "กินข้าวไหมคะ":
            replyObj = TextSendMessage(text="กินค่ะ กำลังหิวพอดีเลย")
            line_bot_api.reply_message(rtoken, replyObj)
        elif msg == "ไปเที่ยวกันไหมคะ":
            replyObj = TextSendMessage(text="ไปแน่นอนค่ะ")
            line_bot_api.reply_message(rtoken, replyObj)
        elif msg == "covid":
            url = "https://covid19.ddc.moph.go.th/api/Cases/today-cases-all"
            response = requests.get(url)
            response = response.json()
            replyObj = TextSendMessage(text=str(response))
            line_bot_api.reply_message(rtoken, replyObj)
        else :
            headers = request.headers
            json_headers = ({k:v for k, v in headers.items()})
            json_headers.update({'Host':'bots.dialogflow.com'})
            url = "https://dialogflow.cloud.google.com/v1/integrations/line/webhook/a56aca9e-a0f2-43b6-baa1-a20e066dfb3f"
            requests.post(url,data=json_line, headers=json_headers)
    elif msgType == "image":
        try:
            message_content = line_bot_api.get_message_content(event['message']['id'])
            i = Image.open(BytesIO(message_content.content))
            filename = event['message']['id'] + '.jpg'
            i.save(UPLOAD_FOLDER + filename)
            process_file(os.path.join(UPLOAD_FOLDER, filename), filename)

            url = request.url_root + DOWNLOAD_FOLDER + filename
            
            line_bot_api.reply_message(
                rtoken, [
                    TextSendMessage(text='Object detection result:'),
                    ImageSendMessage(url,url)
                ])    
    
        except:
            message = TextSendMessage(text="เกิดข้อผิดพลาด กรุณาส่งใหม่อีกครั้ง")
            line_bot_api.reply_message(event.reply_token, message)

            return 0

    else:
        sk_id = np.random.randint(1,17)
        replyObj = StickerSendMessage(package_id=str(1),sticker_id=str(sk_id))
        line_bot_api.reply_message(rtoken, replyObj)
    return ''

if __name__ == '__main__':
    app.run()
