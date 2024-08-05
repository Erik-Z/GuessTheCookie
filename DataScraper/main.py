import json
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import requests
import base64

BLOCK_RESOURCE_NAMES = [
    'adzerk',
    'analytics',
    'cdn.api.twitter',
    'doubleclick',
    'exelator',
    'facebook',
    'fontawesome',
    'google',
    'google-analytics',
    'googletagmanager',
]

BLOCK_RESOURCE_TYPES = [
    'beacon',
    'csp_report',
    'font',
    'image',
    'imageset',
    'media',
    'object',
    'texttrack',
]


def get_dynamic_soup(url: str) -> BeautifulSoup:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.set_default_timeout(0)
        page.route("**/*", intercept_route)
        page.goto(url)
        soup = BeautifulSoup(page.content(), 'html5lib')
        browser.close()
        return soup


def intercept_route(route):
    if route.request.resource_type in BLOCK_RESOURCE_TYPES:
        print(f'blocking background resource {route.request} blocked type "{route.request.resource_type}"')
        return route.abort()
    if any(key in route.request.url for key in BLOCK_RESOURCE_NAMES):
        print(f"blocking background resource {route.request} blocked name {route.request.url}")
        return route.abort()
    return route.continue_()


# def download_image(url, image_name) -> str:
#     data = requests.get(url, verify=False).content
#
#     if data.startswith(b"data:image/gif;base64,"):
#         data = base64.b64decode(data.split(b',')[1])
#
#     file_name = "./data/cookie_profile_img/" + image_name + ".webp"
#     with open(file_name, 'wb') as image_file:
#         image_file.write(data)
#
#     return file_name

def download_image(url, image_name) -> str:
    data = ""
    try:
        # Check if the URL is a data URL
        if url.startswith('data:image/gif;base64,'):
            data = base64.b64decode(url.split(',', 1)[1])
        else:
            response = requests.get(url, verify=False)
            data = response.content

        file_name = "./data/cookie_profile_img/" + image_name + ".webp"

        with open(file_name, 'wb') as image_file:
            image_file.write(data)

        return file_name
    except Exception as e:
        print(url)
        print(data)
        print(e)
        quit(1)

URL = "https://cookierunkingdom.fandom.com/wiki/List_of_Cookies"

soup = get_dynamic_soup(URL)
table = soup.find_all('div', attrs={'class': 'loccard'})
cookie_list = []
with sync_playwright() as p:
    #TODO: Check cookies.json and see if cookie exists. If it does skip scraping the data.
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.set_default_timeout(0)
    page.route("**/*", intercept_route)
    for row in table:
        cookie = {}
        cookie_url = 'https://cookierunkingdom.fandom.com' + row.div.a['href']
        page.goto(cookie_url)
        cookie_soup = BeautifulSoup(page.content(), 'html5lib')
        cookie['name'] = cookie_soup.find('h2', attrs={'data-source': 'name'}).text.strip()
        cookie['profile_image_url'] = download_image(cookie_soup.find('h2', attrs={'data-source': 'name'}).img['src'], cookie['name'])
        cookie['rarity'] = cookie_soup.find('div', attrs={'class': 'pi-data-value'}).a.img['alt']

        type_and_position = cookie_soup.find_all('td', attrs={'class': 'pi-horizontal-group-item'})
        if len(type_and_position) == 0:
            cookie['attack_type'] = "Unknown"
            cookie['position'] = "Unknown"
        else:
            cookie['attack_type'] = type_and_position[0].a.img['alt']
            cookie['position'] = type_and_position[1].a.img['alt']
        cookie['link'] = cookie_url
        cookie_list.append(cookie)
        print(cookie)

with open('./data/cookies.json', 'w') as f:
    json.dump(cookie_list, f)

print("Cookies.json created successfully")
