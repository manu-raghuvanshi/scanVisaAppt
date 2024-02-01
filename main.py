import time
from bs4 import BeautifulSoup
from email.message import EmailMessage
import json
import ssl
import smtplib
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

import os
from dotenv import load_dotenv

load_dotenv()

while True:
    print(time.strftime("%H:%M:%S", time.localtime()))
    # instantiate webdriver
    chrome_driver_path = os.getenv("chrome_driver_path")
    options = Options()
    options.add_argument("--headless")
    service = Service(chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=options)

    # open web page
    url = os.getenv("url")
    driver.get(url)
    time.sleep(2)

    # load page
    page_source = driver.page_source

    # Close Driver
    driver.quit()

    # load content from selenium webdriver into beautiful soup
    soup = BeautifulSoup(page_source, "html.parser")
    for tr in soup.find_all("tr"):
        if "data-index" in tr.attrs:
            if tr["data-index"] == "9":
                if (
                    tr.contents[1].get_text() == "B1/B2 (Regular)"
                    and tr.contents[0].get_text() == "NEW DELHI VAC"
                ):
                    if (
                        "Jan" in tr.contents[2].get_text()
                        or "Feb" in tr.contents[2].get_text()
                        or "Mar" in tr.contents[2].get_text()
                        or "Apr" in tr.contents[2].get_text()
                    ):
                        message = {
                            "location": tr.contents[0].get_text(),
                            "visa_type": tr.contents[1].get_text(),
                            "earliest_date_available": tr.contents[2].get_text(),
                            "last_checked": tr.contents[5].get_text(),
                        }
                        print(message)
                        subject = "Visa Slot Alert"
                        email_sender = "manu.raghuvanshi92@gmail.com"
                        email_password = os.getenv("check_visa_slot_password")
                        email_receivers = [
                            "manu.raghuvanshi92@gmail.com",
                            "heerakchugh@gmail.com",
                        ]
                        for email_receiver in email_receivers:
                            email_obj = EmailMessage()
                            email_obj["From"] = email_sender
                            email_obj["To"] = email_receiver
                            email_obj["Subject"] = subject
                            email_obj.set_content(json.dumps(message))

                            ssl_context = ssl.create_default_context()

                            with smtplib.SMTP_SSL(
                                "smtp.gmail.com", 465, context=ssl_context
                            ) as smtp:
                                smtp.login(email_sender, email_password)
                                smtp.sendmail(
                                    email_sender, email_receiver, email_obj.as_string()
                                )

                        break

    time.sleep(120)
