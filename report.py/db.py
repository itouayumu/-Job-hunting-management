import os
from colorama import Cursor
import psycopg2



def get_connection():
    url = os.environ['DATABASE_URL']
    connection = psycopg2.connect(url)
    return connection

def add_students(name,mail,digest,course,salt):
   try:
    connection = get_connection()
    cursor = connection.cursor()

    # SQLの実行
    sql = "INSERT INTO jobreport_students1(name, mail, pass,course,salt,status,delflag) VALUES(%s, %s, %s,%s,%s,%s,%s)"
    cursor.execute(sql,(name,mail,digest,course,salt,True,True))
    count = cursor.rowcount # 更新件数を取得
    connection.commit()
   except:
    count=0
   finally: # 成功しようが、失敗しようが、close する。
    cursor.close()
    connection.close()

   return count

def salt(mail):
    connection = get_connection()
    cursor = connection.cursor()

    sql1 = "SELECT salt FROM jobreport_students1 WHERE mail = %s"
    cursor.execute(sql1, (mail,))
    rows1 = cursor.fetchone()    
    cursor.close()
    connection.close()
    return rows1

def login(mail,saltpw):

    sql = "SELECT * FROM jobreport_students1 WHERE mail = %s and pass = %s"
    
    try :
        connection = get_connection()
        cursor = connection.cursor()
        
        cursor.execute(sql, (mail,saltpw,))
    #   # タプル形式で１行取出し
        user = cursor.fetchone()


    except psycopg2.DatabaseError :
        flg = False

    finally :
        cursor.close()
        connection.close()

    return user
def mail(mail):
    sql = "SELECT * FROM jobreport_students1 WHERE mail = %s"
    flg = False
    try :
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(sql, (mail,))
        user = cursor.fetchone()
        if user != None:
            flg = True

    except psycopg2.DatabaseError :
        flg = False

    finally :
        cursor.close()
        connection.close()

    return flg

def change_pw(mail,pw,salt):
   try:
    result=False
    connection = get_connection()
    cursor = connection.cursor()

    sql = " UPDATE  jobreport_students1 SET pass = %s, salt=%s WHERE mail = %s"
    cursor.execute(sql,(pw,salt,mail))
    count = cursor.rowcount 
    connection.commit()
    if count==1:
        result=True
   except:
    result=False
   finally: 
    cursor.close()
    connection.close()

   return result

def post_report(name,f_name,region,address,category,test_day,result,studentname):
    print(test_day)
    
    # try:
    connection = get_connection()
    cursor = connection.cursor()

     # SQLの実行
    sql = "INSERT INTO job_report(student_name, fail_pass, campany_name,region,address,category,test_day,result,status,delflag) VALUES(%s, %s, %s,%s,%s,%s,%s,%s,%s,%s)"
    cursor.execute(sql,(studentname,f_name,name,region,address,category,test_day.strftime('%Y-%m-%d'),result,False,True))
    count = cursor.rowcount # 更新件数を取得
    connection.commit()
    # except:
        #  count=0
    # finally: # 成功しようが、失敗しようが、close する。
    cursor.close()
    connection.close()

    return count

def passcount(result):
    
#    try:
    
    connection = get_connection()
    cursor = connection.cursor()

    # SQLの実行
    sql = 'SELECT * FROM job_report where result=%s and status=True and delflag=True'
    cursor.execute(sql,(result,))
    count = cursor.rowcount # 更新件数を取得
    
#    except:
#     count=0
#    finally: # 成功しようが、失敗しようが、close する。
    cursor.close()
    connection.close()

    return count

def count():
   try:
    connection = get_connection()
    cursor = connection.cursor()

    # SQLの実行
    sql = 'SELECT * FROM job_report status=True and delflag=True'
    cursor.execute(sql)
    count = cursor.rowcount # 更新件数を取得
    
   except:
    count=0
   finally: # 成功しようが、失敗しようが、close する。
    cursor.close()
    connection.close()

   return count

def my_report(name):
     sql = "SELECT * FROM job_report WHERE student_name=%s "
    
     try :
            connection = get_connection()
            cursor = connection.cursor()
            
            cursor.execute(sql, (name,))
        #   # タプル形式で１行取出し
            user = cursor.fetchall()


     except psycopg2.DatabaseError :
            flg = False

     finally :
            cursor.close()
            connection.close()

     return user
        
        
def post_jobinf(name,f_name,region,address,category):

    
    # try:
    connection = get_connection()
    cursor = connection.cursor()

     # SQLの実行
    sql = "INSERT INTO job_info( fail_pass, campany_name,region,address,category,status,delflag) VALUES(%s, %s, %s,%s,%s,%s,%s)"
    cursor.execute(sql,(f_name,name,region,address,category,True,True))
    count = cursor.rowcount # 更新件数を取得
    connection.commit()
    # except:
        #  count=0
    # finally: # 成功しようが、失敗しようが、close する。
    cursor.close()
    connection.close()

    return count

def failcheck(failname):
    connection = get_connection()
    cursor = connection.cursor()
    sql = "select status from job_report where fail_pass=%s"
    cursor.execute(sql,(failname))
    status = cursor.fetchone()
    # except:
        #  count=0
    # finally: # 成功しようが、失敗しようが、close する。
    cursor.close()
    connection.close()

    return status