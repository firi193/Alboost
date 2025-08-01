# streamlit_app.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import streamlit as st
import requests
import json
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import pandas as pd
import docx
from ui.components.time_selector import time_range_selector
from google_auth_oauthlib.flow import Flow
try:
    from ga4_utils import get_user_properties
    GOOGLE_ANALYTICS_AVAILABLE = True
except ImportError:
    GOOGLE_ANALYTICS_AVAILABLE = False
    def get_user_properties(credentials):
        return []
import plotly.express as px
from urllib.parse import urlencode

# Import database functions
try:
    # Try multiple import paths
    try:
        from workflows.server.db.onboarding_db import save_onboarding_data
    except ImportError:
        # Try relative import
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'workflows', 'server', 'db'))
        from onboarding_db import save_onboarding_data
except ImportError as e:
    print(f"Database import error: {e}")
    # Fallback if database module is not available
    def save_onboarding_data(**kwargs):
        return {
            "success": False, 
            "error": "Database module not available",
            "message": "Database module not available"
        }


# Load environment variables
load_dotenv()
api_key = os.getenv("VULTR_API_KEY")
collection_name = os.getenv("VULTR_COLLECTION_NAME")
client_id = os.getenv("GOOGLE_CLIENT_ID")
client_secret = os.getenv("GOOGLE_CLIENT_SECRET")


flow = Flow.from_client_config(
    {
        "web": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost:8501"],  # update this when deployed
        }
    },
    scopes=["https://www.googleapis.com/auth/analytics.readonly"],
    redirect_uri="http://localhost:8501"
)



def extract_text_from_file(file):
    if file.type == "application/pdf":
        pdf = PdfReader(file)
        return "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
    elif file.type in ["text/plain"]:
        content = file.read().decode("utf-8")
        print(content)
        return content
    elif file.type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
        doc = docx.Document(file)
        return "\n".join([para.text for para in doc.paragraphs])
    else:
        return "Unsupported file type."

st.set_page_config(page_title="AI Campaign Assistant", layout="wide")

st.title("📢 AI Campaign Assistant")
st.markdown("Plan, generate, and deploy marketing content with AI agents.")

tab0, tab1_insights, tab1_strategy, tab2, tab3, tab4 = st.tabs(["onboarding", "Campaign Insights", "Campaign Strategy", "Campaign KPIs", "File Uploader", "Social Accounts"])


with tab0:
    st.header("👋 Onboarding")
    st.markdown("Welcome to the AI Campaign Assistant! This tool helps you plan, generate, and deploy marketing campaigns using AI agents.")

    # Show existing onboarding data if available
    if "onboarding_id" in st.session_state:
        st.info(f"📋 You have existing onboarding data (ID: {st.session_state['onboarding_id']})")
        if st.button("🔄 Start New Onboarding"):
            # Clear the session state to start fresh
            del st.session_state["onboarding_id"]
            st.rerun()

    # 1. Brand & Business Info
    with st.expander("1. Business and Brand Info"):
        st.markdown("You can either fill this out or upload brand documents like pitch decks, brand guidelines, etc.")
        uploaded_brand_files = st.file_uploader("Upload Brand Files", type=["pdf", "docx", "pptx"], accept_multiple_files=True)
        
        brand_name = st.text_input("Brand Name")
        industry = st.selectbox("Industry", ["Skincare", "Fashion", "Tech", "Food", "Other"])
        product = st.text_input("Core Product or Service")
        voice = st.text_area("Describe your brand voice (e.g. clean, playful, professional)")
        aesthetic = st.text_area("Describe your visual aesthetic (e.g. minimal, lush, retro)")

    # 2. Campaign Goal
    with st.expander("2. Campaign Goal"):
        campaign_objective = st.selectbox("Objective", ["Awareness", "Engagement", "Conversion", "Retention"])
        campaign_type = st.selectbox("Campaign Type", ["New product launch", "Seasonal promo", "Rebrand", "Other"])
        urgency = st.selectbox("Timeline/Urgency", ["High", "Medium", "Low"])
        channels = st.multiselect("Channels of Focus", ["Instagram", "TikTok", "SEO", "Email", "Web", "Influencers"])

    # 3. Audience Profile
    with st.expander("3. Audience Profile"):
        st.markdown("Fill out what you know. You can also upload customer personas or surveys here.")
        uploaded_audience_docs = st.file_uploader("Upload Audience Docs", type=["pdf", "docx"], accept_multiple_files=True)

        age_range = st.text_input("Age Range (e.g. 18–30)")
        location = st.text_input("Primary Location(s)")
        gender = st.text_input("Gender Identity (optional)")
        values = st.text_area("Psychographic Values (e.g. eco-conscious, wellness, etc.)")
        interests = st.text_area("Interests and Lifestyle")
        behavior = st.text_area("Behavioral Insights (e.g. shopping habits, media usage)")

    # 4. Confirmation / Submit
    st.markdown("---")
    if st.button("✨ Submit"):
        # Collect all the form data
        onboarding_data = {
            "brand_name": brand_name,
            "industry": industry,
            "product": product,
            "voice": voice,
            "aesthetic": aesthetic,
            "campaign_objective": campaign_objective,
            "campaign_type": campaign_type,
            "urgency": urgency,
            "channels": list(channels) if channels else [],
            "age_range": age_range,
            "location": location,
            "gender": gender,
            "values": values,
            "interests": interests,
            "behavior": behavior
        }
        
        # Show a spinner while saving
        with st.spinner("Saving your onboarding information..."):
            # Save to database
            result = save_onboarding_data(**onboarding_data)
            
            if result.get("success"):
                st.success(f"✅ {result.get('message', 'Onboarding data saved successfully')}")
                if "id" in result:
                    st.info(f"Onboarding ID: {result['id']}")
                    # Store the onboarding ID in session state for future use
                    st.session_state["onboarding_id"] = result["id"]
                
                # Show next steps
                st.markdown("### 🎯 Next Steps:")
                st.markdown("1. **Review your data** in the Campaign Strategy tab")
                st.markdown("2. **Upload files** in the File Uploader tab")
                st.markdown("3. **Connect analytics** in the Social Accounts tab")
                
            else:
                error_message = result.get('message', 'Unknown error occurred')
                st.error(f"❌ {error_message}")
                if "error" in result:
                    st.error(f"Error details: {result['error']}")



import json

def load_json_with_platform(filepath: str, platform: str) -> list:
    """
    Load JSON data with robust encoding handling.
    """
    import codecs
    
    try:
        # Try UTF-8 first (most common for modern files)
        with codecs.open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except UnicodeDecodeError:
        try:
            # Try UTF-8 with BOM
            with codecs.open(filepath, 'r', encoding='utf-8-sig') as f:
                data = json.load(f)
        except UnicodeDecodeError:
            # Last resort: try with error handling
            with codecs.open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                data = json.load(f)
    
    # Attach platform field to each record
    for item in data:
        item.setdefault("platform", platform)
    
    return data


from datetime import datetime

def filter_posts_by_date(posts, start_date, end_date, date_key=None):
    """
    Filter posts by date range, automatically detecting the date field.
    """
    filtered = []
    print(f"🔍 Filtering {len(posts)} posts from {start_date} to {end_date}")
    
    for post in posts:
        # Auto-detect date key if not provided
        if date_key is None:
            if "created_at" in post:
                date_key = "created_at"
            elif "date" in post:
                date_key = "date"
            else:
                print(f"⚠️ No date field found in post: {list(post.keys())}")
                continue
        
        try:
            date_str = post[date_key]
            print(f" Processing date: {date_str} (key: {date_key})")
            
            # Handle different date formats
            if "T" in date_str:  # ISO datetime format: "2025-06-30T10:45:00Z"
                post_date = datetime.fromisoformat(date_str.replace("Z", "")).date()
            else:  # Simple date format: "2025-07-30"
                post_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            
            print(f" Parsed date: {post_date}")
            
            if start_date <= post_date <= end_date:
                filtered.append(post)
                print(f"✅ Post included: {post_date}")
            else:
                print(f"❌ Post excluded: {post_date} (not in range {start_date} to {end_date})")
                
        except Exception as e:
            print(f"⚠️ Error processing date '{date_str}' with key '{date_key}': {e}")
            continue
    
    print(f"✅ Found {len(filtered)} posts in date range")
    return filtered



# Step 2: Load post data from all platforms
ga4_data = load_json_with_platform("ui/mock_ga4_data.json", "ga4")           # Already in mock
meta_data = load_json_with_platform("ui/mock_meta_data.json", "meta")         # Already in mock
twitter_data = load_json_with_platform("ui/mock_twitter_data.json", "twitter")  # Changed from x_data

# Step 3: Combine raw post data
all_posts = ga4_data + meta_data + twitter_data         # Updated variable name


# --- Tab 1: Campaign Insights Generation ---
with tab1_insights:
    
    st.header("🧠 Campaign Insights Generation")
    # Inside your layout / sidebar / tab section:
    start_date, end_date = time_range_selector(key="insights_tab")
    print(f"🎯 Selected date range: {start_date} to {end_date}")

    filtered_posts = filter_posts_by_date(all_posts, start_date, end_date)

    # Check if we have onboarding data
    if "onboarding_id" in st.session_state:
        st.success(f"✅ Using onboarding data (ID: {st.session_state['onboarding_id']})")
        
        # New comprehensive research button
        if st.button("🔍 Generate Comprehensive Insights (with Qloo Insights)"):
            with st.spinner("Conducting comprehensive research with Qloo insights..."):
                try:
                    # Import and use the researcher agent
                    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
                    from workflows.core.researcher_agent import ResearcherAgent
                    
                    researcher = ResearcherAgent(
                        name="streamlit_researcher",
                        initial_state={},
                        context={}
                    )
                    
                    # # Conduct comprehensive research
                    # research_result = researcher.conduct_comprehensive_research(
                    #     st.session_state["onboarding_id"]
                    # )

                    # Step 4: Call full strategic analysis
                    research_result = researcher.generate_strategic_analysis_and_plan(
                        onboarding_id=st.session_state["onboarding_id"],  # Fix: use session state value
                        performance_data=filtered_posts,
                        type="insights"  # or "insights"
                    )

                    
                    if research_result.get("success"):
                        st.success("✅ Comprehensive research completed!")
                        
                        # Display results in expandable sections
                        with st.expander("📊 Campaign Insights", expanded=True):
                            st.markdown(research_result.get("campaign_insights", ""))
                        
                        # with st.expander("📋 Campaign Plan"):
                        #     st.markdown(research_result.get("campaign_plan", ""))
                        
                        with st.expander("🎯 Performance Analysis"):
                            st.text(research_result.get("performance_analysis", ""))
                        
                        # with st.expander("📈 Qloo Data"):
                        #     qloo_data = research_result.get("qloo_data", {})
                        #     if qloo_data:
                        #         st.json(qloo_data)
                        #     else:
                        #         st.info("No Qloo data available")
                        
                        # Store results in session state for other tabs
                        st.session_state["research_results"] = research_result
                        
                    else:
                        st.error(f"❌ Research failed: {research_result.get('error', 'Unknown error')}")
                        
                except Exception as e:
                    st.error(f"❌ Error during research: {str(e)}")
                    st.info("💡 Make sure all environment variables are set (QLOO_API_KEY, etc.)")
    
    # # Original form-based strategy generation
    # with st.form("campaign_form"):
    #     project_type = st.selectbox("Project Type", ["Web3 Launch", "Product Marketing", "Event Promotion"])
    #     goal = st.text_area("Campaign Goal", "Drive engagement and sign-ups for our upcoming launch.")
    #     submitted = st.form_submit_button("Generate Basic Strategy")

    # if submitted:
    #     with st.spinner("Calling AI agents..."):
    #         response = requests.post(
    #             "http://localhost:8000/campaign-request",
    #             json={"goal": goal, "projectType": project_type}
    #         )
    #         result = response.json()

    #         if response.status_code != 200:
    #             st.error(f"Error: {result.get('error', 'Unknown error occurred.')}")
    #             st.stop()

    #         st.success("Strategy Generated!")
    #         strategy = result.get("strategy", {})

    #         st.markdown("### 🧠 Suggested Strategy Overview")
    #         st.markdown(f"**Goal:** {strategy.get('goal', 'N/A')}")

    #         st.markdown("### 🔍 Research Summary")
    #         st.text_area("Research Summary", value=strategy.get("research_summary", ""), height=200, disabled=True)

    #         st.markdown("### 📌 Key Findings")
    #         key_points = strategy.get("key_findings", [])
    #         if isinstance(key_points, list) and all(isinstance(kp, dict) for kp in key_points):
    #             for idx, item in enumerate(key_points, start=1):
    #                 with st.container():
    #                     st.markdown(f"**Insight {idx}:** {item.get('insight', '')}")
    #                     st.markdown(f"📝 {item.get('details', '')}")
    #                     st.markdown("---")
    #         else:
    #             st.warning("Key findings are not in expected format.")
    #             st.text_area("Key Findings (raw)", value=str(key_points), height=200, disabled=True)

    #         if "tweets" in result and result["tweets"]:
    #             st.markdown("### 🐦 Suggested Tweets")
    #             for tweet in result["tweets"]:
    #                 st.write(f"- {tweet}")

# --- Tab 1: Campaign Strategy Generation ---
with tab1_strategy:
    st.header("🧠 Campaign Strategy Generation")
    # Inside your layout / sidebar / tab section:
    start_date, end_date = time_range_selector(key="strategy_tab")
    filtered_posts = filter_posts_by_date(all_posts, start_date, end_date)

    st.markdown("Generate a comprehensive campaign strategy based on your research insights.")
    
    # Check if we have research results
    if "research_results" in st.session_state:
        research_result = st.session_state["research_results"]
        
        if research_result.get("success"):
            # Check if campaign plan already exists
            if "campaign_plan" in research_result:
                st.success("✅ Campaign strategy ready!")
                st.markdown("### 📋 Campaign Strategy")
                st.markdown(research_result["campaign_plan"])
            else:
                # Generate campaign plan from existing insights
                st.info("🔄 Generating campaign strategy from existing insights...")
                with st.spinner("Creating campaign strategy..."):
                    try:
                        # Import and create researcher agent (same as insights tab)
                        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
                        from workflows.core.researcher_agent import ResearcherAgent
                        
                        researcher = ResearcherAgent(
                            name="streamlit_researcher",
                            initial_state={},
                            context={}
                        )

                        # Call the method on the researcher instance
                        research_result = researcher.generate_strategic_analysis_and_plan(
                            onboarding_id=st.session_state["onboarding_id"],
                            performance_data=filtered_posts,
                            type="plan"
                        )
                        
                        if research_result.get("success"):
                            st.success("✅ Campaign strategy generated!")
                            st.markdown("### 📋 Campaign Strategy")
                            st.markdown(research_result.get("campaign_plan", ""))
                            
                            # Update session state with the plan
                            st.session_state["research_results"]["campaign_plan"] = research_result.get("campaign_plan", "")
                        else:
                            st.error(f"❌ Strategy generation failed: {research_result.get('error', 'Unknown error')}")
                        
                    except Exception as e:
                        st.error(f"❌ Error generating strategy: {str(e)}")
        else:
            st.error("❌ No valid research data available")
    else:
        st.info("💡 Complete the research in the Campaign Insights tab first to generate your strategy.")
    

# --- Tab 2: Campaign KPIs (Dashboard) ---
with tab2:
    st.header("📊 Campaign Performance Dashboard")
    
    # Add time range selector for the dashboard
    start_date, end_date = time_range_selector(key="dashboard_tab")
    
    # Filter posts based on selected date range
    filtered_posts = filter_posts_by_date(all_posts, start_date, end_date)
    
    if len(filtered_posts) > 0:
        # Use the new dashboard with real data
        from ui.components.dashboard import render_social_media_dashboard
        render_social_media_dashboard(filtered_posts)
    else:
        st.warning(f"⚠️ No posts found in the selected date range ({start_date} to {end_date}). Please try a different time period.")
        
        # Fallback to old dashboard with mock data
        st.info("Showing mock data instead:")
        from ui.components.dashboard import render_dashboard
        render_dashboard()

# --- Tab 3: File Uploader ---
with tab3:
    st.header("📂 Upload Customer or CRM Data")
    from ui.components.file_uploader import file_uploader_component
    uploaded_file, df, extracted_text = file_uploader_component()

    if df is not None:
        st.markdown("✅ DataFrame loaded. Ready for agents.")
        st.session_state["uploaded_df"] = df

    elif extracted_text:
        st.markdown("✅ Document text extracted. Ready to index.")
        st.text_area("Extracted Content", value=extracted_text[:1000] + "...", height=200, disabled=True)

        if st.button("🔁 Index to Vultr Vectorstore"):
            if not api_key or not collection_name:
                st.error("Missing `VULTR_API_KEY` or `VULTR_COLLECTION_NAME` in environment.")
            else:
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "content": extracted_text,
                    "description": f"Content from {uploaded_file.name if uploaded_file else 'uploaded file'}",
                    "auto_chunk": True,
                    "auto_embed": True
                }

                try:
                    response = requests.post(
                        f"https://api.vultrinference.com/v1/vector_store/{collection_name}/items",
                        headers=headers,
                        data=json.dumps(payload)
                    )

                    if response.status_code == 200:
                        st.success("✅ Submitted successfully!")
                    elif response.status_code == 403:
                        st.warning("🔒 Unauthorized: Please check your API key or collection name.")
                    else:
                        st.error("❌ Failed to submit to the vector store.")
                        st.caption(f"(Code: {response.status_code})")

                except Exception as e:
                    st.warning("⚠️ Could not connect to the vector store API.")
                    print("Exception during Vultr POST request:", e)

    else:
        st.info("Upload a file to begin.")


with tab4:
    option = st.sidebar.radio("Select Data Source", ["GA4", "Twitter/X (Mock)", "Facebook/Meta (Mock)"])

    if option == "GA4":
        if not GOOGLE_ANALYTICS_AVAILABLE:
            st.header("Connect your Google Analytics")
            st.warning("⚠️ Google Analytics modules not available. Please install required dependencies:")
            st.code("pip install google-analytics-admin google-analytics-data google-auth-oauthlib")
            st.info("For now, you can use the mock data options below.")
        else:
            st.header("Connect your Google Analytics")

        if "credentials" not in st.session_state:

            # Initialize OAuth Flow
            if "flow" not in st.session_state:
                st.session_state["flow"] = Flow.from_client_config(
                    {
                        "web": {
                            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                            "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                            "token_uri": "https://oauth2.googleapis.com/token",
                            "redirect_uris": ["http://localhost:8501"],
                        }
                    },
                    scopes=["https://www.googleapis.com/auth/analytics.readonly"],
                    redirect_uri="http://localhost:8501"
                )

            flow = st.session_state["flow"]

            # Step 1: Authorization URL
            if "oauth_state" not in st.session_state:
                auth_url, state = flow.authorization_url(
                    prompt='consent',
                    access_type='offline',
                    include_granted_scopes='true'
                )
                st.session_state["oauth_state"] = state
                st.markdown(f"[**Authorize Google Analytics Access**]({auth_url})", unsafe_allow_html=True)

            # Step 2: Handle Redirect Back with Code
            query_params = st.query_params
            if "code" in query_params and "state" in query_params:
                if query_params["state"] != st.session_state.get("oauth_state"):
                    st.error("❌ State mismatch. Please retry authentication.")
                else:
                    full_url = f"http://localhost:8501/?{urlencode(query_params)}"
                    flow.fetch_token(authorization_response=full_url)
                    st.session_state["credentials"] = flow.credentials
                    st.success("✅ Google Analytics access granted!")

        else:
            st.success("✅ Already connected to Google Analytics!")

        # GA4 Property selection section (just a placeholder)
        st.subheader("🎯 Select Your GA4 Property")


        # Step 2: List Properties
        if 'credentials' in st.session_state:
            properties = get_user_properties(st.session_state['credentials'])
            # ...existing code...
            if properties:
                options = {f"{p['display_name']} ({p['property_id']})": p['property_id'] for p in properties}
                selected = st.selectbox("Choose a GA4 Property", options.keys())
                property_id = options[selected]

                # Step 3: Fetch and Display Report
                from google.analytics.data_v1beta import BetaAnalyticsDataClient
                from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest

                client = BetaAnalyticsDataClient(credentials=st.session_state['credentials'])

                request = RunReportRequest(
                    property=f"properties/{property_id}",
                    dimensions=[
                        Dimension(name="sessionSource"),
                        Dimension(name="sessionCampaignId")
                    ],
                    metrics=[
                        Metric(name="sessions"),
                        Metric(name="totalUsers")
                    ],
                    date_ranges=[DateRange(start_date="30daysAgo", end_date="today")],
                )

                response = client.run_report(request)

                # Format the response into a DataFrame for display
                rows = []
                for row in response.rows:
                    rows.append({
                        "Session Source": row.dimension_values[0].value,
                        "Campaign": row.dimension_values[1].value,
                        "Sessions": row.metric_values[0].value,
                        "Users": row.metric_values[1].value
                    })

                st.write("📊 GA4 Traffic Metrics")
                st.dataframe(rows)
        # else:
        #     st.warning("Google Analytics is not connected. Please authorize first.")    

        else:
            st.warning("No GA4 properties found for this account.")

    elif option == "Twitter/X (Mock)":
        st.header("🐦 Twitter/X Data (Mock)")
        try:
            with open("ui/mock_twitter_data.json", "r") as f:
                twitter_data = json.load(f)

            # Compute summary KPIs
            df = pd.DataFrame(twitter_data)
            df["date"] = pd.to_datetime(df["date"])
            total_impressions = df["impressions"].sum()
            total_engagements = df["engagements"].sum()
            avg_engagement_rate = round((df["engagements"] / df["impressions"]).mean() * 100, 2)

            # Show KPI Cards
            col1, col2, col3 = st.columns(3)
            col1.metric("👁️ Impressions", f"{total_impressions:,}")
            col2.metric("💬 Engagements", f"{total_engagements:,}")
            col3.metric("📊 Engagement Rate", f"{avg_engagement_rate}%")

            # Show Timeline Chart
            st.subheader("📅 Daily Twitter Post Performance")
            fig = px.line(
                df,
                x="date",
                y=["impressions", "engagements"],
                labels={"value": "Metric Value", "date": "Date", "variable": "Metric"},
                title="Twitter Engagement Over Time"
            )
            st.plotly_chart(fig, use_container_width=True)

            # Optional: Show top tweets
            st.subheader("🧵 Top Tweets by Engagement")
            top_tweets = df.sort_values(by="engagements", ascending=False).head(5)
            for _, row in top_tweets.iterrows():
                st.markdown(f"**{row['date'].date()}** — {row['text']}")
                st.caption(f"👁️ {row['impressions']} | 💬 {row['engagements']} | ❤️ {row['likes']} | 🔁 {row['retweets']} | 💬 {row['replies']}")

        except Exception as e:
            st.error(f"Error loading mock Twitter data: {e}")


    elif option == "Facebook/Meta (Mock)":
        st.header("Facebook/Meta Data (Mock)")
        try:
            with open("ui/mock_kpis.json", "r") as f:
                mock_data = json.load(f)

            # Show KPI Cards
            col1, col2, col3 = st.columns(3)
            col1.metric("📈 Impressions", f"{mock_data['summary']['impressions']:,}")
            col2.metric("🔗 CTR", f"{mock_data['summary']['click_through_rate']}%")
            col3.metric("💰 CPA", f"${mock_data['summary']['cost_per_acquisition']:.2f}")

            # Show Timeline Chart
            st.subheader("📅 Daily Ad Performance")

            df = pd.DataFrame(mock_data["daily"])
            df["date"] = pd.to_datetime(df["date"])

            fig = px.line(df, x="date", y=["impressions", "ctr", "cpa"],
                        labels={"value": "Metric Value", "date": "Date", "variable": "Metric"},
                        title="Daily Ad Metrics Over Time")
            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"Error loading mock data: {e}")
