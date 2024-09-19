import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from smtplib import SMTP, SMTPException

# Load environment variables from .env file
load_dotenv()

# Amazon product URL and target price
URL = "https://www.amazon.com/dp/B075CYMYK6?psc=1&ref_=cm_sw_r_cp_ud_ct_FM9M699VKHTT47YD50Q6"
TARGET_PRICE = 100

# Request headers to simulate a browser visit
header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en"
}

# Getting sensitive information from .env file
email = os.getenv("EMAIL")
password = os.getenv("PASSWORD")
receiver_addrs = os.getenv("RECEIVER_ADRESS")
smtp_addrs = os.getenv("SMTP_ADRESS")

# Fetch product data from Amazon and parse it
try:
    response = requests.get(URL, headers=header)
    response.raise_for_status()  # Check if the request was successful
    contents = response.text
except requests.exceptions.RequestException as e:
    print(f"Error fetching product data: {e}")
    exit()

# Parse HTML using BeautifulSoup
soup = BeautifulSoup(contents, "html.parser")

try:
    # Extract product price
    price_whole = soup.find(name="span", class_="a-price-whole").getText().replace(',', '')
    price_fraction = soup.find(name="span", class_="a-price-fraction").get_text()
    total_price = float(f"{price_whole}{price_fraction}")

    # Extract product description
    product_details = soup.find(id="productTitle")
    product_description = [value.strip() for value in product_details.get_text().split("\r\n")]
    product_info = str(''.join(product_description))
except AttributeError:
    print("Error: Unable to fetch product details. The page layout may have changed.")
    exit()

# Check if the product's price is lower than the target price
if total_price < TARGET_PRICE:
    try:
        # Setup email connection
        with SMTP(smtp_addrs, port=587) as connection:
            connection.ehlo()  # Identify ourselves to the SMTP server
            connection.starttls()  # Secure connection
            connection.ehlo()  # Re-identify after securing connection
            connection.login(user=email, password=password)

            # Send email notification
            connection.sendmail(
                from_addr=email,
                to_addrs=receiver_addrs,
                msg=f"Subject: Lower Price Alert\n\n{product_info} is now ${total_price} \n{URL}".encode("utf-8")
            )
            print("Email sent successfully!")
    except SMTPException as smtp_error:
        print(f"SMTP error occurred: {smtp_error}")
    except Exception as e:
        print(f"An error occurred while sending email: {e}")
else:
    print(f"Price is still ${total_price}, no email sent.")
