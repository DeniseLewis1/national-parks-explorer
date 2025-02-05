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
        name TEXT NOT NULL,
        categories[] TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS topics (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL
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
            image_url
        FROM parks
    """
    parks_df = pd.read_sql(query, conn)
    

    activities_data, parks_activities_data = get_activities_data()

    # Dashboard
    st.set_page_config(page_title="National Parks Explorer", layout="wide")
    st.title("National Parks Explorer")

    # Create map
    fig = px.scatter_mapbox(
        parks_df,
        lat="latitude",
        lon="longitude",
        zoom=2.5,
        height=600
    )

    fig.update_layout(mapbox_style="open-street-map")

    fig.update_traces(
        hovertemplate="<b style='font-size:14px;'>%{text}</b><br>"
        + "<a href='%{customdata[0]}' target='_blank' style='font-size:12px;'>View Park Site</a>",
        customdata=parks_df[["url"]].values,
        text=parks_df["name"]
    )

    # Display the map
    st.plotly_chart(fig)

    conn.close()


if __name__ == "__main__":
    main()