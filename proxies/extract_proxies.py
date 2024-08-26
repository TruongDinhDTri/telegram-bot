import pandas as pd
import json

# Step 1: Read the CSV file
df = pd.read_csv('proxy_list.csv')

# Step 2: Extract the IP and Port columns
ip_addresses = df['ip']
ports = df['port']

# Step 3: Combine IP and Port into the final proxy value
proxy_values = ip_addresses + ':' + ports.astype(str)

# Display the result
print(proxy_values.tolist())
# Writing to a JSON file
with open('ip_list.json', 'w') as json_file:
    json.dump(proxy_values.tolist(), json_file)

with open('ip_list.json', 'r') as file:
    proxies = json.load(file)
    
print(proxies[0])
