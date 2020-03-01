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
from urllib.parse import quote
import json
import smtplib
from email.mime.text import MIMEText
from pprint import pprint
from datetime import datetime

file_name = Path(__file__).stem
config_path = str(Path(file_name + ".ini").resolve())
fileConfig(config_path, defaults={'logfilename': Path(file_name + ".log").resolve() })
log = logging.getLogger(__name__)

def config(dic='DEFAULT'):
    config = configparser.ConfigParser()
    config.read(config_path)
    return config[dic]

conf = config()
API_URL = conf.get('api_url')
IMG_URL = conf.get('img_url')
LOC = conf.get('loc')
OMDB_API_KEY = conf.get('OMDB_API_KEY')


def get_json(url):
    with request.urlopen(url) as resp:
        data = json.loads(resp.read().decode())
        return data


def post_json(body, url):
    jsondata = json.dumps(body)
    jsonbytes = jsondata.encode('utf-8')
    req = request.Request(url)
    req.add_header('Content-Type', 'application/json; charset=utf-8')
    req.add_header('Content-Length', len(jsonbytes))
    resp = json.loads(request.urlopen(req, jsonbytes).read().decode())
    return resp


def get_movies_list():
    url = API_URL + "GetEventsByVenueDescription"
    body = { "description": LOC }
    resp = post_json(body, url)
    nd = []
    for m in resp['data']:
        img_url = IMG_URL + m['Image']
        nd.append({"id": m['UrlLink'], "title": m['Description'], "description": m['EventSummary'],"image": img_url, "release-date": m['ReleaseDate'], "director": m['Director'], "starring": m['Staring'], "duration": m['Duration'], "age-rating": m['RatingIE'], "trailer": m['Trailer'], "url": m['UrlLink']})
    return nd


def get_movie_times(movies):
    url = API_URL + "GetEventDatesAndPerformances"
    for m in movies:
        body = { "eventDescription": m['id'], "eventDate": None, "venueDescription": LOC }
        resp = post_json(body, url)['data']
        evd = []
        for ed in resp['EventDates']:
            times = []
            for st in ed['PerformanceDetails']:
                times.append({"time": st['StartDate'], "screen": st['ScreenNumber']})
            evd.append({"date": ed['EventDate'], "times": times})
        m['showtimes'] = evd
    return movies

def get_movie_ratings(movies):
    for m in movies:
        mtitle = quote(m['title'])
        yr = datetime.strptime(m['release-date'], "%Y-%m-%dT%H:%M:%S").year
        url = f'http://www.omdbapi.com/?t={mtitle}&type=movie&y={yr}&apikey={OMDB_API_KEY}'
        resp = get_json(url)
        if 'Error' not in resp:
            m['genre'] = resp['Genre']
            m['ratings'] = resp['Ratings']
            m['imdbID'] = resp['imdbID']
    return movies

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
    movies = get_movies_list()
    movies = get_movie_times(movies)
    d = get_movie_ratings(movies)
    with open("data.json", 'w') as fp:
        json.dump(d, fp)

    # TODO stick data in to html and send via email

    

if __name__ == '__main__':
    main()
