
import datetime
from email.mime.text import MIMEText
import hashlib
import os
from flask import Flask
import psycopg2
from werkzeug.utils import secure_filename

import random
import string
from MySQLdb import connect
from flask import Flask, redirect, render_template, request, session, url_for 
from datetime import date, timedelta 
import db,string,random
import send_mail


import hashlib
app = Flask(__name__)


# セッション用設定
app.secret_key = ''.join(random.choices(string.ascii_letters, k=256))
app.permanent_session_lifetime = timedelta(minutes=3000) 

def get_connection():
    url = os.environ['DATABASE_URL']
    connection = psycopg2.connect(url)
    return connection
  
@app.route('/')
def index():
    msg=request.args.get('msg')
    error=request.args.get('error')
    if msg == None and error == None:
      return render_template('index.html')
    else:
      return render_template('index.html',msg=msg,error=error)

  
@app.route('/top')
def top():
  session.permanent = True
  
  if 'id' in session:
    sql = "SELECT * FROM job_report where delflag=True and status=True ORDER BY random() LIMIT 5"
  
    
    # try :
    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute(sql)
    rows = cursor.fetchall()


    # except psycopg2.DatabaseError :
    #     flg = False

    # finally :
    cursor.close()
    connection.close()
    print(rows)
    result='合格'
    count_p=db.passcount(result)
    print(count_p)
    count=db.count()
    print(count)

    
    sql2 = "SELECT * FROM job_info where delflag=True and status=True ORDER BY random() LIMIT 5"

    
    # try :
    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute(sql2)
    rows2 = cursor.fetchall()


    # except psycopg2.DatabaseError :
    #     flg = False

    # finally :
    cursor.close()
    connection.close()
    
    # return render_template('top.html',reports_list=reports_list)
    return render_template('top.html',reports_list=rows,jobinf_list=rows2,p_result=count_p,count=count)
  else:
    return redirect (url_for('index'))

@app.route("/login", methods = ["POST","GET"])
def login():
  mail = request.form.get("id") 
  pw = request.form.get("pass")
  if not mail and not pw:
    error ='エラーが発生しました。入力しなおしてください'
    return render_template("index.html",error=error) 
  if mail == "admin@admin":
    return render_template('adominlogin.html')
  b_pw =bytes(pw,"utf-8")
  row1=db.salt(mail)
  if not row1:
    error ='エラーが発生しました。入力しなおしてください'
    return render_template("index.html",error=error,mail=mail) 
  b_salt =bytes(row1[0],"utf-8")
  saltpw = hashlib.pbkdf2_hmac("sha256", b_pw, b_salt, 1000).hex()
  row2=db.login(mail,saltpw)
  if not row2 :
    error ='エラーが発生しました。入力しなおしてください'
    return render_template("index.html",error=error,mail=mail) 
  elif row2[6]==False:
      return render_template("index.html",error=error,mail=mail)    
  else:
    session.permanent = True  
    session["id"] = row2[0]
    session["name"] = row2[1]
    session["mail"] = row2[2]
    session["course"] = row2[4]
    print(session["id"])
    return redirect(url_for('top'))

@app.route("/logout", methods=["GET"])
def logout():
  session.pop('id',None)
  session.clear()
  return redirect("/")
 
@app.route("/newacount")
def newacount():
    return render_template("newacount.html")



@app.route("/adomionresult",methods = ["POST"])
def adomionresult():
    a_id = request.form.get("id") 
    a_pass = request.form.get("pass")
    if a_id=='a' and a_pass == 'a':
        return render_template("atop.html")
    else:
        return render_template("adominlogin.html")
 

    
@app.route("/addacount",methods = ["POST"])
def addacount():
  name=request.form.get("name") 
  mail=request.form.get("mail") 
  pw=request.form.get("pw") 
  charset = string.ascii_letters + string.digits
  salt = ''.join(random.choices(charset, k=30))
  b_pw =bytes(pw,"utf-8")
  b_salt =bytes(salt,"utf-8")
  digest = hashlib.pbkdf2_hmac("sha256", b_pw, b_salt, 1000).hex()
  course=request.form.get("course") 
  count=db.add_students(name,mail,digest,course,salt)
  if count==1:
    msg="登録が完了しました"
    return redirect(url_for('index', msg=msg))
  else:
    error="登録失敗しました。入力しなおしてください"
    return render_template("newacount.html",error=error,name=name,mail=mail,course=course)

@app.route("/changepw")
def changepw():
  return render_template("changepw.html")


  
@app.route("/sendmail",methods = ["POST"])
def sendmail():
  mail=request.form.get("mail") 
  print(mail)
  result=db.mail(mail=mail)
  if result:
    session["mail"]=mail
    send_mail.send_mail(mail)
    return redirect(url_for('index'))
  else:
    error="1"
    return render_template("/changepw.html",error=error)

@app.route('/change')
def change():  
  return render_template('changepw_result.html')
    
    
@app.route('/changepass_result',methods = ["POST"])
def changepass_result():  
  # 以下三行フォームから値受け取り
  mail=session["mail"]
  pw=request.form.get("pass") 
  pw_check=request.form.get("pass_check")
  # 確認用と比較 
  if pw != pw_check:
    return redirect(url_for('change'))
  # ハッシュ化etc...
  b_pw =bytes(pw,"utf-8")
  charset = string.ascii_letters + string.digits
  salt = ''.join(random.choices(charset, k=30))
  b_salt =bytes(salt,"utf-8")
  digest = hashlib.pbkdf2_hmac("sha256", b_pw, b_salt, 1000).hex()
  # ここでdb.pyに値渡す
  result=db.change_pw(mail,digest,salt)
  # 成功かどうかの判断
  if result:
    suc="1"
    return redirect(url_for('index',suc=suc))
  else:
    error="1"
    return redirect(url_for('change',error=error))    

@app.route('/send_report')
def send_report():  
    session.permanent = True
  
    if 'id' in session:
      return render_template('send_report.html')
    else:
      return redirect (url_for('index'))
  
  
@app.route('/post_report',methods = ["POST"])
def post_report(): 
      if 'file' not in request.files:
        return redirect(url_for('send_report'))
      UPLOAD_FOLDER = 'C:/Users/itou/Desktop/python/python_flask_web_final_exercise_2023-itouayumu/report.py/static/pdf'
      file = request.files['file']
      charset = string.ascii_letters + string.digits
      ran = ''.join(random.choices(charset, k=5))
      f_name = secure_filename(file.filename)
      up_fail=ran+f_name
      name=request.form.get("name")
      region=request.form.get("region")
      address=request.form.get("address")
      category=request.form.get("category")
      test_day=request.form.get("test_day")
      t_day = datetime.datetime.strptime(test_day, '%Y-%m-%d')
      date_type= date(t_day.year, t_day.month, t_day.day)
      print(date_type)
      result=request.form.get("result")
      student_name=session['name']
      post_result=db.post_report(name,up_fail,region,address,category,date_type,result,student_name)
      if post_result==1:
        file.save(os.path.join(UPLOAD_FOLDER , up_fail))
        return redirect(url_for('top'))
      else:
        return render_template('send_report.html')
      
@app.route('/report_list')
def report_list():
  session.permanent = True
  
  if 'id' in session :
    sql = "SELECT * FROM job_report where delflag=True and status=True "

    
    # try :
    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute(sql)
    rows = cursor.fetchall()


    # except psycopg2.DatabaseError :
    #     flg = False

    # finally :
    cursor.close()
    connection.close()
    print(rows)
    return render_template('report_list.html',reports_list=rows)
  
@app.route('/search_report',methods = ["POST"])
def search_report():

  session.permanent = True
  name=request.form.get("name")
  session["search"]=name
  result1='%'+name+'%'
  region=request.form.get("region")
  session["region"]=region
  result2='%'+region+'%'
  category=request.form.get("category")
  session["category"]=category
  result3='%'+category+'%'
  if 'id' in session:
    sql = "SELECT * FROM job_report where campany_name LIKE %s and region LIKE %s and category LIKE %s "

    
    # try :
    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute(sql,(result1,result2,result3))
    rows = cursor.fetchall()


    # except psycopg2.DatabaseError :
    #     flg = False

    # finally :
    cursor.close()
    connection.close()
    print(rows)
    return render_template('report_list.html',reports_list=rows,name=session["search"],region=session["region"],category=session["category"])
  else:
    return render_template('index.html')
  
@app.route('/jobinf_list')
def jobinf_list():
  session.permanent = True
  
  if 'id' in session or "admin" in session:
    sql = "SELECT * FROM job_info where delflag=True and status=True "

    
    # try :
    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute(sql)
    rows = cursor.fetchall()


    # except psycopg2.DatabaseError :
    #     flg = False

    # finally :
    cursor.close()
    connection.close()
    print(rows)
    return render_template('job_inflist.html',reports_list=rows)
  
@app.route('/search_jobinf',methods = ["POST"])
def search_jobinf():

  session.permanent = True
  name=request.form.get("name")
  session["search2"]=name
  result1='%'+name+'%'
  region=request.form.get("region")
  session["region2"]=region
  result2='%'+region+'%'
  category=request.form.get("category")
  session["category2"]=category
  result3='%'+category+'%'
  if 'id' in session:
    sql = "SELECT * FROM job_info where campany_name LIKE %s and region LIKE %s and category LIKE %s "

    
    # try :
    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute(sql,(result1,result2,result3))
    rows = cursor.fetchall()

    print(session["search2"])
    # except psycopg2.DatabaseError :
    #     flg = False

    # finally :
    cursor.close()
    connection.close()
    print(rows)
    return render_template('job_inflist.html',reports_list=rows,name=session["search2"],region=session["region2"],category=session["category2"])
  else:
    return render_template('index.html')
  
@app.route('/back_search_report')
def back_search_report():
  session.permanent = True
  if 'id' in session:
    if "search" in session:
      result1='%'+session["search"]+'%'
      result2='%'+session["region"]+'%'
      result3='%'+session["category"]+'%'
      sql = "SELECT * FROM job_report where campany_name LIKE %s and region LIKE %s and category LIKE %s "

      
      # try :
      connection = get_connection()
      cursor = connection.cursor()
      
      cursor.execute(sql,(result1,result2,result3))
      rows = cursor.fetchall()


      # except psycopg2.DatabaseError :
      #     flg = False

      # finally :
      cursor.close()
      connection.close()
      print(rows)
      return render_template('report_list.html',reports_list=rows,name=session["search"],region=session["region"],category=session["category"])
    else:
      sql = "SELECT * FROM job_report where delflag=True and status=True "

    
    # try :
    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute(sql)
    rows = cursor.fetchall()


    # except psycopg2.DatabaseError :
    #     flg = False

    # finally :
    cursor.close()
    connection.close()
    print(rows)
    return render_template('report_list.html',reports_list=rows)
  else:
    return render_template('index.html')
  
@app.route('/back_search_jobinf_list')
def back_search_jobinf_list():
  session.permanent = True
  if 'id' in session:
    if "search2" in session:
      result1='%'+session["search2"]+'%'
      result2='%'+session["region2"]+'%'
      result3='%'+session["category2"]+'%'
      sql = "SELECT * FROM job_info where  delflag=True and status=False and campany_name LIKE %s and region LIKE %s and category LIKE %s "

      
      # try :
      connection = get_connection()
      cursor = connection.cursor()
      
      cursor.execute(sql,(result1,result2,result3))
      rows = cursor.fetchall()


      # except psycopg2.DatabaseError :
      #     flg = False

      # finally :
      cursor.close()
      connection.close()
      print(rows)
      return render_template('job_inflist.html',reports_list=rows,name=session["search2"],region=session["region2"],category=session["category2"])
    else:
      sql = "SELECT * FROM job_info where delflag=True and status=True "

    
    # try :
    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute(sql)
    rows = cursor.fetchall()


    # except psycopg2.DatabaseError :
    #     flg = False

    # finally :
    cursor.close()
    connection.close()
    print(rows)
    return render_template('job_inflist.html',reports_list=rows)
  else:
    return render_template('index.html')
  
@app.route('/detail')
def detail():
    contents = request.args.get('f_name')
    connection = get_connection()
    cursor = connection.cursor()
    sql = "select status from job_report where fail_pass= %s"
    cursor.execute(sql,(contents,))
    status = cursor.fetchall()
    cursor.close()
    connection.close()
    print(status)
    if status[0] !="f":
      fail='pdf/'+contents

      return render_template('detail_report.html',fail=fail)
    else:
      error="1"
      return render_template('detail_report.html',error=error)
  
@app.route('/jobinf')
def jobinf():
    contents = request.args.get('f_name', '')
    fail='pdf/'+contents
    return render_template('jobinf.html',fail=fail,name=session["name"])
    
@app.route('/mydetail')
def mydetail():
    contents = request.args.get('f_name', '')
    fail='pdf/'+contents
    return render_template('mydetail_report.html',fail=fail,name=session["name"])
  
@app.route('/topdetail')
def topdetail():
    contents = request.args.get('f_name', '')
    fail='pdf/'+contents
    return render_template('topdetail_report.html',fail=fail,name=session["name"])
  
@app.route('/mypage')
def mypage():
  session.permanent = True
  if 'id' in session:
    report=db.my_report(session["name"])

    return render_template('mypage.html',my_reports_list=report,name=session["name"],mail=session["mail"],course=session["course"])
  else:
    return redirect (url_for('index'))
  
  
# ---------ここまで利用者-------------
# ---------ここから管理者-------------

@app.route('/atop')
def atop():  
  if "admin" in session:
    return render_template('atop.html')
  else:
    return render_template("index.html")



@app.route('/a_login',methods = ["POST"])
def a_login():
    a_id=request.form.get("id")
    a_pass=request.form.get("pw")
    if a_id=="10025511" and a_pass=="gn545323":
      session["admin"]=True
      return render_template('atop.html')
    else:
      return render_template('adominlogin.html',mail=a_id)
    
@app.route('/post_jobinf',methods = ["POST"])
def post_jobinf(): 
    
      if 'file' not in request.files:
        return redirect(url_for('send_report'))
      UPLOAD_FOLDER = 'C:/Users/itou/Desktop/python/python_flask_web_final_exercise_2023-itouayumu/report.py/static/pdf'
      file = request.files['file']
      charset = string.ascii_letters + string.digits
      ran = ''.join(random.choices(charset, k=5))
      f_name = secure_filename(file.filename)
      up_fail=ran+f_name
      name=request.form.get("name")
      region=request.form.get("region")
      address=request.form.get("address")
      category=request.form.get("category")

      post_result=db.post_jobinf(name,up_fail,region,address,category)
      if post_result==1:
        file.save(os.path.join(UPLOAD_FOLDER , up_fail))
        return redirect(url_for('a_top'))
      else:
        return render_template('send_report.html')
      
@app.route('/allupdate')
def allupdate():  
  if "admin" in session:
    return render_template('allupdate.html')
  else:
    return redirect (url_for('index'))
  
@app.route('/send_jobinf')
def send_jobinf():  
  if "admin" in session:
    return render_template('send_jobinf.html')
  else:
    return redirect (url_for('index'))
  
@app.route('/all_regist')
def all_regist():  
  if "admin" in session:
     connection = get_connection()
     cursor = connection.cursor()

     sql = "UPDATE job_report SET status=True WHERE status=False"
     cursor.execute(sql)
     count = cursor.rowcount 
     connection.commit()

     cursor.close()
     connection.close()

     return render_template('atop.html')
  else:
    return redirect (url_for('index'))
  
@app.route('/tentative')
def tentative():
  session.permanent = True
  
  if  "admin" in session:
    sql = "SELECT * FROM job_report where delflag=True and status=False "

    
    # try :
    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute(sql)
    rows = cursor.fetchall()


    # except psycopg2.DatabaseError :
    #     flg = False

    # finally :
    cursor.close()
    connection.close()
    print(rows)
    return render_template('tentative.html',reports_list=rows)
  else:
    return render_template('adominlogin.html')

@app.route('/search_t_report',methods = ["POST"])
def search_t_report():

  session.permanent = True
  name=request.form.get("name")
  session["searcha"]=name
  result1='%'+name+'%'
  region=request.form.get("region")
  session["regiona"]=region
  result2='%'+region+'%'
  category=request.form.get("category")
  session["categorya"]=category
  result3='%'+category+'%'
  if 'id' in session:
    sql = "SELECT * FROM job_report where delflag=True and status=False campany_name LIKE %s and region LIKE %s and category LIKE %s "

    
    # try :
    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute(sql,(result1,result2,result3))
    rows = cursor.fetchall()


    # except psycopg2.DatabaseError :
    #     flg = False

    # finally :
    cursor.close()
    connection.close()
    print(rows)
    return render_template('report_list.html',reports_list=rows,name=session["searcha"],region=session["regiona"],category=session["categorya"])
  else:
    return render_template('index.html')
  
@app.route('/t_detail')
def t_detail():
    contents = request.args.get('f_name')
    connection = get_connection()
    cursor = connection.cursor()
    sql = "select status from job_report where fail_pass= %s"
    cursor.execute(sql,(contents,))
    status = cursor.fetchall()
    cursor.close()
    connection.close()
    print(status)

    fail='pdf/'+contents
    return render_template('t_detail_report.html',fail=fail)

  
  
@app.route('/back_tentative')
def back_tentative():
  session.permanent = True
  if 'admin' in session:
    if "searcha" in session:
      result1='%'+session["searcha"]+'%'
      result2='%'+session["regiona"]+'%'
      result3='%'+session["categorya"]+'%'
      sql = "SELECT * FROM job_report where  delflag=True and status=False and campany_name LIKE %s and region LIKE %s and category LIKE %s "

      
      # try :
      connection = get_connection()
      cursor = connection.cursor()
      
      cursor.execute(sql,(result1,result2,result3,))
      rows = cursor.fetchall()


      # except psycopg2.DatabaseError :
      #     flg = False

      # finally :
      cursor.close()
      connection.close()
      print(rows)
      return render_template('tentative.html',reports_list=rows,name=session["searcha"],region=session["regiona"],category=session["categorya"])
    else:
      sql = "SELECT * FROM job_report where delflag=True and status=False "

    
    # try :
    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute(sql)
    rows = cursor.fetchall()


    # except psycopg2.DatabaseError :
    #     flg = False

    # finally :
    cursor.close()
    connection.close()
    print(rows)
    return render_template('tentative.html',reports_list=rows)
  else:
    return render_template('adominlogin.html')
  
@app.route('/search_t',methods = ["POST"])
def search_t():

  session.permanent = True
  name=request.form.get("name")
  session["searcha"]=name
  result1='%'+name+'%'
  region=request.form.get("region")
  session["regiona"]=region
  result2='%'+region+'%'
  category=request.form.get("category")
  session["categorya"]=category
  result3='%'+category+'%'
  if 'admin' in session:
    sql = "SELECT * FROM job_report where delflag=True and status=False and campany_name LIKE %s and region LIKE %s and category LIKE %s "

    
    # try :
    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute(sql,(result1,result2,result3))
    rows = cursor.fetchall()

    print(session["searcha"])
    # except psycopg2.DatabaseError :
    #     flg = False

    # finally :
    cursor.close()
    connection.close()
    print(rows)
    return render_template('tentative.html',reports_list=rows,name=session["searcha"],region=session["regiona"],category=session["categorya"])
  else:
    return render_template('adominlogin.html')
  
if __name__=="__main__":
    app.run(debug=True) #webサーバーを起動
    