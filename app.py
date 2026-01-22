import streamlit as st
import pandas as pd
import numpy as np
import pickle

# --- ASSETS LOADING ---
# Ensure these files are in C:\DMUSL\Hackathon\
df = pd.read_csv("Hackathon_Processed.csv")
cluster_map = {"Conservative": 2, "Moderate": 0, "Aggressive": 1}

st.set_page_config(page_title="Portfolio Advisor Pro", layout="wide")

# --- MAIN NAVIGATION (VISIBLE TABS) ---
st.title("🛡️ Personalized Portfolio Advisory System")
tab1, tab2 = st.tabs(["📋 Step 1: Risk Advisory", "💰 Step 2: Investment Calculator"])

# ---------------------------------------------------------
# TAB 1: RISK ADVISORY
# ---------------------------------------------------------
with tab1:
    st.header("Determine Your Risk Profile")

    # Sidebar remains for profile data
    st.sidebar.header("User Profile Data")
    age = st.sidebar.slider("Age", 18, 90, 30)
    horizon = st.sidebar.selectbox("Investment Horizon", ["Short Term (<3y)", "Medium Term (3-7y)", "Long Term (7y+)"])

    # Business Logic for Recommendation
    if age < 35 or horizon == "Long Term (7y+)":
        rec_label, rec_cluster = "Aggressive", 1
    elif age > 60 or horizon == "Short Term (<3y)":
        rec_label, rec_cluster = "Conservative", 2
    else:
        rec_label, rec_cluster = "Moderate", 0

    st.info(f"💡 AI Suggestion: **{rec_label}** strategy.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button(f"✅ Use AI Recommendation ({rec_label})"):
            st.session_state.final_choice = rec_label
            st.success(f"Profile locked as: {rec_label}")

    with col2:
        manual_choice = st.selectbox("Or Choose Manually:", ["Conservative", "Moderate", "Aggressive"])
        if st.button("Apply Manual Choice"):
            st.session_state.final_choice = manual_choice
            st.success(f"Profile locked as: {manual_choice}")

    if 'final_choice' in st.session_state:
        st.divider()
        st.subheader(f"Portfolio Preview: {st.session_state.final_choice}")
        portfolio_view = df[df['Cluster'] == cluster_map[st.session_state.final_choice]]
        st.dataframe(portfolio_view[['Symbol', 'Shortname', 'Sector', 'Weight']].head(10), use_container_width=True)

# ---------------------------------------------------------
# TAB 2: INVESTMENT CALCULATOR
# ---------------------------------------------------------
with tab2:
    st.header("Investment Distribution")

    if 'final_choice' not in st.session_state:
        st.warning("⚠️ Please complete 'Step 1: Risk Advisory' first to select a profile!")
    else:
        st.write(f"Calculating for: **{st.session_state.final_choice} Profile**")

        # User inputs investment amount
        total_investment = st.number_input("Enter Total Investment Amount ($)", min_value=100, value=2000, step=100)

        # Calculation Logic
        selected_cluster = cluster_map[st.session_state.final_choice]
        portfolio = df[df['Cluster'] == selected_cluster].copy()

        # Normalize weights so they sum to 100% of the user's input
        portfolio['Normalized_Weight'] = portfolio['Weight'] / portfolio['Weight'].sum()
        portfolio['Invest_Amount'] = portfolio['Normalized_Weight'] * total_investment

        calc_df = portfolio[portfolio['Invest_Amount'] > 0.5].sort_values(by='Invest_Amount', ascending=False)

        st.subheader(f"How to invest your ${total_investment:,}:")

        # Display the specific examples you wanted (Apple/Microsoft style)
        top_3 = calc_df.head(3)
        st.success(
            f"Primary Move: Invest **${top_3.iloc[0]['Invest_Amount']:.2f}** in **{top_3.iloc[0]['Shortname']}**")

        # Full Table
        st.dataframe(
            calc_df[['Symbol', 'Shortname', 'Invest_Amount', 'Normalized_Weight']].style.format({
                'Invest_Amount': '${:,.2f}',
                'Normalized_Weight': '{:.2%}'
            }), use_container_width=True
        )

        # Chart
        st.bar_chart(calc_df.set_index('Shortname')['Invest_Amount'].head(15))