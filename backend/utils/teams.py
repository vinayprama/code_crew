# import requests
# from msal import ConfidentialClientApplication
# import os

# def get_graph_token():
#     client_id = os.getenv("AZURE_CLIENT_ID")
#     client_secret = os.getenv("AZURE_CLIENT_SECRET")
#     tenant_id = os.getenv("AZURE_TENANT_ID")

#     authority = f"https://login.microsoftonline.com/{tenant_id}"
#     scopes = ["https://graph.microsoft.com/.default"]

#     app = ConfidentialClientApplication(client_id, authority=authority, client_credential=client_secret)
#     token_response = app.acquire_token_for_client(scopes=scopes)
#     if "access_token" not in token_response:
#         raise Exception("Could not obtain access token for Microsoft Graph.")
#     return token_response["access_token"]

# def create_teams_meeting(subject, start_time, end_time, attendees):
#     access_token = get_graph_token()
#     url = "https://graph.microsoft.com/v1.0/me/onlineMeetings"

#     # Build attendees array
#     attendee_list = [
#         {"identity": {"user": {"id": email}}}
#         for email in attendees
#     ]
#     payload = {
#         "startDateTime": start_time,  # ISO8601 format
#         "endDateTime": end_time,      # ISO8601 format
#         "subject": subject,
#         # Optionally add attendees
#         # "participants": {
#         #     "attendees": attendee_list
#         # }
#     }
#     headers = {
#         "Authorization": f"Bearer {access_token}",
#         "Content-Type": "application/json"
#     }
#     resp = requests.post(url, json=payload, headers=headers)
#     resp.raise_for_status()
#     data = resp.json()
#     return data["joinWebUrl"]

# import requests
# from msal import ConfidentialClientApplication
# import os
# from dotenv import load_dotenv
# load_dotenv()


# def get_graph_token():
#     client_id = os.getenv("AZURE_CLIENT_ID")
#     client_secret = os.getenv("AZURE_CLIENT_SECRET")
#     tenant_id = os.getenv("AZURE_TENANT_ID")

#     authority = f"https://login.microsoftonline.com/{tenant_id}"
#     scopes = ["https://graph.microsoft.com/.default"]

#     app = ConfidentialClientApplication(client_id, authority=authority, client_credential=client_secret)
#     token_response = app.acquire_token_for_client(scopes=scopes)
#     if "access_token" not in token_response:
#         raise Exception("Could not obtain access token for Microsoft Graph.")
#     return token_response["access_token"]

# def create_teams_meeting(subject, start_time, end_time, attendees):
#     access_token = get_graph_token()
#     user_email = attendees[0]  # Organizer's email
#     url = f"https://graph.microsoft.com/v1.0/users/{user_email}/onlineMeetings"

#     attendee_list = [
#         {"identity": {"user": {"id": email}}}
#         for email in attendees
#     ]
#     payload = {
#         "startDateTime": start_time,  # ISO8601 UTC with Z
#         "endDateTime": end_time,
#         "subject": subject,
#         "participants": {
#             "attendees": attendee_list
#         }
#     }
#     headers = {
#         "Authorization": f"Bearer {access_token}",
#         "Content-Type": "application/json"
#     }
#     print("DEBUG Teams API payload:", payload)
#     resp = requests.post(url, json=payload, headers=headers)
#     print("DEBUG Teams API response:", resp.text)
#     resp.raise_for_status()
#     data = resp.json()
#     return data["joinWebUrl"]