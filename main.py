import os
from urllib.parse import urljoin, unquote

import requests
from bs4 import BeautifulSoup


# TODO: Add some try-excepts

# Path to save curiosity images to
pathname = os.path.abspath("curios")

# Curiosity wiki page link
URL = "http://ringofbrodgar.com/wiki/Curiosity"

# Fetch the page and content
page = requests.get(URL)
soup = BeautifulSoup(page.content, 'html.parser')

# List to store our curiosity data
curio_list = []

# Fetch the "craftable" curiosities table
table = soup.find_all("table", class_="sortable wikitable smwtable")[1]

# Iterate through each row in the table and save the data
for row in table.find_all("tr"):
    # Get all columns in the row
    cols = row.find_all('td')

    # Sometimes we get a row with 0 columns, skip those
    if len(cols) > 0:
        # Get just the text in the columns (strip the html)
        cols = [elem.text for elem in cols]

        # Fetch the link in the row (leading to the curiosity wiki page) and get the page
        link = row.find_all("a", href=True)[0]["href"]
        curio_url = urljoin(URL, link)
        curio_page = requests.get(curio_url)
        soup = BeautifulSoup(curio_page.content, 'html.parser')

        # Find the infobox and fetch the curiosity image URL
        infobox = soup.find_all("table", class_="infobox")[0]
        img_src = infobox.find_all("img")[0]["src"]
        img_url = urljoin(URL, img_src)

        # Check to make sure the desired image destination exists, and if not, create it
        if not os.path.isdir(pathname):
            os.makedirs(pathname)

        # Download the image and save it to the folder
        response = requests.get(img_url, stream=True)
        # We use the "unquote" function to convert the HTML URL encodings into normal characters
        filename = os.path.join(pathname, unquote(img_url.split("/")[-1]))
        with open(filename, "wb") as f:
            f.write(response.content)

        # Calculate how many slots a curiosity takes up by dividing it's LP/Hour value by it's  LP/Hour/Size value
        size = int(float(cols[6])/float(cols[7]))

        # Create a dictionary to store each curiosity and append it to
        data = {
            "name": cols[0],
            "base_lp": cols[2],
            "study_time": cols[3],
            "weight": cols[4],
            "size": size,
            "filename": filename
        }
        curio_list.append(data)

# TODO: Populate Postgres database with this data
for item in curio_list:
    print(item)
