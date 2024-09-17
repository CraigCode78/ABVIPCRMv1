import os
import openai
from openai import OpenAI
import streamlit as st
import pandas as pd
import random
import time
import re
from string import Template
from data import load_vip_data, generate_upcoming_events

def get_openai_key():
    # First, try to get the key from environment variables
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        try:
            api_key = st.secrets["OPENAI_API_KEY"]
        except (AttributeError, KeyError):
            st.error("OpenAI API key not found. Please set it in Streamlit secrets or environment variables.")
            st.stop()
    return api_key

# Initialize the OpenAI client
client = OpenAI(api_key=get_openai_key())
DEFAULT_MODEL = 'gpt-4o'  # Change to 'gpt-3.5-turbo' if needed

def generate_openai_response(prompt, max_tokens=250, temperature=0.7, retries=3):
    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model=DEFAULT_MODEL,
                messages=[{'role': 'user', 'content': prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                n=1
            )
            # Validate response structure
            if hasattr(response, 'choices') and len(response.choices) > 0:
                return response.choices[0].message.content.strip()
            else:
                st.error(f"Unexpected API response structure: {response}")
                return ""
        except Exception as e:
            st.error(f"Error during OpenAI API call: {str(e)}")
            if attempt < retries - 1:
                st.warning(f"Retrying... (Attempt {attempt + 2} of {retries})")
            else:
                return ""

INSIGHTS_PROMPT_TEMPLATE = Template("""
Analyze the following VIP client's data and provide insights:

Name: $name
Purchase History: $purchase_history
Interaction History: $interaction_history
Preferred Contact Times: $preferred_contact_times
Last Contact Date: $last_contact_date
Sentiment Score: $sentiment_score

Provide suggestions on how to best engage with this client.
""")

MESSAGE_PROMPT_TEMPLATE = Template("""
Compose a personalized invitation email to $name for the upcoming Art Basel event.
Mention their interest in $purchase_history and reference their previous interaction: $interaction_history.
Suggest scheduling a meeting during their preferred contact time: $preferred_contact_times.
""")

SENTIMENT_PROMPT_TEMPLATE = Template("""
Analyze the sentiment of the following interaction history and provide a score between -1 (very negative) and 1 (very positive):

$interaction_history

Please respond with only a number between -1 and 1, representing the sentiment score.
""")

def generate_vip_insights(vip_info):
    prompt = INSIGHTS_PROMPT_TEMPLATE.substitute(
        name=vip_info['Name'],
        purchase_history=vip_info['Purchase_History'],
        interaction_history=vip_info['Interaction_History'],
        preferred_contact_times=vip_info['Preferred_Contact_Times'],
        last_contact_date=vip_info['Last_Contact_Date'],
        sentiment_score=vip_info['Sentiment_Score']
    )
    return generate_openai_response(prompt)

def generate_personalized_message(vip_info):
    prompt = MESSAGE_PROMPT_TEMPLATE.substitute(
        name=vip_info['Name'],
        purchase_history=vip_info['Purchase_History'],
        interaction_history=vip_info['Interaction_History'],
        preferred_contact_times=vip_info['Preferred_Contact_Times']
    )
    return generate_openai_response(prompt)

def analyze_sentiment(vip_info):
    prompt = SENTIMENT_PROMPT_TEMPLATE.substitute(
        interaction_history=vip_info['Interaction_History']
    )
    sentiment_response = generate_openai_response(prompt, max_tokens=100, temperature=0)
    
    # Try to extract a numerical value from the response
    numerical_match = re.search(r'(-?\d+(\.\d+)?)', sentiment_response)
    if numerical_match:
        try:
            sentiment_score = float(numerical_match.group(1))
            if -1 <= sentiment_score <= 1:
                return sentiment_score
            else:
                st.warning(f"Extracted sentiment score {sentiment_score} is out of expected range [-1, 1].")
        except ValueError:
            pass
    
    # If no valid numerical value found, estimate based on the text
    lower_response = sentiment_response.lower()
    if 'positive' in lower_response:
        return 0.5
    elif 'negative' in lower_response:
        return -0.5
    elif 'neutral' in lower_response:
        return 0
    else:
        st.warning(f"Unable to determine sentiment score from response: '{sentiment_response}'")
        return 0  # Default to neutral

def get_engagement_score():
    # Simulated engagement score between 50 and 100
    return random.randint(50, 100)

# New functions
def generate_engagement_suggestions(vip_info):
    prompt = f"Based on the VIP's interests in {vip_info['Purchase_History']} and past interaction of {vip_info['Interaction_History']}, suggest 3 personalized ways to engage with them."
    return generate_openai_response(prompt)

def recommend_events(vip_info, upcoming_events):
    events_str = ", ".join([f"{e['name']} on {e['date']}" for e in upcoming_events])
    prompt = f"Given the VIP's interest in {vip_info['Purchase_History']}, which of these upcoming events would they likely be interested in: {events_str}? Explain why for the top 2 recommendations."
    return generate_openai_response(prompt)

def generate_conversation_starters(vip_info):
    prompt = f"Create 3 engaging conversation starters for a VIP interested in {vip_info['Purchase_History']} with a recent interaction of {vip_info['Interaction_History']}."
    return generate_openai_response(prompt)

def generate_vip_summary(vip_info):
    prompt = f"Create a concise 3-4 sentence summary of the VIP based on this information: {vip_info}. Highlight key interests and important points for engagement."
    return generate_openai_response(prompt)

def plan_follow_up_actions(vip_info, interaction_notes):
    prompt = f"Based on the VIP's profile ({vip_info}) and recent interaction notes ({interaction_notes}), suggest 3 follow-up actions for the next 2 weeks."
    return generate_openai_response(prompt)

def curate_personalized_content(vip_info):
    prompt = f"Suggest 5 recent articles, videos, or artworks that would interest a VIP with these interests: {vip_info['Purchase_History']}."
    return generate_openai_response(prompt)

# Main app
def main():
    st.title("Art Basel AI-Driven CRM Prototype")
    
    # Debug information
    st.sidebar.write("Debug Information:")
    api_key = get_openai_key()
    st.sidebar.write(f"API Key (first 5 chars): {api_key[:5]}...")
    
    # Test API connection
    try:
        test_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello, World!"}],
            max_tokens=5
        )
        st.sidebar.success("API connection test successful!")
    except Exception as e:
        st.sidebar.error(f"API connection test failed: {str(e)}")

    # Load VIP Data
    vip_data = load_vip_data()
    upcoming_events = generate_upcoming_events()

    # Sidebar for VIP Selection
    selected_vip = st.sidebar.selectbox("Select VIP Client", vip_data['Name'].tolist())

    # Retrieve VIP Information
    vip_info = vip_data[vip_data['Name'] == selected_vip].iloc[0].to_dict()

    # Display VIP Profile
    st.header(f"Profile: {vip_info['Name']}")
    st.write(f"**Purchase History:** {vip_info['Purchase_History']}")
    st.write(f"**Interaction History:** {vip_info['Interaction_History']}")
    st.write(f"**Preferred Contact Times:** {vip_info['Preferred_Contact_Times']}")
    st.write(f"**Last Contact Date:** {vip_info['Last_Contact_Date']}")
    st.write(f"**Sentiment Score:** {vip_info['Sentiment_Score']}")

    # Predictive Engagement Score
    engagement_score = get_engagement_score()
    st.subheader("Predictive Engagement Score")
    st.progress(engagement_score)
    st.write(f"Engagement Likelihood: {engagement_score}%")

    # Generate AI Insights
    if st.button("Generate AI Insights"):
        with st.spinner("Generating insights..."):
            insights = generate_vip_insights(vip_info)
        if insights:
            st.subheader("AI-Generated Insights")
            st.write(insights)

    # Generate Personalized Message
    if st.button("Generate Personalized Message"):
        with st.spinner("Generating message..."):
            message = generate_personalized_message(vip_info)
        if message:
            st.subheader("Personalized Message")
            st.write(message)

    # Analyze Sentiment
    if st.button("Analyze Sentiment"):
        with st.spinner("Analyzing sentiment..."):
            sentiment = analyze_sentiment(vip_info)
        if sentiment is not None:
            st.subheader("Sentiment Analysis")
            st.write(f"Sentiment Score: {sentiment:.2f}")
        else:
            st.error("Unable to determine sentiment score.")

    # VIP Summary
    if st.button("Generate VIP Summary"):
        with st.spinner("Generating VIP summary..."):
            summary = generate_vip_summary(vip_info)
        st.subheader("VIP Summary")
        st.write(summary)

    # Engagement Suggestions
    if st.button("Generate Engagement Suggestions"):
        with st.spinner("Generating engagement suggestions..."):
            suggestions = generate_engagement_suggestions(vip_info)
        st.subheader("Engagement Suggestions")
        st.write(suggestions)

    # Event Recommendations
    if st.button("Recommend Events"):
        with st.spinner("Generating event recommendations..."):
            recommendations = recommend_events(vip_info, upcoming_events)
        st.subheader("Event Recommendations")
        st.write(recommendations)

    # Conversation Starters
    if st.button("Generate Conversation Starters"):
        with st.spinner("Generating conversation starters..."):
            starters = generate_conversation_starters(vip_info)
        st.subheader("Conversation Starters")
        st.write(starters)

    # Follow-up Action Planner
    interaction_notes = st.text_area("Enter recent interaction notes:")
    if st.button("Plan Follow-up Actions"):
        with st.spinner("Planning follow-up actions..."):
            actions = plan_follow_up_actions(vip_info, interaction_notes)
        st.subheader("Follow-up Action Plan")
        st.write(actions)

    # Personalized Content Curator
    if st.button("Curate Personalized Content"):
        with st.spinner("Curating personalized content..."):
            content = curate_personalized_content(vip_info)
        st.subheader("Personalized Content Recommendations")
        st.write(content)

if __name__ == "__main__":
    main()
