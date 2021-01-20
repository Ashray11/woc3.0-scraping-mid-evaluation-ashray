# selenium
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
# email sending
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
# read csv files
import pandas as pd
import time


def Scrap():
    # Save last modified time log data
    timeLog = pd.read_csv(r'C:\Users\Hetal\PycharmProjects\woc3.0-ecommerce-price-tracker-ashray\lastModified.csv')
    timeLog.at[0, 'lastModified'] = str(round(time.time()))
    timeLog.to_csv('lastModified.csv', index=False)

    # create webdriver object
    driver = webdriver.Chrome("C:\Program Files (x86)\chromedriver.exe")

    file = open(r"info.txt", "r")
    URLX, myPrice, myEmail = file.read().split(",")
    file.close()

    URL = URLX
    try:
        driver.get(URL)
    except:
        return "Invalid URL. Try again :("
    name = ""
    website = ""
    price = ""
    available = True

    # get element
    if URL[12:20] == "flipkart":
        # fixed class name for product name
        element = driver.find_element_by_class_name("B_NuCI").text
        name = element
        print(name)
        # fixed class name for product price
        element = driver.find_element_by_class_name("_16Jk6d").text
        price = element
        print(price)

        website = "Flipkart"

    elif URL[12:18] == "amazon":
        # Check availability
        try:
            element = driver.find_element_by_id("availability").text
        except NoSuchElementException as exception:
            available = False
        if available:
            # distinguish b/w deal of day and normal product
            dayDeal = True
            try:
                # fixed class name if deal of day product
                element = driver.find_element_by_id("priceblock_dealprice_lbl").text
                # print(element)
            except NoSuchElementException as exception:
                # class does not exist means not deal of day product
                dayDeal = False

            # fixed class name for product name irrespective of deal of day or normal product
            element = driver.find_element_by_id("productTitle").text
            name = element
            print(name)
            if dayDeal:
                # if deal of day product then use corresponding id
                element = driver.find_element_by_id("priceblock_dealprice").text
                price = element
                print(price)
            else:
                # if normal product then use corresponding id
                element = driver.find_element_by_id("priceblock_ourprice").text
                price = element
                print(price)

            website = "Amazon"
        else:
            return "Unavailable. Email will be sent when available within budget."

    elif URL[12:20] == "snapdeal":
        try:
            element = driver.find_element_by_class_name("sold-out-err").text
            available = False
        except NoSuchElementException as exception:
            available = True
        if available:
            # fixed class name for product name
            element = driver.find_element_by_class_name("pdp-e-i-head").text
            name = element
            print(name)
            # fixed class name for product price
            element = driver.find_element_by_class_name("payBlkBig").text
            price = "₹" + element
            print(price)

            website = "Snapdeal"

        else:
            return "Unavailable. Email will be sent when available within budget."

    else:
        return "We dont work with this website :("

    # send email if conditions are satisfied
    if available and name != "" and price != "" and myPrice >= price[1:len(price)] and website != "":
        mail_content = '''<pre>Hello Customer!<br>
The product you looked for on %s is now available within your budget.<br>
The datails are:
    Name: %s
    Price: %s
    <a href="%s">LINK</a>
    </pre>''' % (website, name, price, URL)
        # The mail addresses and password
        validation = pd.read_csv(r'C:\Users\Hetal\PycharmProjects\woc3.0-ecommerce-price-tracker-ashray\validation.csv')
        sender_address = validation["Email"][0]
        sender_pass = validation["Pass"][0]
        receiver_address = myEmail
        # Setup the MIME
        message = MIMEMultipart()
        message['From'] = sender_address
        message['To'] = receiver_address
        message['Subject'] = 'Product available within budget!'  # The subject line
        # The body and the attachments for the mail
        message.attach(MIMEText(mail_content, 'html'))

        # Create SMTP session for sending the mail
        session = smtplib.SMTP('smtp.gmail.com', 587)  # use gmail with port
        session.starttls()  # enable security
        session.login(sender_address, sender_pass)  # login with mail_id and password
        text = message.as_string()
        session.sendmail(sender_address, receiver_address, text)
        session.quit()

        print('Mail Sent')
        return True
    return False


from IPython.display import clear_output

# run the application
repeatAfter = 10
timeLog = pd.read_csv(r'C:\Users\Hetal\PycharmProjects\woc3.0-ecommerce-price-tracker-ashray\lastModified.csv')
diff = round(time.time()) - timeLog['lastModified'][0]
if diff < repeatAfter:
    time.sleep(repeatAfter - diff)
while True:
    clear_output(wait=True)
    end = Scrap()
    if end == True:  # email sent. terminate.
        break
    elif end == False:  # email not sent
        print("Will notify when available within range.")
    else:
        print(end)

    time.sleep(repeatAfter)
