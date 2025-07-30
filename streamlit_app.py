# Import python packages
import streamlit as st
import pandas as pd
from snowflake.snowpark.functions import col
import requests

# Write directly to the app
st.title(":tropical_drink: Welcome to Melanie's Smoothie Bar! :tropical_drink:")

st.write(
    """
    You can mix up to 5 ingredients for best taste!
    """
)

name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Get the fruit table
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON')).to_pandas()

# OPTIONAL: Show the dataframe for reference
# st.dataframe(my_dataframe, use_container_width=True)

# Use the FRUIT_NAME column for selection
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe['FRUIT_NAME'].tolist(),
    max_selections=5
)

# If ingredients are selected, show nutrition info
if ingredients_list:
    ingredients_string = ""
    for fruit_chosen in ingredients_list:
        search_term = my_dataframe.loc[my_dataframe['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].values[0]
        ingredients_string += fruit_chosen + ' '

        st.subheader(fruit_chosen + ' Nutrition Information')
        response = requests.get("https://fruityvice.com/api/fruit/" + search_term)

        if response.status_code == 200:
            fruityvice_data = response.json()
            st.json(fruityvice_data)  # Or use st.write(pd.json_normalize(fruityvice_data)) for cleaner view
        else:
            st.error("No data found for " + fruit_chosen)

    # Insert order
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(ingredients, name_on_order)
        VALUES ('{ingredients_string.strip()}', '{name_on_order}')
    """

    if st.button('Submit Order'):
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")
