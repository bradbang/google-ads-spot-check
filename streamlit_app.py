import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")  # Set the page to wide mode

st.title("Google Ads Data Analyzer")
st.markdown("This sytem helps easily analyse the keywords and destination URL's for each campaign and ad-group").
st.markdown("Upload your Google Ads and keywords data to get started.")

## File Uploads

st.header("Upload CSV Files")

col1, col2, col3 = st.columns(3)

with col1:
    ad_file = st.file_uploader("Upload Google Ads 'ads' export CSV", type="csv")

with col2:
    keyword_file = st.file_uploader("Upload Google Ads 'search keyword' export CSV", type="csv")

with col3:
    negative_keyword_file = st.file_uploader("Upload Google Ads negative 'search keyword' export CSV (Optional)", type="csv")

if ad_file and keyword_file:
    ## Data Processing
    
    # Read CSVs, skipping the first two rows and dropping rows with blank second column
    ad_df = pd.read_csv(ad_file, skiprows=2)
    ad_df = ad_df.dropna(subset=[ad_df.columns[1]])
    
    keyword_df = pd.read_csv(keyword_file, skiprows=2)
    keyword_df = keyword_df.dropna(subset=[keyword_df.columns[1]])
    
    # Select required columns from ad_df
    ad_df = ad_df[['Campaign', 'Ad group', 'Ad type', 'Final URL']]
    
    # Select required columns from keyword_df
    keyword_df = keyword_df[['Campaign', 'Ad group', 'Keyword', 'Match type', 'Status']]
    
    # Merge ad_df and keyword_df
    merged_df = pd.merge(ad_df, keyword_df, on=['Campaign', 'Ad group'], how='left')
    
    # Process negative keywords if file is uploaded
    if negative_keyword_file:
        neg_keyword_df = pd.read_csv(negative_keyword_file, skiprows=2)
        neg_keyword_df = neg_keyword_df.dropna(subset=[neg_keyword_df.columns[1]])
        neg_keyword_df = neg_keyword_df[['Campaign', 'Ad group', 'Negative keyword', 'Keyword or list', 'Level', 'Match type']]
        
        # Rename 'Match type' to avoid confusion with keyword match type
        neg_keyword_df = neg_keyword_df.rename(columns={'Match type': 'Negative match type'})
        
        # Merge with existing dataframe
        merged_df = pd.merge(merged_df, neg_keyword_df, on=['Campaign', 'Ad group'], how='left')
    
    ## Display Results
    
    st.header("Regular Ads")
    
    # Filter out Demand Gen image ads
    regular_ads = merged_df[merged_df['Ad type'] != 'Demand Gen image ad']
    
    # Group by Campaign and Ad Group
    grouped = regular_ads.groupby(['Campaign', 'Ad group'])
    
    for (campaign, ad_group), group_data in grouped:
        with st.expander(f"Campaign: {campaign} - Ad Group: {ad_group}"):
            st.dataframe(group_data.drop(['Campaign', 'Ad group'], axis=1), use_container_width=True)
    
    ## Demand Gen Image Ads Section
    
    st.header("Demand Gen Image Ads")
    
    # Filter for Demand Gen image ads
    demand_gen_ads = merged_df[merged_df['Ad type'] == 'Demand Gen image ad']
    
    if not demand_gen_ads.empty:
        st.dataframe(demand_gen_ads, use_container_width=True)
    else:
        st.info("No Demand Gen image ads found in the dataset.")
    
    ## Download Options
    
    col1, col2 = st.columns(2)
    
    with col1:
        csv_all = merged_df.to_csv(index=False)
        st.download_button(
            label="Download Full CSV",
            data=csv_all,
            file_name="google_ads_analysis_all.csv",
            mime="text/csv",
        )
    
    with col2:
        csv_demand_gen = demand_gen_ads.to_csv(index=False)
        st.download_button(
            label="Download Demand Gen Image Ads CSV",
            data=csv_demand_gen,
            file_name="google_ads_analysis_demand_gen.csv",
            mime="text/csv",
        )
else:
    st.warning("Please upload the required CSV files.")