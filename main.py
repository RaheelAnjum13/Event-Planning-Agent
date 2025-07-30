import streamlit as st
from crewai import Agent, Crew, Task
from crewai_tools import ScrapeWebsiteTool, SerperDevTool
from pydantic import BaseModel
import os
import json


class VenueDetails(BaseModel):
    name: str
    address: str
    capacity: int
    booking_status: str


class MarketingReport(BaseModel):
    summary: str
    campaigns: list[str]
    estimated_reach: int


st.sidebar.title("API Configuration")
openai_key = st.sidebar.text_input("OpenAI API Key", type="password")
serper_key = st.sidebar.text_input("Serper API Key", type="password")

if openai_key and serper_key:
    os.environ["OPENAI_API_KEY"] = openai_key
    os.environ["OPENAI_MODEL_NAME"] = "gpt-3.5-turbo"
    os.environ["SERPER_API_KEY"] = serper_key
else:
    st.warning(
        "Please enter both OpenAI and Serper API keys in the sidebar to proceed."
    )


search_tool = SerperDevTool()
scrape_tool = ScrapeWebsiteTool()


venue_cordinator = Agent(
    role="Venue Coordinator",
    goal="Find and book the most suitable venue for the event",
    tools=[search_tool, scrape_tool],
    verbose=True,
    backstory=(
        "You're a logistics genius who can find a perfect venue for any tech event."
        " You balance cost, capacity, availability, and quality while ensuring the venue meets the event's needs."
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


st.title("Event Management AI Planner")

with st.form("event_form"):
    event_topic = st.text_input("Event Topic", value="")
    event_description = st.text_area("Event Description", value="")
    event_city = st.text_input("City", value="")
    tentative_date = st.date_input("Event Date")
    expected_participants = st.number_input("Expected Participants", min_value=10)
    budget = st.number_input("Budget", min_value=10000)
    venue_type = st.selectbox(
        "Venue Type",
        [
            "Select...",
            "Conference Hall",
            "Auditorium",
            "Outdoor",
            "Hotel",
            "University Campus",
        ],
    )
    submit = st.form_submit_button("Run Event Planner")


if submit and openai_key and serper_key:
    st.info("Running AI Agents.")

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
        agents=[venue_cordinator, logistics_manager, marketing_communications_agent],
        tasks=[venue_task, logistics_task, marketing_task],
    )

    result = event_management_crew.kickoff(inputs=event_details)

    st.success("Event Planning Completed ✅")
    st.markdown("✅ AI Planning Summary")
    st.markdown("Here are the finalized details by agents:")

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
                    "Download Venue JSON",
                    json.dumps(venue, indent=2),
                    file_name="venue_details.json",
                )
        except Exception as e:
            st.error(f"Error loading venue details: {e}")
    else:
        st.warning("Venue details file not found or not properly generated.")

    if os.path.exists("marketing_report.json"):
        st.subheader("📣 Marketing Report")
        try:
            with open("marketing_report.json") as f:
                report = json.load(f)
                st.markdown(
                    f"""
📝 Summary: {report["summary"]}  
📊 Estimated Reach:** {report["estimated_reach"]}  
📌 Campaigns:  
"""
                    + "\n".join(f"- {c}" for c in report["campaigns"])
                )
                st.download_button(
                    "Download Marketing Report",
                    json.dumps(report, indent=2),
                    file_name="marketing_report.json",
                )
        except Exception as e:
            st.error(f"Error loading marketing report: {e}")
    else:
        st.warning("Marketing report file not found.")

    # --- Optional: Show Agent Task Summaries ---
    if "tasks_output" in result:
        st.subheader("🧠 Agent Task Summaries")
        for task in result["tasks_output"]:
            if isinstance(task, str):
                continue
            agent = task.get("agent", "Unknown")
            desc = task.get("description", "")
            summary = task.get("summary", "")
            st.markdown(f"👤 Agent:** {agent}")
            st.markdown(f"Task: {desc[:120]}...")
            st.markdown(f"Summary: {summary if summary else 'No summary available.'}")
            st.markdown("---")
