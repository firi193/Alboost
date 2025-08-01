import streamlit as st

def apply_custom_styles():
    """
    Apply custom CSS styles for a professional, modern look.
    """
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .main {
        font-family: 'Inter', sans-serif;
        background-color: #F8F9FA;
    }
    
    /* Custom CSS Variables */
    :root {
        --primary-color: #1A1A40;
        --secondary-color: #FF5C8D;
        --background-color: #F5F5F7;
        --card-background: #FFFFFF;
        --text-primary: #1A1A40;
        --text-secondary: #6C757D;
        --border-color: #E9ECEF;
        --shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        --border-radius: 12px;
    }
    
    /* Typography */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 1rem;
    }
    
    h1 {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    h2 {
        font-size: 1.75rem;
        font-weight: 600;
    }
    
    h3 {
        font-size: 1.25rem;
        font-weight: 500;
    }
    
    /* Sidebar Styling */
    .css-1d391kg {
        background-color: var(--card-background);
        border-right: 1px solid var(--border-color);
    }
    
    .css-1d391kg .sidebar-content {
        padding: 2rem 1rem;
    }
    
    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-color), #2A2A5A);
        color: white;
        border: none;
        border-radius: var(--border-radius);
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        font-family: 'Inter', sans-serif;
        transition: all 0.3s ease;
        box-shadow: var(--shadow);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #2A2A5A, var(--secondary-color));
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    /* Secondary Button */
    .secondary-button {
        background: var(--card-background) !important;
        color: var(--text-primary) !important;
        border: 2px solid var(--border-color) !important;
    }
    
    .secondary-button:hover {
        background: var(--background-color) !important;
        border-color: var(--secondary-color) !important;
    }
    
    /* Selectbox Styling */
    .stSelectbox > div > div {
        border-radius: var(--border-radius);
        border: 2px solid var(--border-color);
        background-color: var(--card-background);
    }
    
    .stSelectbox > div > div:hover {
        border-color: var(--secondary-color);
    }
    
    /* Date Input Styling */
    .stDateInput > div > div {
        border-radius: var(--border-radius);
        border: 2px solid var(--border-color);
        background-color: var(--card-background);
    }
    
    /* Metric Cards */
    .metric-container {
        background: var(--card-background);
        border-radius: var(--border-radius);
        padding: 1.5rem;
        box-shadow: var(--shadow);
        border: 1px solid var(--border-color);
        margin-bottom: 1rem;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--primary-color);
    }
    
    .metric-label {
        font-size: 0.875rem;
        color: var(--text-secondary);
        font-weight: 500;
    }
    
    /* Card Styling */
    .custom-card {
        background: var(--card-background);
        border-radius: var(--border-radius);
        padding: 1.5rem;
        box-shadow: var(--shadow);
        border: 1px solid var(--border-color);
        margin-bottom: 1rem;
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background-color: var(--background-color);
        border-radius: var(--border-radius);
        padding: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: var(--text-secondary);
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--primary-color);
        color: white;
    }
    
    /* Form Styling */
    .stTextInput > div > div > input {
        border-radius: var(--border-radius);
        border: 2px solid var(--border-color);
        background-color: var(--card-background);
    }
    
    .stTextArea > div > div > textarea {
        border-radius: var(--border-radius);
        border: 2px solid var(--border-color);
        background-color: var(--card-background);
    }
    
    /* Success/Error Messages */
    .stAlert {
        border-radius: var(--border-radius);
        border: none;
    }
    
    /* Dataframe Styling */
    .stDataFrame {
        border-radius: var(--border-radius);
        overflow: hidden;
    }
    
    /* Expander Styling */
    .streamlit-expanderHeader {
        background-color: var(--card-background);
        border-radius: var(--border-radius);
        border: 1px solid var(--border-color);
        font-weight: 500;
    }
    
    /* Progress Bar */
    .stProgress > div > div > div > div {
        background-color: var(--secondary-color);
    }
    
    /* Remove Streamlit Default Styling */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Custom Spacing */
    .section-spacing {
        margin: 2rem 0;
    }
    
    .card-spacing {
        margin: 1rem 0;
    }
    
    </style>
    """, unsafe_allow_html=True) 