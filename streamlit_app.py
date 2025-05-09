import streamlit as st
import snowflake.snowpark as snp
from snowflake.snowpark.functions import col

# Create Snowflake session
def get_snowflake_session():
    connection_params = {
        "account": st.secrets["connections.snowflake"]["account"],
        "user": st.secrets["connections.snowflake"]["user"],
        "password": st.secrets["connections.snowflake"]["password"],
        "warehouse": st.secrets["connections.snowflake"]["warehouse"],
        "database": st.secrets["connections.snowflake"]["database"],
        "schema": st.secrets["connections.snowflake"]["schema"]
    }
    return snp.Session.builder.configs(connection_params).create()

# Snowflake session
session = get_snowflake_session()

# Write directly to the app
st.title(f"Customize Your Smoothie :cup_with_straw: {st.__version__}")
st.write("Choose the fruits you want in your custom smoothie!")

# Get name input for the smoothie
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name of your smoothie will be:", name_on_order)

# Fetch fruit options from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

# Convert the Snowpark dataframe to a list of fruit names
fruit_list = [row['FRUIT_NAME'] for row in my_dataframe.collect()]

# Multi-select input for choosing fruits
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_list,
    max_selections=5
)

# Handle the order submission
if ingredients_list:
    ingredients_string = ' '.join(ingredients_list)
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """
    
    # Button to submit the order
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()  # Insert the order into the database
        st.success('Your Smoothie is ordered!', icon="✅")
