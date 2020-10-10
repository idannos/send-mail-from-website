import socket
import select
import smtplib
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
        return temp[1]
    elif temp[0] == "POST":
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
        print "probably not valid email address or not blocked email"


open_client_sockets = []
server_socket = socket.socket()
server_socket.bind(('0.0.0.0', 80))
server_socket.listen(100)


email = ""  # email to send from
password = ''  # password to the email above
reciever_mail = ""
subject = ''
content = ""
email_const_from_client = "arnav123"
while True:
    rlist, wlist, xlist = select.select(open_client_sockets+[server_socket], open_client_sockets, [])
    for current_socket in rlist:
        if current_socket is server_socket:
            (new_socket1, address1) = server_socket.accept()
            open_client_sockets.append(new_socket1)

        else:
            data = current_socket.recv(4096)
            if data != "":
                print "here"
                original_data = data
                if valid_http(data): 
                    data = focus(data)
                    if data == "/":
                        f = open("webs.html", "r")
                        txt = f.read()
                        current_socket.send(txt)
                        f.close()
                    if data == "/favicon.ico":
                        try:
                            with open("favicon.png", "rb") as image_file:
                                a=image_file.read()
                                current_socket.send(a)
                                image_file.close()
                        except:
                            print "no favicon image in this server"
                    else:
                        data = clean(data)
                        print data
                        if email_const_from_client in data:  # the user wnts to send an email
                            data = data.split(email_const_from_client)  # [0] is mail. [1] is content
                            subject = data[0]
                            content = data[1]  # password for the code segment
                            reciever_mail = data[2]
                            print subject
                            print content
                            print reciever_mail

                            send_email(content, email, password, reciever_mail, subject)

            open_client_sockets.remove(current_socket)
            current_socket.close()
