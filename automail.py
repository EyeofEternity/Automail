#!/usr/bin/python
import smtplib
import sys
from pathlib import Path
import time
import csv
from csv import reader
import mimetypes
import email
import email.mime.application
import os
import subprocess
import optparse
from optparse import OptionParser
import glob
from email.mime import multipart
from email.mime import text
from os import path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import getpass

parser = OptionParser()

parser.add_option("-e", "--ecol", type="string", help="define the column nummber for email", action="store", dest="ecol")
parser.add_option("-a", "--attach", type="string", help="attach a file or list of files to mail", action="append", dest="attach")
parser.add_option("-c", "--acol", type="string", help="attach file written in a given column", action="append", dest="acol")
parser.add_option("-m", "--content", type="string", help="the file containing the email content. Default is nothing.", action="store", default="", dest="content")
parser.add_option("-n", "--content-col", type="string", help="define column contaning the message file name", action="store", dest="ccol")
parser.add_option("-s", "--subject", type="string", help="define the subject of email. Put it in quotes. Default is nothing.", default="", action="store", dest="subject")
parser.add_option("-t", "--subject-col", type="string", help="define column containing subject", action="store", dest="scol")
parser.add_option("-d", "--delimiter", type="string", help="sets the delimiter. Default is ,", default=",", action="store", dest="delim")
parser.add_option("-f", "--file", type="string", help="define the file to take input", action="store", dest="file")
parser.add_option("-p", "--pick", type="string", help="This is used to define what word should be used to call details from file. Default is arg. In content, arg[1] refers to value of cell corresponding to column 1 and respective row.", default="arg", action="store", dest="pick")
parser.add_option("-i", "--host", type="string", help="used to set the smtp host. Default is smtp.googlemail.com", default="smtp.googlemail.com", action="store", dest="host")
parser.add_option("-j", "--port", type="string", help="sets the port of smtp host. Default is 465.", default="465", action="store", dest="port")
parser.add_option("--no-ssl", type="string", help="restricts the use of ssl. For non ssl smtp hosts", action="store", dest="nossl")

(options, args) = parser.parse_args()

if not options.file:
    print("No file defined")
    sys.exit(0)    

if not options.ecol:
    print("Column for receivers not defined")
    sys.exit(0)

if not options.content:
    if not options.ccol:
        print("No message file defined.")
        print("Sending email with default content")
        print("Program will wait for 30 seconds. Close it for stopping the process.")
        time.sleep(30)

if options.content:
    con = options.content
    if options.ccol:
        print("You cannot use both content and content-col options.")
        sys.exit(0)

if options.subject:
    subject = options.subject
    if options.scol:
        print("You cannot use both subject and subject-col options.")
        sys.exit(0)

emid = input("Email-Id: ")
password = getpass.getpass()

options.ecol = int(options.ecol)
options.port = int(options.port)
pick = options.pick
delim = options.delim
attachment = []
attachment = options.attach

ifile = open(options.file, 'rU')
reader = csv.reader(ifile, delimiter=delim)
a = []
rownum = int(0)

try:
    server_ssl = smtplib.SMTP_SSL(options.host, (options.port))
    if options.nossl:
        server_ssl = smtplib.SMTP(options.host, (options.port))
    server_ssl.ehlo()
    server_ssl.login(emid, password)

    for (row) in reader:
        a = (row)
        msg = email.mime.multipart.MIMEMultipart()
        if options.scol:
            options.scol = int(options.scol)
            subject = a[(options.scol)]
        msg['Subject'] = subject
        msg['From'] = emid
        msg['To'] = a[(options.ecol)]

        if options.ccol:
            options.ccol = int(options.ccol)
            con = open(a[(options.ccol)], 'r')
            message = con.read()
            con.close()
        if options.content:
            con = open(options.content, 'r')
            message = con.read()
            con.close()
        i = int(0)
        while i < len(a):
            message = message.replace(pick + '[' + str(i) + ']', a[i])
            i+=1

        body = email.mime.text.MIMEText(message)
        msg.attach(body)

        if options.acol:
            acola = []
            acolas = [len(acola)]
            acola = options.acol
            i = int(0)
            while i < len(acola):
                acolas[i] = (a[int(acola[i])])
                i+=1
            if options.attach:
                attachment = acolas + attachment
            else:
                attachment = acolas
        i = int(0)
        if options.acol or options.attach:
            while i < len(attachment):
                if attachment[i] != '':
                    filename=attachment[i]
                    fp=open(filename, 'rb')
                    ext=Path(filename).suffix
                    ext = ext[1:]
                    att = email.mime.application.MIMEApplication(fp.read(),_subtype=ext)
                    fp.close()
                    att.add_header('Content-Disposition','attachment',filename=filename)
                    msg.attach(att)
                i+=1
        try:
            server_ssl.sendmail(emid,[a[(options.ecol)]], msg.as_string())
            rownum+=1
            print("Completed " + str(rownum) + " emails.")
        except:
            try:
                server_ssl.sendmail(emid,[a[(options.ecol)]], msg.as_string())
                rownum+=1
                print("Completed " + str(rownum) + " emails.")
            except:
                with open('fail.txt', 'a') as fail:
                    fail.write(a[(options.ecol)] + '\n')
    server_ssl.quit()
except:
    print("Login failed.")