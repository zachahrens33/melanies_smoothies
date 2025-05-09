# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
from snowflake.snowpark.session import Session

# Set page title
st.set_page_config(page_title="Smoothie Customizer", page_icon="🥤")

# Set Streamlit title
st.title(f"Customize Your Smoothie :cup_with_straw: (v{st.__version__})")
st.write("Choose the fruits you want in your custom smoothie!")

# Initialize Snowpark session (update with your actual Snowflake connection info if needed)
@st.cache_resource
def get_snowflake_session():
    connection_parameters = {
        "account": "your_account",
        "user": "your_user",
        "password": "your_password",
        "role": "your_role",
        "warehouse": "your_warehouse",
        "database": "smoothies",
        "schema": "public"
    }
    return Session.builder.configs(connection_parameters).create()

session = get_snowflake_session()

# Fetch fruit list from Snowflake
fruit_df = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
fruit_list = [row['FRUIT_NAME'] for row in fruit_df.collect()]

# Input fields
name_on_order = st.text_input("Name on Smoothie:")
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_list,
    max_selections=5
)

# Submit order logic
if st.button("Submit Order"):
    if not name_on_order:
        st.warning("Please enter a name for your smoothie.")
    elif not ingredients_list:
        st.warning("Please select at least one ingredient.")
    else:
        ingredients_string = ', '.join(ingredients_list)

        # Insert order using parameterized Snowpark method
        session.table("smoothies.public.orders").insert([
            {"ingredients": ingredients_string, "name_on_order": name_on_order}
        ])
        st.success(f"Your smoothie has been ordered, {name_on_order}! ✅")
