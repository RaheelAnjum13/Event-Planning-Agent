# 🎯 Event Management AI Planner

An AI-powered event planning assistant built with **Streamlit**, **CrewAI**, and the **Serper API**. This smart tool coordinates venue selection, logistics, and marketing for tech events using autonomous agents powered by GPT.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-brightgreen.svg)
![CrewAI](https://img.shields.io/badge/CrewAI-Autonomous_Agents-red.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## 🌟 Features

### 🧠 Multi-Agent AI Coordination

- Uses **CrewAI** to assign tasks to dedicated AI agents:
  - 📍 _Venue Coordinator_ – Finds and suggests suitable venues
  - 📦 _Logistics Manager_ – Manages catering and technical equipment
  - 📣 _Marketing Agent_ – Designs campaigns and estimates reach

### 🔍 Web Search & Scraping

- Real-time data using **Serper API** and **ScrapeWebsiteTool**
- Agents can intelligently gather live information about venues, vendors, etc.

### 📝 Structured Outputs

- Agents return structured data in JSON format:
  - `venue_details.json`
  - `marketing_report.json`

### 🎛️ Streamlit UI

- Easy-to-use form for entering event information
- Clear display of venue details and marketing plan
- Downloadable reports
- Error handling and agent summaries

---

## 🚀 Getting Started

### 📦 Prerequisites

- Python 3.8+
- OpenAI API Key ([Get yours](https://platform.openai.com/account/api-keys))
- Serper API Key ([Get one](https://serper.dev/))

### 🧰 Installation

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/event-management-planner.git
cd event-management-planner

# 2. Create a virtual environment
python -m venv .venv

# 3. Activate the virtual environment
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the Streamlit app
streamlit run main.py

event-management-planner/
├── .venv/                    # Virtual environment (excluded in .gitignore)
├── .env                      # API keys and environment variables
├── .gitignore                # Ignore venv, .env, and output files
├── app.py                    # CrewAI agent and task logic
├── main.py                   # Streamlit frontend
├── requirements.txt          # Project dependencies
├── marketing_report.json     # Output: AI-generated marketing insights
├── venue_details.json        # Output: Selected venue data
└── README.md                 # This file

```
