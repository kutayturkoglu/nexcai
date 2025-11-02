from core.orchestrator.router import route_query
from core.agents.weather.agent import WeatherAgent
from core.agents.general.agent import GeneralAgent
from core.agents.calendar.agent import CalendarAgent
def main():
    print("🤖 NEXCAI Modular Assistant Ready")
    print("(type 'exit' to quit)\n")

    weather_agent = WeatherAgent()
    general_agent = GeneralAgent()
    calendar_agent = CalendarAgent()

    while True:
        query = input("You: ")
        if query.lower() in ["exit", "quit", "q"]:
            print("Goodbye!")
            break

        intent = route_query(query)
        print(f"[Router → {intent.upper()}]")

        if intent == "weather":
            reply = weather_agent.run(query)
        elif intent == "calendar":
            reply = calendar_agent.run(query)
        else:
            reply = general_agent.run(query)

        print("NEXCAI:", reply)
        print()

if __name__ == "__main__":
    main()
