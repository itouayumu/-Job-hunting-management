# メール用設定
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from smtplib import SMTP
import os



def send_mail(to):
    ID='changepas202306@gmail.com'
    PASS = os.environ['mail_pass']
    HOST = 'smtp.gmail.com'
    PORT = 587
    body='パスワード変更の場合は以下のリンクからお願いします<br><a href="http://127.0.0.1:5000/change">ここをクリック</a>'
    msg = MIMEMultipart()
    msg.attach(MIMEText(body,'html'))
    
    msg['Subject'] = 'PASS変更'
    msg['From'] = ID
    msg['To'] = to
    
    server = SMTP(HOST,PORT)
    server.starttls()
    
    server.login(ID,PASS)
    
    server.send_message(msg)
    
    server.quit()
    