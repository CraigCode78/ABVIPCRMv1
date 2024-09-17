# app.py

import os
from dotenv import load_dotenv
import openai
import streamlit as st
import pandas as pd
import random

# Load environment variables from .env file
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

def load_vip_data():
    # Expanded VIP data
    data = {
        'VIP_ID': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
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
            'Participated in collector\'s panel discussion',
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

def generate_vip_insights(vip_info):
    prompt = f"""
    Analyze the following VIP client's data and provide insights:

    Name: {vip_info['Name']}
    Purchase History: {vip_info['Purchase_History']}
    Interaction History: {vip_info['Interaction_History']}
    Preferred Contact Times: {vip_info['Preferred_Contact_Times']}
    Last Contact Date: {vip_info['Last_Contact_Date']}
    Sentiment Score: {vip_info['Sentiment_Score']}

    Provide suggestions on how to best engage with this client.
    """
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=250,
        temperature=0.7,
        n=1,
        stop=None
    )
    insights = response.choices[0].text.strip()
    return insights

def generate_personalized_message(vip_info):
    prompt = f"""
    Compose a personalized invitation email to {vip_info['Name']} for the upcoming Art Basel event.
    Mention their interest in {vip_info['Purchase_History']} and reference their previous interaction: {vip_info['Interaction_History']}.
    Suggest scheduling a meeting during their preferred contact time: {vip_info['Preferred_Contact_Times']}.
    """
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=250,
        temperature=0.7,
        n=1,
        stop=None
    )
    message = response.choices[0].text.strip()
    return message

def get_engagement_score():
    # Simulated engagement score between 50 and 100
    return random.randint(50, 100)

def analyze_sentiment(vip_info):
    # Use the Sentiment_Score from the data
    sentiment_score = vip_info['Sentiment_Score']
    return sentiment_score

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
        st.subheader("AI-Generated Insights")
        st.write(insights)

    # Generate Personalized Message
    if st.button("Generate Personalized Message"):
        with st.spinner("Generating message..."):
            message = generate_personalized_message(vip_info)
        st.subheader("Personalized Message")
        st.write(message)

    # Analyze Sentiment
    if st.button("Show Sentiment Score"):
        sentiment_score = analyze_sentiment(vip_info)
        st.subheader("Sentiment Analysis")
        st.write(f"Sentiment Score: {sentiment_score}")

if __name__ == "__main__":
    main()