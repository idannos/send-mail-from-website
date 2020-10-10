import socket
import select
import sys
import smtplib
import pickle
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
HTTP_FORMATS = ["GET", "POST"]


def valid_http(data):
    """
    :param data:
    :return: if the http is valid and relevant to us.
    """
    temp = data.split(" ")
    if temp[0] in HTTP_FORMATS and "HTTP/1.1" in temp[2]:
        return True
    return False


def focus(data):
    """
    :param data:
    :return: the http format
    """
    temp = data.split(" ")
    if temp[0] == "GET":
        #  print "get"
        return temp[1]
    elif temp[0] == "POST":
        #  print "post"
        data = data.split("\r\n\r\n")
        return data[1]


def clean(data):
    """
    :param data:
    :return: "cleaned" data- now python can understand the data
    """
    data = data.replace("%22", '"', 100)  # we want " instead %22
    data = data.replace("%20", ' ', 100)  # we want space instead %20
    data = data.replace("%3Cbr/%3E","\n",100)
    data = data.replace("<br/>", "\n", 100)
    return data


def send_email(message, email, password,send_to_email, subject):
    """
    :param message: the password to the code together+ link and a little description.
    :param email: a mail that I created for this project- the emails will be sent from this email always,
     so the user wont enter his email
    :param password: the password for the email
    :param send_to_email: the email address we want to send too.
    :param subject: subject of the email message
    :exit: sent or an error message- will appear in the server
    """
    try:
        msg = MIMEMultipart()
        msg['From'] = email
        msg['To'] = send_to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(message, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email, password)
        text = msg.as_string()
        server.sendmail(email, send_to_email, text)
        server.quit()
        print "sent email"
    except:
        print "probably not valid email address"

to_send = ""
open_client_sockets = []
server_socket = socket.socket()
server_socket.bind(('0.0.0.0', 80))
server_socket.listen(100)

test = ""
new_data = ""
email = ""  # email to send from
password = ''  # password to the email above
send_to_email = ""  # email to send to
# message = '123'--------------------
subject = ''  # subject to email
pass_and_codes = {}
user_name = ""  # as logged in the website
password1 = ""  # as logged in the website

while True:
    rlist, wlist, xlist = select.select(open_client_sockets+[server_socket], open_client_sockets, [])
    for current_socket in rlist:
        if current_socket is server_socket:
            (new_socket1, address1) = server_socket.accept()
            open_client_sockets.append(new_socket1)

        else:
            data = current_socket.recv(4096)
            if data != "":
                #  print "data is: " + data
                #  print "here"
                original_data = data
                if valid_http(data):
                    data = focus(data)
                    # print "focus data is: " + data
                    if data == "/":
                        f = open("webs.html", "r")
                        txt = f.read()
                        current_socket.send(txt)
                        f.close()
                    if data == "/favicon.ico" or data == "/img_avatar2.png":
                        print "data for pic is: "+data
                        try:

                            with open("icon.png", "rb") as image_file:
                                a = image_file.read()
                                current_socket.send(a)
                                image_file.close()
                        except:
                            print "no favicon image in this server"
                        """
                        if data == "/img_avatar2.png":
                        
                        if data == "/favicon.ico":
                            try:
                                with open("icon.png", "rb") as image_file:
                                    a=image_file.read()
                                    current_socket.send(a)
                                    image_file.close()
                            except:
                                print "no favicon image in this server"
                            if data == "/img_avatar2.png":
                                try:
                                    with open("icon2.png", "rb") as image_file:
                                        a = image_file.read()
                                        current_socket.send(a)
                                        image_file.close()
                                except:
                                    print "no favicon image in this server"
                                    """
                    else:
                        data = clean(data)
                        # current_socket.send("HTTP/1.1 200 Ok\r\n\r\n" + data)
                        current_socket.send("HTTP/1.1 200 Ok\r\n\r\n" + "Test")

                        print "data is: " + data



            open_client_sockets.remove(current_socket)
            current_socket.close()