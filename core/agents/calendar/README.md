# Calendar Agent (Google Calendar, OAuth on WSL/Windows)

This module lets your NEXCAI assistant create, list, and delete events on your Google Calendar using OAuth 2.0.
It’s designed to work on Windows + WSL (no Linux GUI required).

## Features
* Natural-language → structured actions via LLM (create, list, delete)
* WSL-friendly OAuth (run_local_server on 127.0.0.1)
* Token persistence & auto-refresh (no repeated logins)
* Timezone-aware (Europe/Berlin by default)

## Folder Structure
```bash
├── core/
│   └── agents/
│       └── calendar/
│           ├── agent.py
│           ├── setup.py
│           └── credentials/
│               └── credentials.json
└── tokens/
    └── google_calendar.json
```
## 1 - Create a Google Cloud Project & Enable API
* Go to Google Cloud Console → create/select a project.
* Open APIs & Services → Enabled APIs & services → + Enable APIs.
* Enable Google Calendar API.

## 2 - Configure OAuth Consent Screen
* APIs & Services → OAuth consent screen
* User Type: External (recommended for personal projects).
* Fill in app name, support email, etc.
* Add yourself as a Test user (same Google account you’ll authenticate with).
* Save/publish.

If you skip adding your email as a test user, you’ll get:
“Ineligible accounts not added / app_not_verified / access_denied”

## 3 - Create OAuth Client (Desktop)
* APIs & Services → Credentials → Create Credentials → OAuth client ID
* Application type: Desktop app
* Download the JSON; rename it to credentials.json
* Place it at:

```bash
core/agents/calendar/credentials/credentials.json
```

✅ Desktop app clients include the correct http://127.0.0.1 redirect URIs out of the box.

## 4 - Install Dependencies
Use the same environment as your app (example with ```pip```):
```bash
pip install google-auth google-auth-oauthlib google-api-python-client pytz
```
(Your project likely already includes these in ```requirements.txt.```)

## 5 - First Run (OAuth on WSL)
* The agent will attempt to start a local OAuth receiver at ```http://127.0.0.1:8081/``` and open your browser.
* On WSL with no default browser, it prints an auth URL. Copy–paste that URL into your Windows browser, complete login/consent. Google will redirect back to 127.0.0.1:8081 (works across WSL ↔ Windows).

After success, a refreshable token is saved to:

```bash
tokens/google_calendar.json
```
You won’t need to log in again unless you delete that file or the refresh token becomes invalid.

## 6 - Using the CalendarAgent in Your App
* The agent handles:
    * Authentication (stores refreshable token in tokens/google_calendar.json)
    * Natural language → create / list / delete actions
    * ISO time handling in Europe/Berlin by default
Typical Integration:
```bash
from core.agents.calendar.agent import CalendarAgent

agent = CalendarAgent()

print(agent.run("Create dinner with Alex tomorrow 7pm to 8pm"))
print(agent.run("Show me all events tomorrow"))
print(agent.run("Cancel my dinner event"))
```

## 7 - Security & Git Hygiene
* NEVER commit ```credentials.json``` or any token files:
```bash
credentials.json
tokens/*.json
core/agents/calendar/credentials/credentials.json
core/agents/calendar/token.json
```
* Add them to .gitignore.

## 8 - Timezone
* Default TZ is Europe/Berlin in ```agent.py```. Change it if needed:
```bash
import pytz
TZ = pytz.timezone("Europe/Berlin")
```

## 9 - Troubleshooting
```webbrowser.Error: could not locate runnable browser```
* Expected on WSL. We already set ```open_browser=False``` and print a URL to open manually.

```invalid_client / unauthorized_client```
* Wrong or corrupt ```credentials.json```

Make sure it’s an OAuth client for Desktop app and placed at:

```core/agents/calendar/credentials/credentials.json```

```access_denied``` / “app not verified” / “ineligible account”
* Add your Google account under OAuth consent → Test users.

Redirect fails to ```localhost:8080```
* We use ```127.0.0.1:8081.``` Ensure that port is free.
* If you run something on ```8081```, change the port in ```agent.py```.

Token not refreshing / asks login often
* Ensure you save tokens (our agent calls ```save_token("google_calendar", ...)```)
* Check that ```tokens/google_calendar.json``` is writable.

WSL networking quirks
* Use ```127.0.0.1``` (not ```localhost```).
* Open the printed URL in Windows default browser when prompted.

## 10 - Scopes
Current scope:
```bash
https://www.googleapis.com/auth/calendar
```
Gives read/write.
If you only need read access, use:
```bash
https://www.googleapis.com/auth/calendar.readonly
```
(Then re-authenticate and re-save tokens.)

## 11 - Extending
* Support more intents (update, move, invite attendees)
* Add reminders (event['reminders'])
* Use calendar IDs beyond "primary" if needed
* Swap timezone dynamically per user