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
    parks_df = pd.DataFrame([{key: item[key] for key in selected_fields} for item in data])
    parks_df["latitude"] = pd.to_numeric(parks_df["latitude"], errors="coerce")
    parks_df["longitude"] = pd.to_numeric(parks_df["longitude"], errors="coerce")
    parks_df["image_url"] = parks_df["images"].apply(lambda x: x[0]["url"] if isinstance(x, list) and x else None)
    parks_df = parks_df.rename(columns={"fullName": "name", "parkCode": "park_code", "states": "state"})
    parks_df.drop(columns=["images"], inplace=True)

   
    endpoint = "https://developer.nps.gov/api/v1/feespasses"
    
    # Make the GET request
    response = requests.get(endpoint, params=params)
    
    # Check if the request was unsuccessful
    if response.status_code != 200:
        raise RuntimeError(f"Error: {response.status_code}, {response.text}")
    
    # Store data in a dataframe
    response_data = response.json()
    data = response_data["data"]
    selected_fields = ["parkCode", "isFeeFreePark"]
    fees_df = pd.DataFrame([{key: item[key] for key in selected_fields} for item in data])

    parks_df = parks_df.merge(fees_df.rename(columns={"parkCode": "park_code", "isFeeFreePark": "is_free"})[["park_code", "is_free"]], on="park_code", how="left")

    return parks_df

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

# Get topics data from API
def get_topics_data():
    # Define the API endpoint and parameters
    endpoint = "https://developer.nps.gov/api/v1/topics/parks"

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
    topics_df = pd.DataFrame([{key: item[key] for key in selected_fields} for item in data])


    rows = []
    for topic in data:
        topic_id = topic["id"]
        for park in topic["parks"]:
            park_code = park["parkCode"]
            rows.append((park_code, topic_id))

    parks_topics_df = pd.DataFrame(rows, columns=["park_code", "topic_id"])

    return (topics_df, parks_topics_df)