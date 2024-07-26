import requests
import json
import os


import argparse

# Parse command line arguments
parser = argparse.ArgumentParser(description='Process token and user ID.')
parser.add_argument('--token', type=str, help='Authentication token')
parser.add_argument('--user_id', type=str, help='User ID')
parser.add_argument('--cipher', type=str, help='Cipher')
parser.add_argument('--keywords', type=str, help='Comma-separated list of Keywords')
parser.add_argument('--title_query', type=str, help='Comma-separated list of Title Query')

args = parser.parse_args()

token = args.token
user_id = args.user_id
cipher = args.cipher
keywords = args.keywords.split(',') if args.keywords else []
title_query = args.title_query.split(',') if args.title_query else []

# If token or user_id is not provided, perform authentication
if not token or not user_id or not cipher:
    # Define the login credentials
    login_url = 'https://dashboard.leonar.app/api/1.1/wf/auth'
    login_payload = {
        "email": "elod@apeconsulting.xyz",
        "password": "MyPass123!!"
    }

    # Define the headers
    headers = {
        'Content-Type': 'application/json'
    }

    # Send the login request
    response = requests.post(login_url, headers=headers, data=json.dumps(login_payload))

    # Check if the login was successful
    if response.status_code != 200:
        print(f"Login request failed with status code {response.status_code}")
        exit()

    response_data = response.json()
    if response_data.get("status") != "success":
        print("Login failed. Check your credentials.")
        exit()

    token = response_data["response"]["token"]
    user_id = response_data["response"]["user_id"]
    print(f"Token: {token}")
    print(f"User ID: {user_id}")

    cipher_url = 'https://dashboard.leonar.app/api/1.1/wf/update-cipher'
    cipher_headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    cipher_response = requests.post(cipher_url, headers=cipher_headers)
    # Check if the cipher request was successful
    if cipher_response.status_code != 200:
        print(f"Cipher request failed with status code {cipher_response.status_code}")
        exit()
    cipher_data = cipher_response.json()
    if "response" not in cipher_data or "results" not in cipher_data["response"]:
        print("No response data found in cipher request.")
        exit()
    cipher = cipher_data["response"]["results"].get("cipher")
    if cipher:
        print(f"Cipher: {cipher}")
    else:
        print("Cipher not found in the response.")

if not keywords or not title_query:
    print("No keywords or title query provided, skipping profiles request.")
    exit()

full_query_name = "_".join(keywords + title_query)
if full_query_name:
    os.makedirs(full_query_name, exist_ok=True)
    print(f"Folder created for query: {full_query_name}")
else:
    print("Query name not found, skipping folder creation.")
profiles_url = 'https://api.leonar.app/candidates'
profiles_payload = {
    "cipher": cipher,
    "user_id": user_id,
    "title_query": title_query,
    "keywords": keywords,
    "page": 1
}
profiles_headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {token}'
}
profiles_response = requests.post(profiles_url, headers=profiles_headers, json=profiles_payload)
# Check if the profiles request was successful
if profiles_response.status_code != 200:
    print(f"Profiles request failed with status code {profiles_response.status_code}")
    exit()
profiles_data = profiles_response.json()
print(f"Profiles Data: {profiles_data}")
if "hits" not in profiles_data:
    print("No response data found in profiles request.")
    exit()
profiles = profiles_data["hits"]["hits"]
print(f"Profiles: {profiles}")
for profile in profiles:
    profile_id = profile.get("_id")
    if profile_id:
        full_profile_payload = {
            "cipher": cipher,
            "user_id": user_id,
            "_id": profile_id
        }
        full_profile_response = requests.post(profiles_url, headers=profiles_headers, json=full_profile_payload)
        # Check if the full profile request was successful
        if full_profile_response.status_code != 200:
            print(f"Full profile request failed with status code {full_profile_response.status_code}")
            continue
        full_profile_data = full_profile_response.json()
        if "_id" not in full_profile_data:
            print("No response data found in full profile request.")
            continue
        first_name = full_profile_data["_source"].get("first_name", "unknown")
        last_name = full_profile_data["_source"].get("last_name", "unknown")
        profile_filename = f"{first_name}_{last_name}.json"
        with open(os.path.join(full_query_name, profile_filename), 'w') as profile_file:
            json.dump(full_profile_data, profile_file, indent=4)
        print(f"Profile saved: {profile_filename}")
    else:
        print("Profile ID not found, skipping full profile request.")
    
