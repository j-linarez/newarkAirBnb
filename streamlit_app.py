import streamlit as st

import pandas as pd
import altair as alt

st.set_page_config(layout="wide", page_title="Newark Airbnb Dashboard")
st.title("**Investigating Newark's AirBnb Listings**")
#
# Load and prepare the data
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/j-linarez/A6Images/refs/heads/main/NewarkListings.csv"
    df = pd.read_csv(url)
    df['price'] = df['price'].replace('[\$,]', '', regex=True).astype(float)
    df['host_location'] = df['host_location'].fillna('Unknown')
    df = df[['property_type', 'price', 'review_scores_rating', 'host_total_listings_count', 'reviews_per_month', 'host_location']].dropna()
    return df

df = load_data()

# Sidebar filters
st.sidebar.header("Filter by...")
min_price, max_price = st.sidebar.slider("**Price in $**", 0, int(df["price"].max()), (50, 300))
selected_types = st.sidebar.multiselect(
    "**Property Types**", 
    options=df['property_type'].value_counts().index.tolist(), 
    default=df['property_type'].value_counts().nlargest(6).index.tolist()
)

# Filtered dataframe
filtered = df[
    (df['price'] >= min_price) & 
    (df['price'] <= max_price) & 
    (df['property_type'].isin(selected_types))
]


# I don't like getting the setup of this. This is bascially css
# all over AGAIN AHHHHH

# ok for personal reference, KEEP THESE AS LIMIT OF COLUMNS
col1, col2 = st.columns(2)

# Visulize the median booking price of top 6 bookigns initially
with col1:
    price_medians = filtered.groupby('property_type', as_index=False)['price'].median()
    chart1 = alt.Chart(price_medians).mark_bar().encode(
        x=alt.X('price:Q', title='Median Price in $'),
        y=alt.Y('property_type:N', sort='-x'),
        color=alt.Color('price:Q', scale=alt.Scale(scheme="greens")),
        tooltip=['property_type:N', alt.Tooltip('price:Q', format="$,.2f")]
    ).properties(
        width=500,
        height=400,
        title='Median Booking Price by Property Type'
    )
    st.altair_chart(chart1, use_container_width=True)

# Visulize the whiskerplots of reviews the property types typically get
with col2:
    boxplot = alt.Chart(filtered).mark_boxplot(extent='min-max', color = "navy").encode(
        x=alt.X('reviews_per_month:Q', title='Reviews Per Month'),
        y=alt.Y('property_type:N', sort='-x'),
        tooltip=['property_type:N', 'reviews_per_month:Q']
    ).properties(
        width=500,
        height=400,
        title='Reviews Per Month by Property Type'
    )
    st.altair_chart(boxplot, use_container_width=True)

st.markdown("---")  
# most popular related AHHH host locations!
excluded = ["Newark, NJ", "New Jersey, United States", "United States", "New York, United States", "Unknown"]
df_hosts = filtered[~filtered['host_location'].isin(excluded)]
top_hosts = df_hosts['host_location'].value_counts().nlargest(10).reset_index()
top_hosts.columns = ['host_location', 'count']

chart3 = alt.Chart(top_hosts).mark_bar().encode(
    x=alt.X('count:Q', title='Number of Listings'),
    y=alt.Y('host_location:N', sort='-x'),
    color=alt.Color('count:Q', scale=alt.Scale(scheme="reds")),
    tooltip=['host_location:N', 'count:Q']
).properties(
    width=1000,
    height=400,
    title='Top 10 Host Locations Outside Newark'
)
st.altair_chart(chart3, use_container_width=True)