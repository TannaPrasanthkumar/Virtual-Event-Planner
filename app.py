import streamlit as st
from langchain import hub
from composio_langchain import ComposioToolSet, Action, App
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os
import pytz
from datetime import datetime, timedelta, date

# Load environment variables
load_dotenv()
os.environ["COMPOSIO_API_KEY"] = os.getenv("COMPOSIO_KEY")
os.environ["COMPOSIO_LOGGING_LEVEL"] = "debug"
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

# Get current date and time in IST
ist_timezone = pytz.timezone("Asia/Kolkata")
current_datetime_ist = datetime.now(ist_timezone)
current_date_str = current_datetime_ist.strftime("%Y-%m-%d")
tomorrow_date_str = (current_datetime_ist + timedelta(days=1)).strftime("%Y-%m-%d")

# Initialize tools
composio_tools = ComposioToolSet()
calendar_tools = composio_tools.get_tools([
    Action.GOOGLECALENDAR_FIND_FREE_SLOTS,
    Action.GOOGLECALENDAR_CREATE_EVENT,
    Action.GOOGLECALENDAR_FIND_EVENT
])

# Add IST timezone to tools configuration
for tool in calendar_tools:
    if hasattr(tool, 'args_schema') and 'timezone' in tool.args_schema.schema().get('properties', {}):
        tool.args_schema.schema()['properties']['timezone']['default'] = "Asia/Kolkata"

# LLM setup
llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0)

# Enhanced prompt template with current date context and IST timezone instructions
prompt_template = ChatPromptTemplate.from_messages([
    ("system", f"""You are an AI agent responsible for managing Google Calendar actions.
    
    IMPORTANT: Today's date is {current_datetime_ist.strftime("%A, %B %d, %Y")} and tomorrow is {(current_datetime_ist + timedelta(days=1)).strftime("%A, %B %d, %Y")}.
    
    Always use Indian Standard Time (IST/Asia/Kolkata) for all calendar operations.
    
    When handling relative dates:
    - "Today" means {current_date_str}
    - "Tomorrow" means {tomorrow_date_str}
    - "Next week" starts on {(current_datetime_ist + timedelta(days=7 - current_datetime_ist.weekday())).strftime("%Y-%m-%d")}
    
    For date and time formats, convert all relative dates to ISO format (YYYY-MM-DD) for dates and 24-hour format (HH:MM) for times.
    When the user doesn't specify a timezone, assume they mean Indian Standard Time (IST).
    
    Based on the user's request, determine which calendar tool is most appropriate:
    - Use FIND_FREE_SLOTS when the user wants to know available times
    - Use CREATE_EVENT when the user wants to schedule a new event or meeting
    - Use FIND_EVENT when the user wants to search for existing events
    
    Always confirm the actual calendar dates in your response (e.g., "March 8th, 2025" rather than just saying "tomorrow")."""),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

# Create agent executor with all tools
agent = create_tool_calling_agent(
    llm=llm,
    tools=calendar_tools,
    prompt=prompt_template,
)
executor = AgentExecutor(
    agent=agent,
    tools=calendar_tools,
    verbose=True,
    handle_parsing_errors=True,
)

# Process relative date references in user input
def preprocess_user_input(input_text):
    # Replace relative date terms with specific dates
    processed_text = input_text
    processed_text = processed_text.replace("today", f"today ({current_date_str})")
    processed_text = processed_text.replace("tomorrow", f"tomorrow ({tomorrow_date_str})")
    return processed_text

# Streamlit Interface with improved UI
st.set_page_config(
    page_title="Google Calendar Assistant",
    page_icon="📅",
    layout="wide"
)

# Custom CSS for enhanced UI
st.markdown("""
<style>
    .profile-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
    }
    .github-btn {
        display: inline-flex;
        align-items: center;
        background-color: #24292e;
        color: white;
        padding: 8px 16px;
        border-radius: 6px;
        text-decoration: none;
        font-weight: bold;
        margin-top: 10px;
    }
    .main-header {
        background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .calendar-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    .feature-card {
        background-color: white;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    .result-card {
        background-color: #f9f9f9;
        border-left: 4px solid #4b6cb7;
        padding: 15px;
        margin-top: 20px;
        border-radius: 0 8px 8px 0;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar for profile, settings and help
with st.sidebar:
    # Profile Section
    st.markdown('<div class="profile-card">', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image("https://via.placeholder.com/150", width=80)
    with col2:
        st.markdown("### Prasanth kumar Tanna")
        st.markdown("✉️ tannaprasanthkumar76@gmail.com")
        st.markdown("📱 +91 96663 93011")
    
    st.markdown('<a href="https://github.com/yourusername" target="_blank" class="github-btn">'+
                '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="white" style="margin-right: 8px">'+
                '<path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>'+
                '</svg>GitHub Profile</a>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Settings Section
    st.subheader("⚙️ Settings")
    st.write("🕒 **Timezone**: Indian Standard Time (IST)")
    current_time = current_datetime_ist.strftime("%d %b %Y, %H:%M")
    st.write(f"📆 Current time: {current_time}")
    
    st.divider()
    
    # Help Section
    st.subheader("💡 Tips & Examples")
    st.write("This assistant helps you manage your Google Calendar using natural language. Simply type your request and the AI will determine the appropriate action to take.")
    
    st.markdown("#### Try these commands:")
    example_requests = [
        f"🔍 Find me free time slots for tomorrow ({tomorrow_date_str}) between 2pm and 6pm",
        f"📝 Schedule a meeting with the team on {(current_datetime_ist + timedelta(days=2)).strftime('%A (%Y-%m-%d)')} at 10am for 1 hour",
        "📋 Show me all my meetings for next week"
    ]
    for example in example_requests:
        st.markdown(f"- *{example}*")
    
    st.divider()
    
    # Footer with credits
    st.markdown("#### 🛠️ Built with")
    tech_stack = {
        "Streamlit": "https://streamlit.io",
        "LangChain": "https://www.langchain.com",
        "Composio": "https://composio.dev",
        "Gemini 1.5 Pro": "https://ai.google.dev"
    }
    
    for tech, url in tech_stack.items():
        st.markdown(f"[![{tech}]({url}/favicon.ico)]({url}) [{tech}]({url})", unsafe_allow_html=True)

# Main content
# Header with gradient background
st.markdown('<div class="main-header">', unsafe_allow_html=True)
st.markdown('<div class="calendar-icon">📅</div>', unsafe_allow_html=True)
st.markdown('# Smart Calendar Assistant')
st.markdown('### Manage your schedule with natural language')
st.markdown('</div>', unsafe_allow_html=True)

# Display current date prominently
st.markdown(f"**Today:** {current_datetime_ist.strftime('%A, %B %d, %Y')} (IST)")

# Features showcase
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown('<div class="feature-card">', unsafe_allow_html=True)
    st.markdown("### 🔍 Find Free Time")
    st.markdown("Discover available slots in your schedule that work for everyone")
    st.markdown('</div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="feature-card">', unsafe_allow_html=True)
    st.markdown("### 📝 Schedule Events")
    st.markdown("Create new meetings and appointments with natural language")
    st.markdown('</div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="feature-card">', unsafe_allow_html=True)
    st.markdown("### 📋 View Calendar")
    st.markdown("Check your existing appointments and upcoming events")
    st.markdown('</div>', unsafe_allow_html=True)

# Create tabs for different interaction modes
tab1, tab2 = st.tabs(["💬 Quick Ask", "📋 Detailed Request"])

with tab1:
    user_input = st.text_area("What would you like to do with your calendar?", 
                             placeholder=f"Example: Schedule a meeting with John tomorrow ({tomorrow_date_str}) at 3pm for 30 minutes", 
                             height=100)
    col1, col2 = st.columns([1, 5])
    with col1:
        process_button = st.button("📤 Process", type="primary")

with tab2:
    col1, col2 = st.columns(2)
    with col1:
        event_title = st.text_input("📌 Event Title", placeholder="Team Meeting")
        event_date = st.date_input("📅 Date", value=current_datetime_ist.date())
        location = st.text_input("📍 Location", placeholder="Conference Room A or Video Call")
    with col2:
        start_time = st.time_input("🕒 Start Time", value=current_datetime_ist.replace(hour=10, minute=0).time())
        duration = st.number_input("⏱️ Duration (minutes)", min_value=15, max_value=480, value=30, step=15)
        attendees = st.text_input("👥 Attendees (comma separated emails)", placeholder="john@example.com, jane@example.com")
    
    description = st.text_area("📝 Description", placeholder="Meeting agenda or notes", height=100)
    
    create_event_button = st.button("📅 Create Event", type="primary")
    if create_event_button:
        # Format the detailed input as a natural language request
        formatted_request = f"Schedule a meeting titled '{event_title}' on {event_date} at {start_time} for {duration} minutes"
        if location:
            formatted_request += f" at {location}"
        if attendees:
            formatted_request += f" with {attendees}"
        if description:
            formatted_request += f". Description: {description}"
        user_input = formatted_request
        process_button = True

# Process request (works for both tabs)
if process_button and user_input:
    # Preprocess user input to include explicit dates
    processed_input = preprocess_user_input(user_input)
    
    with st.spinner("📊 Processing your request..."):
        # Create expandable section for debug info
        with st.expander("🔍 Debug Information", expanded=False):
            st.write("Request being processed:")
            st.write("Original input: " + user_input)
            st.write("Processed input: " + processed_input)
            st.write("Current date (IST): " + current_date_str)
            st.write("Tomorrow date (IST): " + tomorrow_date_str)
        
        # Get response from LangChain agent
        response = executor.invoke({"input": processed_input})
        
        # Display the full response for debugging
        with st.expander("🔄 Raw Response", expanded=False):
            st.json(response)
        
        # Display response in a nice format
        st.success("✅ Request completed!")
        
        # Extract and display the output in a user-friendly way
        if "output" in response:
            st.markdown('<div class="result-card">', unsafe_allow_html=True)
            st.markdown("### 📊 Result:")
            st.markdown(response["output"])
            
            # If there's structured data in the response, show it nicely
            if "intermediate_steps" in response:
                try:
                    result_data = None
                    for step in response["intermediate_steps"]:
                        if isinstance(step[1], dict) and len(step[1]) > 0:
                            result_data = step[1]
                            break
                    
                    if result_data:
                        # Format the result data in a more user-friendly way
                        st.markdown("### 📅 Calendar Information:")
                        
                        # Format free slots differently
                        if "freeSlots" in str(result_data):
                            st.markdown("#### ⏰ Free Time Slots:")
                            if isinstance(result_data.get("freeSlots"), list):
                                for slot in result_data.get("freeSlots", []):
                                    start = slot.get("start", {}).get("dateTime", "")
                                    end = slot.get("end", {}).get("dateTime", "")
                                    if start and end:
                                        start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                                        end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
                                        start_ist = start_dt.astimezone(ist_timezone)
                                        end_ist = end_dt.astimezone(ist_timezone)
                                        st.markdown(f"- 🕒 {start_ist.strftime('%I:%M %p')} to {end_ist.strftime('%I:%M %p')}")
                            else:
                                st.markdown("🎉 No specific free slots found or entire requested period is free.")
                        
                        # Format events differently
                        elif "items" in result_data:
                            st.markdown("#### 📋 Events Found:")
                            for event in result_data.get("items", []):
                                summary = event.get("summary", "Unnamed event")
                                start = event.get("start", {}).get("dateTime", event.get("start", {}).get("date", ""))
                                if start:
                                    try:
                                        start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                                        start_ist = start_dt.astimezone(ist_timezone)
                                        st.markdown(f"- 📌 **{summary}**: {start_ist.strftime('%B %d, %Y at %I:%M %p')}")
                                    except:
                                        st.markdown(f"- 📌 **{summary}**: {start}")
                        
                        # Format created event differently
                        elif "id" in result_data and "summary" in result_data:
                            st.markdown("#### ✅ Event Created:")
                            summary = result_data.get("summary", "Unnamed event")
                            start = result_data.get("start", {}).get("dateTime", result_data.get("start", {}).get("date", ""))
                            if start:
                                try:
                                    start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                                    start_ist = start_dt.astimezone(ist_timezone)
                                    st.markdown(f"📅 **{summary}** scheduled for {start_ist.strftime('%B %d, %Y at %I:%M %p')}")
                                except:
                                    st.markdown(f"📅 **{summary}** scheduled for {start}")
                except Exception as e:
                    st.error(f"❌ Error formatting response: {str(e)}")
            st.markdown('</div>', unsafe_allow_html=True)
elif process_button:
    st.warning("⚠️ Please enter your request")

# Version information and attribution
st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    st.markdown("**Version 1.0.0** | Last updated: March 2025")
with col2:
    st.markdown("Created by **Your Name** | [GitHub](https://github.com/TannaPrasanthkumar/Virtual-Event-Planner)")