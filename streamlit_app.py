import streamlit as st

st.set_page_config(
    page_title="Financial Data Visualisation",
    page_icon="📊",
    layout="wide"
)

# Title and description
st.title("📊 Financial Data Visualisation Platform")
st.markdown(
    """
    **Welcome to the Financial Data Visualisation Platform!**
    
    This website is an **experimental** demonstration of how **Streamlit** can be used to create 
    interactive and insightful visualisations for **financial use cases**.
    
    ⚠️ **Disclaimer:** This platform is for **demonstration purposes only** and should **not** be used for 
    financial or investment decision-making. The data and insights provided here are illustrative 
    and may not reflect real-world accuracy.
    """
)

# Add some spacing
st.write("---")

# Call to action
st.subheader("🔍 Explore the visualisations")
st.markdown(
    """
    Navigate through the sections using the sidebar to explore various data visualisations.
    """
)

# Footer
st.write("---")
st.caption("© 2025 Financial Data Visualisation - Experimental Project by databasesystems.info")

