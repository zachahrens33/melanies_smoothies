# streamlit_app.py

import streamlit as st
from snowflake.snowpark.session import Session
from snowflake.snowpark.functions import col

# Cached session creation using Streamlit secrets
@st.cache_resource
def get_snowflake_session():
    connection_parameters = {
        "account": st.secrets["connections.snowflake"]["account"],
        "user": st.secrets["connections.snowflake"]["user"],
        "password": st.secrets["connections.snowflake"]["password"],
        "role": st.secrets["connections.snowflake"]["role"],
        "warehouse": st.secrets["connections.snowflake"]["warehouse"],
        "database": st.secrets["connections.snowflake"]["database"],
        "schema": st.secrets["connections.snowflake"]["schema"]
    }
    return Session.builder.configs(connection_parameters).create()

# Connect to Snowflake
session = get_snowflake_session()

# App UI
st.title(f"Customize Your Smoothie :cup_with_straw: {st.__version__}")
st.write("Choose the fruits you want in your custom smoothie!")

# Input: Name on order
name_on_order = st.text_input("Name on Smoothie:")
if name_on_order:
    st.write("The name of your smoothie will be:", name_on_order)

# Load fruit options from Snowflake
fruit_df = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"))
fruit_list = [row["FRUIT_NAME"] for row in fruit_df.collect()]

# Fruit selection input
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    options=fruit_list,
    max_selections=5
)

# Order submission
if ingredients_list and name_on_order:
    ingredients_string = ", ".join(ingredients_list)
    
    if st.button("Submit Order"):
        insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
        """
        session.sql(insert_stmt).collect()
        st.success("Your Smoothie is ordered!", icon="✅")
