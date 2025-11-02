import json
import os
import re
from datetime import datetime, timedelta
import pytz
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from core.utils.llm_interface import LLMInterface
from core.utils.credentials import load_token, save_token

SCOPES = ["https://www.googleapis.com/auth/calendar"]
TZ = pytz.timezone("Europe/Berlin")


class CalendarAgent:
    def __init__(self):
        """Initialize the agent and connect to Google Calendar."""
        self.llm = LLMInterface(model="llama3:8b")
        self.service = self._connect()

    # ---------------------------------------------------------------
    # Connect to Google Calendar (WSL compatible)
    # ---------------------------------------------------------------
    def _connect(self):
        creds_data = load_token("google_calendar")
        creds = None

        if creds_data:
            creds = Credentials.from_authorized_user_info(json.loads(creds_data), SCOPES)
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
                save_token("google_calendar", creds.to_json())
                print("Token refreshed successfully.")

        if not creds or not creds.valid:
            print("\n Browser could not be opened automatically.")
            print("Falling back to manual authentication.")
            print("Copy this URL into your Windows browser, allow access, then wait for redirect.")

            cred_path = os.path.join(os.path.dirname(__file__), "credentials/credentials.json")
            flow = InstalledAppFlow.from_client_secrets_file(cred_path, SCOPES)
            creds = flow.run_local_server(host="127.0.0.1", port=8081, open_browser=False)
            save_token("google_calendar", creds.to_json())

        print("Connected to Google Calendar.")
        return build("calendar", "v3", credentials=creds)

    # ---------------------------------------------------------------
    # Interpret the query with an LLM
    # ---------------------------------------------------------------
    def interpret_query(self, query: str):
        now = datetime.now(TZ)
        today_str = now.strftime("%A, %B %d, %Y %H:%M %Z")
        tz_name = "Europe/Berlin"

        prompt = f"""
        You are NEXCAI — a precise AI assistant that controls the user's Google Calendar.

        Current local time: {today_str} ({tz_name})
        User message: "{query}"

        Goals:
        - Detect intent: "create" | "list" | "delete".
        - For "create": resolve all relative times to ISO 8601 in {tz_name}.
        - For "list": if the user mentions a specific period like "tomorrow", "today",
          "this week", "next week", "on Monday", etc., return explicit ISO 8601
          "start_time" and "end_time" covering that whole period
          (e.g., "tomorrow" => 00:00 to 23:59:59 of tomorrow in {tz_name}).
          If the user says only "next N days", you may return "days": N instead.
        - For "delete": return a partial "summary" to match events by title.

        Respond ONLY with valid JSON:
        {{
          "actions": [
            {{
              "intent": "create",
              "event": {{
                "summary": "Title",
                "start_time": "YYYY-MM-DDTHH:MM:SS±HH:MM",
                "end_time":   "YYYY-MM-DDTHH:MM:SS±HH:MM",
                "description": "optional",
                "location": "optional"
              }}
            }},
            {{
              "intent": "list",
              "start_time": "YYYY-MM-DDTHH:MM:SS±HH:MM",
              "end_time":   "YYYY-MM-DDTHH:MM:SS±HH:MM",
              "days": null
            }},
            {{
              "intent": "delete",
              "summary": "partial title"
            }}
          ]
        }}

        Examples:
        - "Show me tomorrow" →
          {{ "actions": [{{ "intent": "list",
            "start_time": "<tomorrow 00:00 ISO>",
            "end_time": "<tomorrow 23:59:59 ISO>",
            "days": null
          }}] }}

        - "Show next 3 days" →
          {{ "actions": [{{ "intent": "list", "start_time": "", "end_time": "", "days": 3 }}] }}

        IMPORTANT: Respond only with JSON. No explanations or extra text.
        """

        response = self.llm.chat(prompt)

        try:
            # Extract only the first {...} JSON block
            json_str = re.search(r"\{[\s\S]*\}", response).group(0)
            parsed = json.loads(json_str)
            return parsed.get("actions", [])
        except Exception as e:
            print("LLM returned invalid JSON. Raw output below:\n", response)
            print("Error:", e)
            return []

    # ---------------------------------------------------------------
    # Create event
    # ---------------------------------------------------------------
    def create_event(self, summary, start_time, end_time, description=None, location=None):
        event = {
            "summary": summary,
            "location": location,
            "description": description,
            "start": {"dateTime": start_time, "timeZone": "Europe/Berlin"},
            "end": {"dateTime": end_time, "timeZone": "Europe/Berlin"},
        }

        result = self.service.events().insert(calendarId="primary", body=event).execute()
        return f"Event '{result['summary']}' created! {result['htmlLink']}"

    # ---------------------------------------------------------------
    # List events (supports either explicit time range or N days)
    # ---------------------------------------------------------------
    def list_events(self, start_time=None, end_time=None, days=None):
        now = datetime.now(TZ)

        if start_time and end_time:
            # Use explicit ISO times provided by LLM
            pass
        else:
            # Default to "now → now + days"
            days = days or 1
            start_time = now.isoformat()
            end_time = (now + timedelta(days=days)).isoformat()

        events = (
            self.service.events()
            .list(
                calendarId="primary",
                timeMin=start_time,
                timeMax=end_time,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
            .get("items", [])
        )

        if not events:
            return "No upcoming events found."

        formatted = []
        for e in events:
            # Get the ISO string (dateTime or all-day date)
            dt_str = e["start"].get("dateTime", e["start"].get("date"))

            # Convert to datetime and extract local time if possible
            try:
                event_time = datetime.fromisoformat(dt_str).astimezone(TZ)
                time_str = event_time.strftime("%H:%M")
            except Exception:
                # Fallback (for all-day events without a specific time)
                time_str = "All day"

            formatted.append(f"• {e['summary']} — {time_str}")

        return "Upcoming events:\n" + "\n".join(formatted)

    # ---------------------------------------------------------------
    # Delete event (cancel)
    # ---------------------------------------------------------------
    def delete_event(self, summary_part):
        """Find events matching title substring and delete them."""
        now = datetime.utcnow().isoformat() + "Z"
        events = (
            self.service.events()
            .list(calendarId="primary", timeMin=now, maxResults=20, singleEvents=True, orderBy="startTime")
            .execute()
            .get("items", [])
        )

        matches = [e for e in events if summary_part.lower() in e["summary"].lower()]

        if not matches:
            return f"No event found matching '{summary_part}'."

        deleted = []
        for e in matches:
            self.service.events().delete(calendarId="primary", eventId=e["id"]).execute()
            deleted.append(e["summary"])

        return f"Deleted events: {', '.join(deleted)}"

    # ---------------------------------------------------------------
    # Run the query
    # ---------------------------------------------------------------
    def run(self, query: str):
        actions = self.interpret_query(query)
        if not actions:
            return "I couldn't understand your request."

        responses = []
        for action in actions:
            intent = action.get("intent")

            if intent == "create":
                event = action.get("event", {})
                responses.append(self.create_event(**event))

            elif intent == "list":
                start_time = action.get("start_time")
                end_time = action.get("end_time")
                days = action.get("days")

                responses.append(
                    self.list_events(
                        start_time=start_time,
                        end_time=end_time,
                        days=days if days is not None else 1
                    )
                )

            elif intent == "delete":
                summary = action.get("summary", "")
                responses.append(self.delete_event(summary))

        return "\n\n".join(responses)
