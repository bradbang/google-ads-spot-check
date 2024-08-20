import streamlit as st
import pandas as pd
import openai

# Set the title of the app
st.title('Google Ads Campaign Summary')

# Upload the CSV file
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

# Initialize OpenAI API
openai.api_key = st.secrets["OPENAI_API_KEY"]

def analyze_data_with_chatgpt(data):
    # Convert DataFrame to a string or JSON format
    data_str = data.to_json()

    # Create a message list for ChatGPT
    messages = [
        {"role": "system", "content": "You are a data analyst specializing in Google Ads campaigns."},
        {"role": "user", "content": f"Analyze the following Google Ads campaign data and identify any errors or areas for improvement:\n\n{data_str}"}
    ]

    # Call OpenAI API
    response = openai.ChatCompletion.create(
        model="gpt-4",  # You can use "gpt-3.5-turbo" if you don't have access to GPT-4
        messages=messages,
        max_tokens=150
    )

    # Extract the response content
    return response['choices'][0]['message']['content'].strip()

if uploaded_file is not None:
    # Read the uploaded CSV file
    df = pd.read_csv(uploaded_file)

    # Define the required columns
    required_columns = [
        'Campaign', 'Headline 1', 'Headline 2', 'Headline 3', 'Headline 4', 
        'Headline 5', 'Headline 6', 'Headline 7', 'Headline 8', 'Headline 9', 
        'Headline 10', 'Headline 11', 'Headline 12', 'Headline 13', 'Headline 14', 
        'Headline 15', 'Long headline 1', 'Long headline 2', 'Long headline 3', 
        'Long headline 4', 'Long headline 5', 'Description 1', 'Description 2', 
        'Description 3', 'Description 4', 'Description 5', 'Call to action', 
        'Final URL'
    ]

    # Check if the required columns are in the uploaded file
    if set(required_columns).issubset(df.columns):
        # Extract and display the required columns
        summary_df = df[required_columns]
        st.write("Campaign Summary:")
        st.write(summary_df)

        # Analyze data with ChatGPT
        analysis = analyze_data_with_chatgpt(summary_df)
        st.write("ChatGPT Analysis:")
        st.write(analysis)
    else:
        missing_columns = set(required_columns) - set(df.columns)
        st.error(f"The uploaded file is missing the following required columns: {', '.join(missing_columns)}")