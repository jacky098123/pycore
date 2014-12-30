#coding=utf-8
import email.Header
import email.MIMEBase
import email.MIMEMultipart
import email.MIMEText
import smtplib
import pdb
import socket
import string
import time

'''
https://docs.python.org/release/2.6.6/library/smtplib.html#smtplib.SMTP.sendmail
msg = ("From: %s\r\nTo: %s\r\n\r\n"
       % (fromaddr, ", ".join(toaddrs)))
smtp.sendmail(from, to,msg)
'''

FROM_USER   = 'kuxun_mail@163.com'
FROM_PASSWD = '1234569'

def send_mail(to_user, subject, content, subtype='', attachfile=''):
    smtp=smtplib.SMTP() 
#    smtp.set_debuglevel(1)
    socket.setdefaulttimeout(60)

    # message header
    msg         = email.Message.Message()
    msg['From'] = FROM_USER
    msg['To']   = to_user
    msg['date'] = time.ctime()
    msg['subject'] = email.Header.Header(subject,'utf8')

    # message body
    if subtype:
        body=email.MIMEText.MIMEText(content, _subtype=subtype, _charset='utf8')
    else:
        body=email.MIMEText.MIMEText(content, _charset='utf8')

    if attachfile != "" :
        attach = email.MIMEMultipart.MIMEMultipart()
        attach.attach(body)

        contype = 'application/octet-stream'
        maintype, subtype = contype.split('/', 1)
        filedata=open(attachfile,'rb')
        file_msg = email.MIMEBase.MIMEBase(maintype, subtype)
        file_msg.set_payload(filedata.read( ))
        filedata.close()
        email.Encoders.encode_base64(file_msg)
        file_msg.add_header('Content-Disposition', 'attachment', filename=attachfile[attachfile.rfind('/')+1:] )
        attach.attach(file_msg)

    smtp.connect('smtp.163.com') 
    smtp.login(FROM_USER, FROM_PASSWD) 
    
    if attachfile:
        smtp.sendmail(FROM_USER, to_user , msg.as_string()[:-1] + attach.as_string()) 
    else:
        smtp.sendmail(FROM_USER, to_user , msg.as_string()[:-1] + body.as_string()) 
    smtp.quit()

if __name__ == '__main__':
    send_mail('77543001@qq.com', 'test title, 163.py', 'test content', attachfile='mail.163.py')
