#!/usr/bin/env python3
"""
movies.py by Neil Grogan, 2020

A script to email you when movies of interest are on in local cinema
"""
import logging
from logging.config import fileConfig
import configparser
from pathlib import Path
from urllib import request
import smtplib
from email.mime.text import MIMEText

file_name = Path(__file__).stem
config_path = Path(file_name + ".ini").resolve()
fileConfig(config_path, defaults={'logfilename': Path(file_name + ".log").resolve() })
log = logging.getLogger(__name__)


def config(dic='DEFAULT'):
    config = configparser.ConfigParser()
    config.read(config_path)
    return config[dic]


# TODO methods getting movies
# TODO check IMDB / Rotten Tomatoes rating


def get_smtp_config():
    cf = config('SMTP')
    return  cf.get("host"), \
            cf.get("port"), \
            cf.get("username"), \
            cf.get("password"), \
            cf.get("from"), \
            cf.get("to")

def send_email(num_jack):
    """
    Sends email notification
    """
    host, port, user, passw, fro, to = get_smtp_config()

    title = 'Movies are ready to see!'
    msg_content = '<h2>{title} </h2> <font color="green">MOVIE OK!</font></h2>\n'.format(title=title)
    message = MIMEText(msg_content, 'html')

    message['From'] = 'Movies ' + fro
    message['To'] = 'Movies ' + to
    message['Subject'] = 'Movies of interest!'

    msg_full = message.as_string()

    server = smtplib.SMTP_SSL('{host}:{port}'.format(host=host, port=port))
    server.login(user, passw)
    server.sendmail(fro, [to], msg_full)
    server.quit()


def main():
    conf = config()

    # TODO!

    

if __name__ == '__main__':
    main()
