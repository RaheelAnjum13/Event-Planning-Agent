import streamlit as st
from crewai import Agent, Crew, Task
from crewai_tools import ScrapeWebsiteTool, SerperDevTool
from pydantic import BaseModel
import os
import json


# --- Data Models ---
class VenueDetails(BaseModel):
    name: str
    address: str
    capacity: int
    booking_status: str


class MarketingReport(BaseModel):
    summary: str
    campaigns: list[str]
    estimated_reach: int


# --- Sidebar API Config ---
st.sidebar.title("🔐 API Configuration")
openai_key = st.sidebar.text_input("OpenAI API Key", type="password")
serper_key = st.sidebar.text_input("Serper API Key", type="password")

# --- Tools ---
search_tool = SerperDevTool()
scrape_tool = ScrapeWebsiteTool()

# --- Agents ---
venue_cordinator = Agent(
    role="Venue Coordinator",
    goal="Find and book the most suitable venue for the event",
    tools=[search_tool, scrape_tool],
    verbose=True,
    backstory=(
        "You're a logistics genius who can find a perfect venue for any tech event. "
        "You balance cost, capacity, availability, and quality while ensuring the venue meets the event's needs."
    ),
)

logistics_manager = Agent(
    role="Logistics Manager",
    goal="Handle catering and equipment logistics smoothly",
    tools=[search_tool, scrape_tool],
    verbose=True,
    backstory="You manage catering and technical setup with efficiency and precision.",
)

marketing_communications_agent = Agent(
    role="Marketing and Communications Agent",
    goal="Promote the event and ensure maximum attendance",
    tools=[search_tool, scrape_tool],
    verbose=True,
    backstory="You excel at designing effective marketing campaigns and reaching the right audience.",
)

# --- Main UI ---
st.title("🎯 Event Management AI Planner")

import streamlit as st

with st.form("event_form"):
    event_topic = st.text_input("Event Topic", value="")
    event_description = st.text_area("Event Description", value="")
    event_city = st.text_input("City", value="")
    tentative_date = st.date_input("Event Date")

    # Replacing number_input with text_input and adding placeholder
    expected_participants_input = st.text_input(
        "Expected Participants", placeholder="Enter the Expected Participants"
    )
    budget_input = st.text_input("Budget", placeholder="Enter your Budget")

    venue_type = st.text_input(
        "Preferred Venue Type", placeholder="e.g., Hotel, Banquet Hall, Outdoor, etc."
    )

    submit = st.form_submit_button("Run Event Planner")

    # ---- Validation Logic after form submission ----
    if submit:
        errors = False

        # Validate expected participants
        if expected_participants_input.strip() == "":
            expected_participants = None
        elif expected_participants_input.isdigit():
            expected_participants = int(expected_participants_input)
        else:
            st.error("❌ Expected Participants must be a whole number.")
            errors = True

        # Validate budget
        if budget_input.strip() == "":
            budget = None
        else:
            try:
                budget = float(budget_input)
            except ValueError:
                st.error("❌ Budget must be a valid number (e.g., 1000 or 1000.50).")
                errors = True

        # If no validation errors, process the data
        if not errors:
            st.success("✅ All inputs are valid! Proceeding with event planning...")
            # You now have: event_topic, event_description, event_city,
            # tentative_date, expected_participants, budget, venue_type


# --- Validation & AI Agent Execution ---
if submit:
    # Validate input fields
    if not all(
        [
            openai_key.strip(),
            serper_key.strip(),
            event_topic.strip(),
            event_description.strip(),
            event_city.strip(),
            venue_type.strip(),
        ]
    ):
        st.error("🚨 Please fill in all fields and provide both API keys.")
    elif expected_participants <= 0:
        st.error("🚨 Expected participants must be greater than 0.")
    elif budget <= 0:
        st.error("🚨 Budget must be greater than 0.")
    else:
        # Set environment variables
        os.environ["OPENAI_API_KEY"] = openai_key
        os.environ["OPENAI_MODEL_NAME"] = "gpt-3.5-turbo"
        os.environ["SERPER_API_KEY"] = serper_key

        st.info("⏳ Running AI Agents...")

        event_details = {
            "event_topic": event_topic,
            "event_description": event_description,
            "event_city": event_city,
            "tentative_date": tentative_date.strftime("%Y-%m-%d"),
            "expected_participants": expected_participants,
            "budget": budget,
            "venue_type": venue_type,
        }

        venue_task = Task(
            description=(
                f"Find a venue in {event_city} suitable for hosting a {event_topic}. "
                f"The venue must support at least {expected_participants} participants, "
                f"stay within the budget of {budget}, be available on {tentative_date}, and have appropriate tech facilities. "
                "Return only one most suitable venue as structured JSON."
            ),
            expected_output="Return the venue's name, address, capacity, and booking_status.",
            output_json=VenueDetails,
            output_file="venue_details.json",
            agent=venue_cordinator,
        )

        logistics_task = Task(
            description=(
                f"Arrange catering and equipment for an event happening on {tentative_date} with "
                f"{expected_participants} participants. Ensure all logistics are confirmed and documented."
            ),
            expected_output="Confirmation of all arrangements for food, seating, projectors, mics, and stage setup.",
            agent=logistics_manager,
        )

        marketing_task = Task(
            description=(
                f"Plan a marketing campaign to promote the {event_topic} in {event_city} aiming to reach at least "
                f"{expected_participants} people. Suggest at least 3 channels (e.g., Facebook, local radio, WhatsApp groups)."
            ),
            expected_output="Return summary, campaign list, and estimated audience reach.",
            output_json=MarketingReport,
            output_file="marketing_report.json",
            agent=marketing_communications_agent,
        )

        event_management_crew = Crew(
            agents=[
                venue_cordinator,
                logistics_manager,
                marketing_communications_agent,
            ],
            tasks=[venue_task, logistics_task, marketing_task],
        )

        result = event_management_crew.kickoff(inputs=event_details)

        st.success("🎉 Event Planning Completed")
        st.markdown("### ✅ AI Planning Summary")

        # --- Venue Details ---
        if os.path.exists("venue_details.json"):
            st.subheader("📍 Venue Details")
            try:
                with open("venue_details.json") as f:
                    venue = json.load(f)
                    st.markdown(f"""
**🏢 Name:** {venue["name"]}  
**📍 Address:** {venue["address"]}  
**👥 Capacity:** {venue["capacity"]}  
**📅 Booking Status:** {venue["booking_status"]}  
""")
                    st.download_button(
                        "⬇️ Download Venue JSON",
                        json.dumps(venue, indent=2),
                        file_name="venue_details.json",
                    )
            except Exception as e:
                st.error(f"Error loading venue details: {e}")
        else:
            st.warning("⚠️ Venue details file not found or not properly generated.")

        # --- Marketing Report ---
        if os.path.exists("marketing_report.json"):
            st.subheader("📣 Marketing Report")
            try:
                with open("marketing_report.json") as f:
                    report = json.load(f)
                    st.markdown(
                        f"""
📝 **Summary**: {report["summary"]}  
📊 **Estimated Reach**: {report["estimated_reach"]}  
📌 **Campaigns**:  
"""
                        + "\n".join(f"- {c}" for c in report["campaigns"])
                    )
                    st.download_button(
                        "⬇️ Download Marketing Report",
                        json.dumps(report, indent=2),
                        file_name="marketing_report.json",
                    )
            except Exception as e:
                st.error(f"Error loading marketing report: {e}")
        else:
            st.warning("⚠️ Marketing report file not found.")

        # --- Optional: Agent Summaries ---
        if "tasks_output" in result:
            st.subheader("🧠 Agent Task Summaries")
            for task in result["tasks_output"]:
                if isinstance(task, str):
                    continue
                agent = task.get("agent", "Unknown")
                desc = task.get("description", "")
                summary = task.get("summary", "")
                st.markdown(f"👤 **Agent:** {agent}")
                st.markdown(f"📌 Task: {desc[:120]}...")
                st.markdown(
                    f"🧾 Summary: {summary if summary else 'No summary available.'}"
                )
                st.markdown("---")
