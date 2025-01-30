import requests
import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px


def main():
    # Connect to database
    conn = sqlite3.connect("national_parks.db")
    cursor = conn.cursor()

    # Create tables
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS parks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    """)

    conn.commit()


    # Load API key
    api_key = st.secrets["API_KEY"]

    # Define the API endpoint and parameters
    endpoint = "https://developer.nps.gov/api/v1/parks"

    params = {
        "api_key": api_key,
        "limit": 2000
    }

    # Make the GET request
    response = requests.get(endpoint, params=params)

    # Check if the request was unsuccessful
    if response.status_code != 200:
        raise RuntimeError(f"Error: {response.status_code}, {response.text}")

    # Store data in a dataframe
    response_data = response.json()
    data = response_data["data"]
    selected_fields = ["id", "fullName", "url", "parkCode", "states", "latitude", "longitude", "description", "designation", "images"]
    df = pd.DataFrame([{key: item[key] for key in selected_fields} for item in data])
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    df["image_url"] = df["images"].apply(lambda x: x[0]["url"] if isinstance(x, list) and x else None)
    
    # Insert data into parks table
    df = df.rename(columns={"fullName": "name", "parkCode": "park_code", "states": "state"})
    df.drop(columns=["images"], inplace=True)
    df.to_sql("parks", conn, if_exists="replace", index=False)

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
    

    conn.close()


if __name__ == "__main__":
    main()