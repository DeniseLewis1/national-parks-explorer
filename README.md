# National Parks Explorer

## Table of Contents
1. [Introduction](#introduction)
2. [Features](#features)
3. [Technologies Used](#technologies-used)
4. [Installation](#installation)
5. [Usage](#usage)
6. [Visuals](#visuals)
7. [Future enhancements](#future-enhancements)

## Introduction
The National Parks Explorer is an interactive dashboard that allows users to explore U.S. National Parks using data from the [National Park Service API](https://www.nps.gov/subjects/developer/api-documentation.htm). Users can filter parks by state, activities, amenities, and topics while viewing their locations on an interactive map.

Click [here](https://national-parks-explorer.streamlit.app/) to view.

## Features
- Display park locations on an interactive map
- View park name and website when hovering over park location
- Map dynamically updates to show parks based on selected filters:
    - State
    - Activities (e.g., hiking, camping, wildlife watching)
    - Amenities (e.g., restrooms, picnic areas)
    - Topics (e.g., archeology, waterfalls)

## Technologies Used
- **Backend**: Python, SQLite, ETL, REST API
- **Frontend**: Streamlit
- **Data Manipulation**: Pandas
- **Visualization**: Plotly

## Installation
1. Clone the repository:
    ```
    git clone https://github.com/your-username/national-parks-explorer.git
    cd national-parks-explorer
    ```
2. Install the required dependencies:
    ```
    pip install -r requirements.txt
    ```
3. Run the application:
    ```
    streamlit run main.py
    ```

## Usage
1. Open the application in your browser.
2. Use the filters to select parks based on state, activities, amenities, or topics.
3. View the updated map displaying parks that match your selections.
4. Hover over a park location to see its name and website.

## Visuals
Dashboard:

![Dashboard](/images/dashboard.png)

Schema:

![Schema](/images/schema.png)

## Future enhancements
- Add analytical insights and visualizations using aggregated data.
- Ability to view list of parks that match search criteria.