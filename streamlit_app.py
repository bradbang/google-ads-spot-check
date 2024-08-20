import streamlit as st
import pandas as pd
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
st.set_page_config(layout="wide")

# Set the title of the app
st.title('Google Ads Campaign Summary + Spot Check')
st.write("Upload your Google Ads campaign data and we will analyse for issues.")
st.write("Generate the CSV by going to Google Ads > Campaigns > Ads > *Filter by active* > Downloads > Download as CSV")

# Upload the CSV file
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

# Initialize OpenAI API

def analyze_data_with_chatgpt(data):
    # Convert DataFrame to a string or JSON format
    data_str = data.to_json()

    # Create a message list for ChatGPT
    messages = [
        {"role": "system", "content": "You are a data analyst specializing in Google Ads campaigns."},
        {"role": "user", "content": f"Take the following Google Ads campaign export and analyse the data to identify spelling errors (we should use Australian english), incorrect data or messaging conflicts/mis-matches. Note that it is expected that the 'campaign' and 'ad group' be repeated as these indicate grouping - and this is not an error. Headlines = Title Case, Descriptions = Sentence case. If you flag a spelling mistake then realise it's not a spelling mistake don't output anything. note that headlines have a limit of 30 characters, so sometimes we use abbreviations to come in under the limit. Ignore use of & instead of 'and'. Ignore 'Text not available' errors or empty cells. Output issues in a table format indicate which CSV row and column name the error is on, what the issue is and what needs to be fixed:\n\n{data_str}"}
    ]

    # Call OpenAI API
    response = client.chat.completions.create(model="gpt-4o",  # Use "gpt-4" if you have access
    messages=messages,
    max_tokens=1000)

    # Extract the response content
    return response.choices[0].message.content.strip()

if uploaded_file is not None:
    # Read the uploaded CSV file, specifying that the header is on the third row
    df = pd.read_csv(uploaded_file, header=2)

    # Define the required columns, excluding "Headline X position" columns
    required_columns = ['Campaign', 'Ad group', 'Final URL']

    # Optional columns
    optional_columns = [
        'Long headline','Headline 1', 'Headline 2', 'Headline 3', 'Headline 4', 
        'Headline 5', 'Headline 6', 'Headline 7', 'Headline 8', 
        'Headline 9', 'Headline 10', 'Headline 11', 'Headline 12', 
        'Headline 13', 'Headline 14', 'Headline 15', 'Description', 
        'Description 1', 'Description 2', 'Description 3', 
        'Description 4', 'Description 5'
    ]

    # Check if the required columns are in the uploaded file
    if set(required_columns).issubset(df.columns):
        # Filter out rows where 'Campaign' is empty or '--'
        df = df.dropna(subset=['Campaign'])
        df = df[df['Campaign'] != '--']

        # Include optional columns if they exist
        available_optional_columns = [col for col in optional_columns if col in df.columns]
        all_columns = required_columns + available_optional_columns

        # Extract and display the required and available optional columns
        summary_df = df[all_columns]
        st.write("Campaign Summary:")
        st.write(summary_df)

        # Analyze data with ChatGPT
        analysis = analyze_data_with_chatgpt(summary_df)
        st.write("# Bradgic analysis:")
        st.write(analysis)
    else:
        missing_columns = set(required_columns) - set(df.columns)
        st.error(f"The file is missing the columns, please make sure you are exporting from the Google Ads interface: {', '.join(missing_columns)}")