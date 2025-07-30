# Import python packages
import streamlit as st
import pandas as pd
from snowflake.snowpark.functions import col
import requests

# App title
st.title(":tropical_drink: Welcome to Melanie's Smoothie Bar! :tropical_drink:")

st.write(
    """
    You can mix up to 5 ingredients for best taste!
    """
)

# Smoothie name input
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Get fruit table as a pandas DataFrame
my_dataframe = session.table("smoothies.public.fruit_options").select(
    col('FRUIT_NAME'), col('SEARCH_ON')
).to_pandas()

# Multiselect input
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe['FRUIT_NAME'].tolist(),
    max_selections=5
)

# Show nutrition info and prepare insert
if ingredients_list:
    ingredients_string = ""

    for fruit_chosen in ingredients_list:
        # Get the search term from the dataframe
        search_term = my_dataframe.loc[
            my_dataframe['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'
        ].values[0]

        ingredients_string += fruit_chosen + ' '

        st.subheader(fruit_chosen + ' Nutrition Information')

        # Get API data
        response = requests.get("https://fruityvice.com/api/fruit/" + search_term)

        if response.status_code == 200:
            fruityvice_data = response.json()
            
            # ✅ Convert API JSON to a pandas DataFrame
            fruityvice_df = pd.json_normalize(fruityvice_data)

            # ✅ Display using Streamlit
            st.dataframe(fruityvice_df)
        else:
            st.error("No data found for " + fruit_chosen)

    # Insert order
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(ingredients, name_on_order)
        VALUES ('{ingredients_string.strip()}', '{name_on_order}')
    """

    # Submit button
    if st.button('Submit Order'):
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")
