import json
import requests
import pandas as pd
import argparse
import re
import numpy as np
import matplotlib.pyplot as plt
import os
from fpdf import FPDF 

import email, smtplib, ssl

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import getpass 


df_ratings = pd.read_csv("ratings_reduced.csv") 

df_ratings = df_ratings.groupby("movieId").agg({"rating":"mean"})*2
df_ratings = df_ratings.rename(columns={"rating": "tmdbRating"})

def bring_rating(movieId):
    if movieId in df_ratings.index:
        return round(df_ratings["tmdbRating"][movieId],2)




def year_column(title):
    match = re.search(r'.+\((\d+)\)',title)
    if match:
        return int(match.group(1))


def clean_title(title):
    year_clean = title.split("(")[0].strip()
    the_clean = year_clean.split(", The")[0]
    return the_clean



def get_movies(movie):
    from dotenv import load_dotenv
    load_dotenv(".env")

    token = os.getenv("Omdb_APIKEY")
    url = F"http://www.omdbapi.com/?apikey={token}&t={movie}"

    response = requests.get(url)
    data = response.json()
    return data


def convert_to_float(score):
    if score !=  'N/A':
        score = float(score)
        return score
    else:
        return score



def report(df,film):
    pdf = FPDF('P','mm','A4')
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)

    pdf.cell(190, 10, 'REPORTING',1,1,'C')
    pdf.set_font('Arial', 'B', 16)

    #1
    num_col = len(df.columns)
    w = 190
    h = 277
    font_type = ('Arial', 'B', 16)
    pdf.set_font(*font_type)
    pdf.set_text_color(0)
    pdf.set_draw_color(0)
    pdf.cell(w,10,'','TB',1,'C')
    pdf.cell(w,10,'Global Data',1,1,'C')
    pdf.set_line_width(0.2)
    for col in df.columns:
        pdf.cell(w/num_col,10,col,1,0,'C')
    pdf.ln()

    pdf.set_fill_color(243,95,95)
    font_type = ('Arial', '', 12)
    pdf.set_font(*font_type)


    # iterating columns
    for index,row in df.iterrows():
        pdf.cell(w/num_col,10,str(row["Stats"]),1,0,'C')
        pdf.cell(w/num_col,10,str(row["Metascore"]),1,0,'C')
        pdf.cell(w/num_col,10,str(row["imdbRating"]),1,0,'C')
        pdf.cell(w/num_col,10,str(row["tmdbRating"]),1,1,'C')
    pdf.ln()

    pdf.cell(w,10,'','TB',1,'C')
    pdf.cell(w,10,film + " " + "Scores",1,1,'C')
    pdf.image('foo.png',30, 170, w=150, h=100)

    pdf.output("reporting.pdf",'F')



def email():
    subject = "An email with your report"
    body = "This is an email with your requested report"
    sender_email = "guillermo.ironhack.tests@gmail.com"
    receiver_email = "guillermo.ironhack.tests@gmail.com"
    password = getpass.getpass(prompt="Type your password and press enter:")

    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message["Bcc"] = receiver_email  # Recommended for mass emails

    # Add body to email
    message.attach(MIMEText(body, "plain"))

    filename = "reporting.pdf"  # In same directory as script

    # Open PDF file in binary mode
    with open(filename, "rb") as attachment:
        # Add file as application/octet-stream
        # Email client can usually download this automatically as attachment
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())

    # Encode file in ASCII characters to send by email    
    encoders.encode_base64(part)

    # Add header as key/value pair to attachment part
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {filename}",
    )

    # Add attachment to message and convert message to string
    message.attach(part)
    text = message.as_string()

    # Log in to server using secure context and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, text)


    

