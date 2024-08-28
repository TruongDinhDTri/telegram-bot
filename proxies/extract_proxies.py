import pandas as pd
import json


file_path = './proxies_testing.txt'
save_path = '../ip_list.json'
def read_proxies_from_file(file_path):
    proxies = []
    with open(file_path, 'r') as file:
        for line in file:
            proxy = line.strip()
            if proxy: 
                proxies.append(proxy)
    return proxies

def save_proxies(save_path, proxies):
    with open(save_path, 'w') as file:
        json.dump(proxies, file, indent = 4)

proxies =read_proxies_from_file(file_path)
save_proxies(save_path, proxies)
