import streamlit as st
import src.ui as ui

# Page Config
st.set_page_config(
    page_title="Jadwal Toga Mawar",
    page_icon="🌺",
    layout="wide",
    initial_sidebar_state="collapsed" # Mobile friendly, hide sidebar by default
)

# Custom CSS for Mobile Optimization and Styling
st.markdown("""
<style>
    .stButton button {
        background-color: #FF4B4B;
        color: white;
        font-weight: bold;
        border-radius: 10px;
        padding: 0.5rem 1rem;
    }
    .stButton button:hover {
        background-color: #D93A3A;
        color: white;
    }
    h1, h2, h3 {
        color: #2C3E50;
    }
    /* Increase touch targets for mobile */
    .stCheckbox {
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)

def main():
    ui.render_header()
    
    # Navigation via Tabs or Sidebar
    # Using Tabs for simplicity on Mobile
    tab_input, tab_dashboard = st.tabs(["📝 Catat Piket", "📊 Laporan"])
    
    with tab_input:
        ui.render_input_form()
    
    with tab_dashboard:
        ui.render_dashboard()

if __name__ == "__main__":
    main()
