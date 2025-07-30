# Import python packages
import streamlit as st
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


cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
#st.dataframe(data=my_dataframe, use_container_width=True)

ingredients_list = st.multiselect(
    'choose up to 5 ingredients:'
, my_dataframe
,  max_selections=5    
)
if ingredients_list:
    ingredients_string = ' '.join(ingredients_list)
    fruityvice_response = requests.get("https://fruityvice.com/api/fruit/watermelon")
    sf_df = st.dataframe(data=fruityvice_response.json(), use_container_width=True)
  

    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """
    st.write(my_insert_stmt)

    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")





