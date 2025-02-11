import requests
import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px
from fetch_data import *


def main():
    # Connect to database
    conn = sqlite3.connect("national_parks.db")
    cursor = conn.cursor()

    # Create tables
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS parks (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        url TEXT NOT NULL,
        park_code TEXT NOT NULL,
        state TEXT NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        description TEXT NOT NULL,
        designation TEXT NOT NULL,
        image_url TEXT NOT NULL,
        is_free BOOLEAN
    );

    CREATE TABLE IF NOT EXISTS activities (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS amenities (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS topics (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL
    );
                         
    CREATE TABLE IF NOT EXISTS campgrounds (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        park_code TEXT                   
    );

    CREATE TABLE IF NOT EXISTS parks_activities (
        park_id TEXT NOT NULL,
        activity_id TEXT NOT NULL,
        park_code TEXT,
        PRIMARY KEY (park_id, activity_id),
        FOREIGN KEY (park_id) REFERENCES parks(id),
        FOREIGN KEY (activity_id) REFERENCES activities(id)
    );

    CREATE TABLE IF NOT EXISTS parks_amenities (
        park_id TEXT NOT NULL,
        amenity_id TEXT NOT NULL,
        park_code TEXT,
        PRIMARY KEY (park_id, amenity_id),
        FOREIGN KEY (park_id) REFERENCES parks(id),
        FOREIGN KEY (amenity_id) REFERENCES amenities(id)
    );

    CREATE TABLE IF NOT EXISTS parks_topics (
        park_id TEXT NOT NULL,
        topic_id TEXT NOT NULL,
        park_code TEXT,
        PRIMARY KEY (park_id, topic_id),
        FOREIGN KEY (park_id) REFERENCES parks(id),
        FOREIGN KEY (topic_id) REFERENCES topics(id)
    );
    """)

    conn.commit()


    # Insert data into parks table
    parks_data = get_parks_data()
    parks_data.to_sql("parks", conn, if_exists="replace", index=False)

    # Query parks
    query = """
        SELECT
            id,
            name,
            url,
            park_code,
            state,
            latitude,
            longitude,
            image_url,
            is_free
        FROM parks
    """
    parks_df = pd.read_sql(query, conn)
    

    activities_data, parks_activities_data = get_activities_data()

    # Insert data into activities table
    activities_data.to_sql("activities", conn, if_exists="replace", index=False)

    # Insert data into parks_activities table
    parks_activities_data = parks_activities_data.merge(parks_df.rename(columns={"id": "park_id"})[["park_code", "park_id"]], on="park_code", how="left")
    parks_activities_data.to_sql("parks_activities", conn, if_exists="replace", index=False)


    amenities_data, parks_amenities_data = get_amenities_data()

    # Insert data into amenities table
    amenities_data.to_sql("amenities", conn, if_exists="replace", index=False)

    # Insert data into parks_amenities table
    parks_amenities_data = parks_amenities_data.merge(parks_df.rename(columns={"id": "park_id"})[["park_code", "park_id"]], on="park_code", how="left")
    parks_amenities_data.to_sql("parks_amenities", conn, if_exists="replace", index=False)


    topics_data, parks_topics_data = get_topics_data()
    
    # Insert data into topics table
    topics_data.to_sql("topics", conn, if_exists="replace", index=False)

    # Insert data into parks_topics table
    parks_topics_data = parks_topics_data.merge(parks_df.rename(columns={"id": "park_id"})[["park_code", "park_id"]], on="park_code", how="left")
    parks_topics_data.to_sql("parks_topics", conn, if_exists="replace", index=False)


    # Insert data into campgrounds table
    campgrounds_data = get_campgrounds_data()
    campgrounds_data.to_sql("campgrounds", conn, if_exists="replace", index=False)


    # Dashboard
    st.set_page_config(page_title="National Parks Explorer", layout="wide")
    st.title("National Parks Explorer")

    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)

    # State filter
    with col1:
        states = sorted(parks_df["state"].str.split(",").explode().unique())
        selected_states = st.multiselect("Select State", states)

        if selected_states:
            filtered_state_park_codes = parks_df.loc[parks_df["state"].apply(lambda x: any(state in x.split(",") for state in selected_states)), "park_code"]
        else:
            filtered_state_park_codes = parks_df["park_code"]
        
    # Activity filter
    with col2:
        selected_activities = st.multiselect("Select Activity", activities_data["name"])
        
        if selected_activities:
            selected_activity_ids = activities_data.loc[activities_data["name"].isin(selected_activities), "id"]
            filtered_activity_park_codes = parks_activities_data.loc[parks_activities_data["activity_id"].isin(selected_activity_ids), "park_code"]
        else:
            filtered_activity_park_codes = parks_df["park_code"]

    # Amenity filter
    with col3:
        selected_amenities = st.multiselect("Select Amenity", amenities_data["name"])

        if selected_amenities:
            selected_amenity_ids = amenities_data.loc[amenities_data["name"].isin(selected_amenities), "id"]
            filtered_amenity_park_codes = parks_amenities_data.loc[parks_amenities_data["amenity_id"].isin(selected_amenity_ids), "park_code"]
        else:
            filtered_amenity_park_codes = parks_df["park_code"]

    # Topic filter
    with col4:
        selected_topics = st.multiselect("Select Topic", topics_data["name"])

        if selected_topics:
            selected_topic_ids = topics_data.loc[topics_data["name"].isin(selected_topics), "id"]
            filtered_topic_park_codes = parks_topics_data.loc[parks_topics_data["topic_id"].isin(selected_topic_ids), "park_code"]
        else:
            filtered_topic_park_codes = parks_df["park_code"]


    # Create a filtered dataframe based on filter criteria
    filtered_park_codes = set(filtered_state_park_codes) & set(filtered_activity_park_codes) & set(filtered_amenity_park_codes) & set(filtered_topic_park_codes)
    filtered_df = parks_df[parks_df["park_code"].isin(filtered_park_codes)]
    print(filtered_df.shape)


    # Create map
    fig = px.scatter_mapbox(
        filtered_df,
        lat="latitude",
        lon="longitude",
        zoom=2.5,
        height=600
    )

    fig.update_layout(mapbox_style="open-street-map")

    fig.update_traces(
        hovertemplate="<b style='font-size:14px;'>%{text}</b><br>"
        + "<a href='%{customdata[0]}' target='_blank' style='font-size:12px;'>View Park Site</a>",
        customdata=filtered_df[["url"]].values,
        text=filtered_df["name"]
    )

    # Display the map
    st.plotly_chart(fig)

    conn.close()


if __name__ == "__main__":
    main()