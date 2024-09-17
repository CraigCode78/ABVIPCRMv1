# data.py

import pandas as pd

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