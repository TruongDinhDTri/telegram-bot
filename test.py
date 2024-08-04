import requests

url = "https://iplogger.org/logger/"

# Form data
payload = {
    'interval': 'all',
    'filters': '',
    'page': '1',
    'sort': 'created',
    'order': 'desc',
    'code': 'RvwL4KDiL0CZ'
}

# Headers (excluding Content-Type and content-length)
headers = {
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'accept-encoding': 'gzip, deflate, br, zstd',
    'cookie': '_lang=us; _autolang=us; cookies-consent=1721871352; confirmation=Sp67xpXBHZeY226232386sRM; cf_clearance=mKy_IeL4t9gkR.RgTYOfI3jZXlpaSx_0dOUpIcGNjKg-1722676948-1.0.1.1-NTXTjfJEdf.M5J8EmuPlBHdxpIIAfkS1kdzFU.ddpckN8mrWIMGr35wc5HmiFVZxPd.e21zbLVahX.yzUJVu7A; _gid=GA1.2.297228745.1722676948; _gat_gtag_UA_67516667_1=1; cursor=EA0V13j7X6C4p8m672q2N731evRXoOjf; __gads=ID=274ad628c2d89cb5:T=1721871346:RT=1722684676:S=ALNI_MY4Ws2UkMN7nX07T9D-9-5sMwXiQg; __gpi=UID=00000ea5712e9c18:T=1721871346:RT=1722684676:S=ALNI_MbmhnCSq0-U4GUQ4xsC4I0Bt3XJug; __eoi=ID=0577e04acefdaa6d:T=1721871346:RT=1722684676:S=AA-AfjbdAs_F3_y6Jht5js18ETY4; loggers=UnZ3TDRLRGlMMENa; turnback=logger%2FRvwL4KDiL0CZ%2F; FCNEC=%5B%5B%22AKsRol9Gz6cyUpHs4bBmnyUjrwY1o7DDPzhgwqkXRf3GHuMpVpvgYIKXkGEMHP90RQGzmEVkthvAaFgl2GRMaDl2BTwKTBWDR_pVeFsiBv-Jflastj9-GQYAJalWqDjXsE6bxbrl50iOObwXE0wzi1vvimD70mproA%3D%3D%22%5D%5D; integrity=XaMEUk0wsSjoLjltL1HfhVv5; _ga_7FSG7D195N=GS1.1.1722683685.11.1.1722684719.9.0.0; _ga=GA1.2.2040753983.1721871345; 37852530250738181=3; _autolang=us; _lang=us; clhf03028ja=14.241.246.5; cursor=EA0V13j7X6C4p8m672q2N731evRXoOjf',
    'origin': 'https://iplogger.org',
    'priority': 'u=1, i',
    'referer': 'https://iplogger.org/logger/RvwL4KDiL0CZ/',
    'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest'
}

# Perform the POST request
response = requests.post(url, headers=headers, data=payload)

# Print the response
print(response.text)
