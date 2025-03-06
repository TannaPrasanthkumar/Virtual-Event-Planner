📅 Google Calendar Assistant
An AI-powered assistant to manage your Google Calendar using natural language. This app uses Streamlit, LangChain, Composio, and Google Gemini (1.5 Pro) to help you find free slots, create events, and check existing meetings, all while handling dates and times in Indian Standard Time (IST).

🚀 Features
🔍 Find Free Time: Check for available slots in your calendar.
📝 Schedule Events: Book meetings with attendees and descriptions.
📋 View Events: Search and view your upcoming events.
🕒 Handles relative dates like today, tomorrow, and next week accurately in IST.
🌐 Easy-to-use interface built with Streamlit.
🛠️ Tech Stack
Streamlit
LangChain
Composio
Google Gemini 1.5 Pro
🧰 Setup Instructions
1. Clone the repository:
bash
Copy
Edit
git clone https://github.com/yourusername/google-calendar-assistant.git
cd google-calendar-assistant
2. Install the required packages:
bash
Copy
Edit
pip install -r requirements.txt
3. Create a .env file:
ini
Copy
Edit
COMPOSIO_KEY=your_composio_api_key
GOOGLE_API_KEY=your_google_api_key
4. Run the Streamlit app:
bash
Copy
Edit
streamlit run app.py
💡 Example Commands
Try asking:

Find free time:
"Find me free time slots for tomorrow between 2pm and 6pm"
Schedule event:
"Schedule a meeting with the team on Friday at 10am for 1 hour"
View events:
"Show me all my meetings for next week"
📷 Screenshots
Homepage	Quick Ask	Detailed Request
👨‍💻 Author
Prasanth Kumar Tanna
✉️ tannaprasanthkumar76@gmail.com
📱 +91 96663 93011
GitHub

⚡ License
This project is licensed under the MIT License.

🌟 Acknowledgements
Thanks to Composio for seamless API integrations.
Thanks to Google AI for the powerful Gemini model.
Thanks to the LangChain ecosystem for the agent framework.
