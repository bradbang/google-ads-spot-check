import streamlit as st
import pandas as pd
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Set the title of the app
st.title('Google Ads Campaign Summary + Spot Check')
st.write("Upload your Google Ads campaign data and we will analyse for issues.")
st.write("*Search Ads Data:* Google Ads > Campaigns > Ads > Downloads > Download as CSV")
st.write("*Assets:* Generate the CSV by going to Google Ads > Assets > Download as CSV")

# Upload the CSV file
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

# Initialize OpenAI API
def analyze_data_with_chatgpt(data, extra_info):
    # Convert DataFrame to a string or JSON format
    data_str = data.to_json()

    # Create a message list for ChatGPT
    messages = [
        {"role": "system", "content": "You are a data analyst specializing in Google Ads campaigns."},
        {"role": "user", "content": f"Take the following Google Ads campaign export and analyse the data to identify spelling errors (we should use Australian english), incorrect data or messaging conflicts/mis-matches. Note that it is expected that the 'campaign' and 'ad group' be repeated as these indicate grouping - and this is not an error. Headlines = Title Case, Descriptions = Sentence case. If you flag a spelling mistake then realise it's not a spelling mistake don't output anything. note that headlines have a limit of 30 characters, so sometimes we use abbreviations to come in under the limit. Output issues in a table format indicate which CSV row and column name the error is on, what the issue is and what needs to be fixed:\n\n{data_str}\n\nAdditional Information: {extra_info}"}
    ]

    # Call OpenAI API
    response = client.chat.completions.create(model="gpt-4o-mini",  # Use "gpt-4" if you have access
    messages=messages,
    max_tokens=1000)

    # Extract the response content
    return response.choices[0].message.content.strip()

if uploaded_file is not None:
    # Read the uploaded CSV file, specifying that the header is on the third row
    df = pd.read_csv(uploaded_file, header=2)

    # Skip rows with a blank first column
    first_column_name = df.columns[0]
    df = df.dropna(subset=[first_column_name])

    # Define the columns to display if they exist
    columns_to_display = [
        'Campaign', 'Ad group', 'Final URL', 'Long headline',
        'Headline 1', 'Headline 1 position', 'Headline 2', 'Headline 2 position',
        'Headline 3', 'Headline 3 position', 'Headline 4', 'Headline 4 position',
        'Headline 5', 'Headline 5 position', 'Headline 6', 'Headline 6 position',
        'Headline 7', 'Headline 7 position', 'Headline 8', 'Headline 8 position',
        'Headline 9', 'Headline 9 position', 'Headline 10', 'Headline 10 position',
        'Headline 11', 'Headline 11 position', 'Headline 12', 'Headline 12 position',
        'Headline 13', 'Headline 13 position', 'Headline 14', 'Headline 14 position',
        'Headline 15', 'Headline 15 position', 'Description', 'Description position',
        'Description 1', 'Description 1 position', 'Description 2', 'Description 2 position',
        'Description 3', 'Description 3 position', 'Description 4', 'Description 4 position',
        'Description 5', 'Description 5 position', 'Asset type', 'Asset', 'Level'
    ]

    # Filter the DataFrame to include only the columns that exist in the uploaded file
    available_columns = [col for col in columns_to_display if col in df.columns]
    summary_df = df.loc[:, available_columns].copy()

    # Display the data in a table without images
    st.markdown("## Summary")
    st.write("Here is a summary of the uploaded dataset.")
    st.write(summary_df)

    # Add a text input for additional information
    extra_info = st.text_input("Is there anything else you would like to add to the analysis prompt?")

    # Phase 2: Button to run analysis
    if st.button(":male-detective: Analyse this dataset"):
        with st.spinner("Analyzing the dataset..."):
            # Analyze data with ChatGPT
            analysis = analyze_data_with_chatgpt(summary_df, extra_info)
            st.markdown("### :brain: Bradgic analysis")
            st.write(analysis)