# Import packages
import streamlit as st
from snowflake.snowpark.session import Session
from snowflake.snowpark.functions import col

# Streamlit UI
st.title(f"Customize Your Smoothie :cup_with_straw: {st.__version__}")
st.write("Choose the fruits you want in your custom smoothie!")

# User input for smoothie name
name_on_order = st.text_input("Name on Smoothie:")
if name_on_order:
    st.write("The name of your smoothie will be:", name_on_order)

# Cached Snowflake session
@st.cache_resource
def get_snowflake_session():
    connection_parameters = {
        "account": st.secrets["connections.snowflake"]["account"],
        "user": st.secrets["connections.snowflake"]["user"],
        "password": st.secrets["connections.snowflake"]["password"],
        "role": st.secrets["connections.snowflake"]["role"],
        "warehouse": st.secrets["connections.snowflake"]["warehouse"],
        "database": st.secrets["connections.snowflake"]["database"],
        "schema": st.secrets["connections.snowflake"]["schema"],
        "client_session_keep_alive": st.secrets["connections.snowflake"].get("client_session_keep_alive", True),
    }
    return Session.builder.configs(connection_parameters).create()

# Initialize session
session = get_snowflake_session()

# Load fruit options from Snowflake
fruit_df = session.table("fruit_options").select(col("FRUIT_NAME")).to_pandas()
fruit_list = fruit_df["FRUIT_NAME"].tolist()

# Multiselect for ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_list,
    max_selections=5
)

# Handle order submission
if ingredients_list and name_on_order:
    ingredients_string = ', '.join(ingredients_list)
    
    if st.button("Submit Order"):
        insert_stmt = f"""
            INSERT INTO orders (ingredients, name_on_order)
            VALUES ('{ingredients_string}', '{name_on_order}')
        """
        session.sql(insert_stmt).collect()
        st.success("Your Smoothie is ordered! ✅")
