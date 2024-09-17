import os
import openai
from openai import OpenAI
import streamlit as st
import pandas as pd
import random
import time
from string import Template

# Set the OpenAI API key
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
            error_message = str(e).lower()
            if "rate limit" in error_message or "quota" in error_message:
                if attempt < retries - 1:
                    wait_time = 2 ** attempt
                    st.warning(f"Rate limit exceeded. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                else:
                    st.error("Rate limit exceeded. Please try again later.")
                    return ""
            else:
                st.error(f"Error during OpenAI API call: {e}")
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
Analyze the sentiment of the following interaction history and provide a score between -1 (negative) and 1 (positive):

$interaction_history
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
    sentiment = generate_openai_response(prompt, max_tokens=60, temperature=0)
    # Validate and convert sentiment to float
    try:
        sentiment_score = float(sentiment)
        if -1 <= sentiment_score <= 1:
            return sentiment_score
        else:
            st.warning(f"Sentiment score {sentiment_score} is out of expected range [-1, 1].")
            return None
    except ValueError:
        st.warning(f"Invalid sentiment score received: '{sentiment}'. Expected a number between -1 and 1.")
        return None

def load_vip_data():
    # Expanded VIP data
    data = {
        'VIP_ID': list(range(1, 11)),
        'Name': [
            'Alice Smith', 'Bob Johnson', 'Carol Williams', 'David Brown', 'Eva Davis',
            'Frank Miller', 'Grace Wilson', 'Henry Moore', 'Isabella Taylor', 'Jack Anderson'
        ],
        'Purchase_History': [
            'Contemporary Art, Sculptures',
            'Modern Art, Installations',
            'Abstract Paintings, Digital Art',
            'Impressionist Paintings, Photography',
            'Sculptures, Mixed Media',
            'Street Art, Graffiti Art',
            'Classical Paintings, Antique Artifacts',
            'Pop Art, Limited Edition Prints',
            'Kinetic Art, Interactive Installations',
            'Video Art, Virtual Reality Art'
        ],
        'Interaction_History': [
            'Attended Art Basel Miami 2022',
            'VIP Lounge Visit in Basel 2021',
            'Missed last event due to scheduling',
            'Regular attendee since 2015',
            'Hosted private gallery tour in 2019',
            'Attended online exhibitions during 2020',
            'Special guest at Art Basel Hong Kong 2018',
            "Participated in collector's panel discussion",
            'Sponsored young artists program in 2021',
            'Expressed interest in emerging digital art'
        ],
        'Preferred_Contact_Times': [
            'Weekdays, Afternoon',
            'Weekends, Morning',
            'Weekdays, Evening',
            'Weekends, Afternoon',
            'Weekdays, Morning',
            'Weekends, Evening',
            'Weekdays, Afternoon',
            'Weekdays, Morning',
            'Weekends, Afternoon',
            'Weekdays, Evening'
        ],
        'Last_Contact_Date': [
            '2023-09-15',
            '2023-09-10',
            '2023-09-05',
            '2023-09-01',
            '2023-08-28',
            '2023-08-25',
            '2023-08-20',
            '2023-08-15',
            '2023-08-10',
            '2023-08-05'
        ],
        'Sentiment_Score': [
            0.8, 0.6, 0.4, 0.9, 0.7, 0.5, 0.85, 0.65, 0.75, 0.95
        ]
    }
    df = pd.DataFrame(data)
    return df

def get_engagement_score():
    # Simulated engagement score between 50 and 100
    return random.randint(50, 100)

def main():
    st.title("Art Basel AI-Driven CRM Prototype")

    # Load VIP Data
    vip_data = load_vip_data()

    # Sidebar for VIP Selection
    vip_names = vip_data['Name'].tolist()
    selected_vip = st.sidebar.selectbox("Select VIP Client", vip_names)

    # Retrieve VIP Information
    vip_info = vip_data[vip_data['Name'] == selected_vip].iloc[0]

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

if __name__ == "__main__":
    main()
