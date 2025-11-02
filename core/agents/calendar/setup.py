import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from core.utils.credentials import save_token
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar"]

def setup_calendar():
    """
    Starts OAuth flow for Google Calendar API and stores credentials.
    Works in WSL or headless Linux (no GUI browser).
    """
    cred_path = os.path.join(os.path.dirname(__file__), "credentials/credentials.json")

    flow = InstalledAppFlow.from_client_secrets_file(cred_path, SCOPES)

    try:
        creds = flow.run_local_server(port=8080)
    except Exception:
        print("\n Browser could not be opened automatically.")
        print("Falling back to manual authentication.")
        print("Copy this URL into your Windows browser, allow access, then paste the code here.\n")

        auth_url, _ = flow.authorization_url(prompt='consent')
        print("->", auth_url)
        code = input("\nPaste the authorization code here: ").strip()
        token = flow.fetch_token(code=code)

        creds = Credentials.from_authorized_user_info({
            "token": token.get("access_token"),
            "refresh_token": token.get("refresh_token"),
            "token_uri": flow.client_config["token_uri"],
            "client_id": flow.client_config["client_id"],
            "client_secret": flow.client_config["client_secret"],
            "scopes": SCOPES
        })

    save_token("google_calendar", creds.to_json())

    service = build("calendar", "v3", credentials=creds)
    print("\nGoogle Calendar setup completed and token saved successfully.")
    return service
