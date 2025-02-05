import requests
import pandas as pd
import streamlit as st

# Load API key
api_key = st.secrets["API_KEY"]

# Get parks data from API
def get_parks_data():
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
    df = df.rename(columns={"fullName": "name", "parkCode": "park_code", "states": "state"})
    df.drop(columns=["images"], inplace=True)

    return df

# Get activities data from API
def get_activities_data():
    # Define the API endpoint and parameters
    endpoint = "https://developer.nps.gov/api/v1/activities/parks"

    params = {
        "api_key": api_key,
        "limit": 2000
    }

    # Make the GET request
    response = requests.get(endpoint, params=params)

    # Check if the request was unsuccessful
    if response.status_code != 200:
        raise RuntimeError(f"Error: {response.status_code}, {response.text}")

    # Store data in dataframes
    response_data = response.json()
    data = response_data["data"]
    selected_fields = ["id", "name"]
    activities_df = pd.DataFrame([{key: item[key] for key in selected_fields} for item in data])


    rows = []
    for activity in data:
        activity_id = activity["id"]
        for park in activity["parks"]:
            park_code = park["parkCode"]
            rows.append((park_code, activity_id))

    parks_activites_df = pd.DataFrame(rows, columns=["park_code", "activity_id"])

    return (activities_df, parks_activites_df)

# Get amenities data from API
def get_amenities_data():
    # Define the API endpoint and parameters
    endpoint = "https://developer.nps.gov/api/v1/amenities/parksplaces"

    params = {
        "api_key": api_key,
        "limit": 2000
    }

    # Make the GET request
    response = requests.get(endpoint, params=params)

    # Check if the request was unsuccessful
    if response.status_code != 200:
        raise RuntimeError(f"Error: {response.status_code}, {response.text}")

    # Store data in dataframes
    response_data = response.json()
    data = response_data["data"]

    rows = []
    for amenity in data:
        id = amenity[0]["id"]
        name = amenity[0]["name"]
        rows.append((id, name))
    amenities_df = pd.DataFrame(rows, columns=["id", "name"])

    rows = []
    for amenity in data:
        amenity_id = amenity[0]["id"]
        for park in amenity[0]["parks"]:
            park_code = park["parkCode"]
            rows.append((park_code, amenity_id))

    parks_amenities_df = pd.DataFrame(rows, columns=["park_code", "amenity_id"])

    return (amenities_df, parks_amenities_df)