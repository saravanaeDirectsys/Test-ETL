import streamlit as st
import pandas as pd
import pymysql
from sqlalchemy import create_engine
from urllib.parse import quote_plus  # For URL encoding

# Streamlit user inputs for database connection
DB_HOST = st.text_input('Enter Database Host (e.g., localhost):', )
DB_USER = st.text_input('Enter Database User (e.g., root):', )
DB_PASSWORD = st.text_input('Enter Database Password:', '', )  # Secure password input
DB_NAME = st.text_input('Enter Database Name (e.g., ETL):', )

# URL-encode the password to handle special characters like '@'
DB_PASSWORD_ENCODED = quote_plus(DB_PASSWORD)

# Create a connection engine
try:
    # Use the encoded password in the connection string
    engine = create_engine(f'mysql+pymysql://{DB_USER}:{DB_PASSWORD_ENCODED}@{DB_HOST}/{DB_NAME}')
    with engine.connect() as connection:
        st.success("Database connection successful!")
except Exception as e:
    st.error(f"Database connection failed: {e}")
    st.stop()

# Step 1: Extract data from the database
def extract_data():
    try:
        query = 'SELECT * FROM employee_data'
        df = pd.read_sql(query, engine)
        return df
    except Exception as e:
        st.error(f"Data extraction failed: {e}")
        return pd.DataFrame()



# Step 2: Clean the data
def clean_data(df):
    try:
        # Debug: Print raw data before cleaning
        st.write("Raw Data Before Cleaning:")
        st.dataframe(df)

        # Remove duplicates based on 'name' and 'phone'
        df = df.drop_duplicates(subset=['name', 'phone'])
        st.write(f"Rows after dropping duplicates: {len(df)}")

        # Check if 'name' is a non-empty string
        df = df[df['name'].notnull() & (df['name'].astype(str).str.strip() != '')]  # Remove empty or whitespace-only names
        st.write(f"Rows after removing invalid names: {len(df)}")

        # Check if 'phone' is a string with length >= 3
        df['phone'] = df['phone'].astype(str)  # Convert phone column to string
        df = df[df['phone'].str.len() >= 3]  # Keep rows where phone length is >= 3
        st.write(f"Rows after checking phone length >= 3: {len(df)}")

        # Check if 'number' is a valid integer and remove rows with null or string values in 'number'
        df = df[pd.to_numeric(df['number'], errors='coerce').notnull()]  # Remove rows where 'number' is null or a string
        st.write(f"Rows after checking 'number' type (only valid integers): {len(df)}")

        # Generate an 'id' column (if not already present in the data)
        df['id'] = range(1, len(df) + 1)  # Generate a sequential 'id' column (starting from 1)

        # Debug: Print cleaned data
        st.write("Cleaned Data After Processing:")
        st.dataframe(df)

        return df
    except Exception as e:
        st.error(f"Data cleaning failed: {e}")
        return pd.DataFrame()

# Step 3: Load cleaned data into the etl.cleaned_employee_data table
def load_cleaned_data(cleaned_df):
    try:
        # Ensure the dataframe columns match the table schema
        cleaned_df = cleaned_df[['id', 'name', 'phone', 'number']]  # Match the table's columns
        # Show cleaned data before inserting
        st.write("Inserting the following cleaned data into 'etl.cleaned_employee_data':")
        st.dataframe(cleaned_df)
        
        # Insert data into the database
        cleaned_df.to_sql('cleaned_employee_data', engine, schema='etl', if_exists='replace', index=False)
        st.success("Cleaned data successfully loaded into 'etl.cleaned_employee_data'!")
    except Exception as e:
        st.error(f"Data loading failed: {e}")

# Streamlit App Layout
st.title("Employee Data Cleaning Process")

# Button to extract raw data
if st.button("Extract Raw Data"):
    raw_data = extract_data()
    if raw_data.empty:
        st.warning("No data found in the 'employee_data' table.")
    else:
        st.write("Extracted Raw Data:")
        st.dataframe(raw_data)

# Button to clean the data
if st.button("Clean Data"):
    raw_data = extract_data()
    if raw_data.empty:
        st.warning("No data found in the 'employee_data' table.")
    else:
        cleaned_data = clean_data(raw_data)
        if cleaned_data.empty:
            st.warning("No valid data after cleaning.")
        else:
            st.write("Cleaned Data:")
            st.dataframe(cleaned_data)

# Button to load cleaned data into the database
if st.button("Load Cleaned Data"):
    raw_data = extract_data()
    if raw_data.empty:
        st.warning("No data found in the 'employee_data' table.")
    else:
        cleaned_data = clean_data(raw_data)
        if cleaned_data.empty:
            st.warning("No valid data after cleaning.")
        else:
            load_cleaned_data(cleaned_data)

# Optional: Insert sample data for testing
if st.button("Insert Sample Data for Testing"):
    try:
        sample_data = [
            ("Alice Johnson", "123-456-7890", "E123"),
            ("Bob Smith", "987-654-3210", "E124"),
            ("Charlie Brown", "555-555-5555", "E125"),
            ("Invalid Name", "", "E126"),  # Invalid row
            ("", "1234567890", "E127")     # Invalid row
        ]
        insert_query = """
        INSERT INTO employee_data (name, phone, number)
        VALUES (%s, %s, %s)
        """
        connection = engine.connect()
        connection.execute(insert_query, sample_data)
        st.success("Sample data inserted successfully!")
    except Exception as e:
        st.error(f"Failed to insert sample data: {e}")

st.title("Hi Maline")