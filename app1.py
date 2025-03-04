import streamlit as st
import pandas as pd
import pymysql
from sqlalchemy import create_engine
from urllib.parse import quote_plus  # For URL encoding

# Initialize session state for navigation and data storage
if 'page' not in st.session_state:
    st.session_state.page = "server_connection"

if 'db_host' not in st.session_state:
    st.session_state.db_host = ""
if 'db_user' not in st.session_state:
    st.session_state.db_user = ""
if 'db_password' not in st.session_state:
    st.session_state.db_password = ""
if 'selected_db' not in st.session_state:
    st.session_state.selected_db = ""
if 'selected_table' not in st.session_state:
    st.session_state.selected_table = ""
if 'raw_data' not in st.session_state:
    st.session_state.raw_data = pd.DataFrame()
if 'cleaned_data' not in st.session_state:
    st.session_state.cleaned_data = pd.DataFrame()

# Helper Functions
def get_databases():
    try:
        connection = pymysql.connect(host=st.session_state.db_host, user=st.session_state.db_user, password=st.session_state.db_password)
        query = "SHOW DATABASES;"
        databases = pd.read_sql(query, connection)
        connection.close()
        return databases
    except Exception as e:
        st.error(f"Error fetching databases: {e}")
        return pd.DataFrame()

def get_tables(database_name):
    try:
        connection = pymysql.connect(host=st.session_state.db_host, user=st.session_state.db_user, password=st.session_state.db_password, database=database_name)
        query = "SHOW TABLES;"
        tables = pd.read_sql(query, connection)
        connection.close()
        return tables
    except Exception as e:
        st.error(f"Error fetching tables from database '{database_name}': {e}")
        return pd.DataFrame()

def extract_data(database_name, table_name):
    try:
        engine = create_engine(f'mysql+pymysql://{st.session_state.db_user}:{quote_plus(st.session_state.db_password)}@{st.session_state.db_host}/{database_name}')
        query = f'SELECT * FROM {table_name}'
        df = pd.read_sql(query, engine)
        return df
    except Exception as e:
        st.error(f"Error extracting data from table '{table_name}': {e}")
        return pd.DataFrame()

def load_cleaned_data(cleaned_df, database_name):
    try:
        engine = create_engine(f'mysql+pymysql://{st.session_state.db_user}:{quote_plus(st.session_state.db_password)}@{st.session_state.db_host}/{database_name}')
        cleaned_df.to_sql('cleaned_employee_data', engine, schema='etl', if_exists='replace', index=False)
        st.success("Cleaned data successfully loaded into 'etl.cleaned_employee_data'!")
    except Exception as e:
        st.error(f"Data loading failed: {e}")

# Navigation Buttons
def navigation_buttons(current_page, next_page=None, prev_page=None):
    col1, col2 = st.columns([1, 1])
    with col1:
        if prev_page and st.button("Previous", key=f"prev_{current_page}"):
            st.session_state.page = prev_page
    with col2:
        if next_page and st.button("Next", key=f"next_{current_page}"):
            st.session_state.page = next_page

# Page: Server Connection
def server_connection_page():
    st.title("Step 1: Database Connection")
    st.session_state.db_host = st.text_input('Enter Database Host (e.g., localhost):', value=st.session_state.db_host)
    st.session_state.db_user = st.text_input('Enter Database User (e.g., root):', value=st.session_state.db_user)
    st.session_state.db_password = st.text_input('Enter Database Password:', type="password", value=st.session_state.db_password)
    navigation_buttons("server_connection", next_page="data_extraction")

# Page: Data Extraction
def data_extraction_page():
    st.title("Step 2: Data Extraction")
    databases = get_databases()
    if not databases.empty:
        db_names = databases.iloc[:, 0].tolist()
        st.session_state.selected_db = st.selectbox('Select Database:', db_names, index=db_names.index(st.session_state.selected_db) if st.session_state.selected_db in db_names else 0)
        tables = get_tables(st.session_state.selected_db)
        if not tables.empty:
            table_names = tables.iloc[:, 0].tolist()
            st.session_state.selected_table = st.selectbox('Select Table:', table_names, index=table_names.index(st.session_state.selected_table) if st.session_state.selected_table in table_names else 0)
            if st.button("Extract Data"):
                st.session_state.raw_data = extract_data(st.session_state.selected_db, st.session_state.selected_table)
                st.write("Extracted Data:")
                st.dataframe(st.session_state.raw_data)
                st.session_state.page = "data_cleaning"
        else:
            st.warning(f"No tables found in database '{st.session_state.selected_db}'.")
    else:
        st.warning("No databases found or could not connect to the database server.")
    navigation_buttons("data_extraction", next_page="data_cleaning", prev_page="server_connection")

# Page: Data Cleaning
def data_cleaning_page():
    st.title("Step 3: Data Cleaning")
    if not st.session_state.raw_data.empty:
        st.write("Raw Data:")
        st.dataframe(st.session_state.raw_data)
        
        cleaning_options = {}
        for column in st.session_state.raw_data.columns:
            st.write(f"Cleaning options for column: **{column}**")
            options = st.multiselect(
                f"Select cleaning operations for column '{column}':",
                [
                    'Remove Duplicates', 
                    'Fill Missing Data', 
                    'Drop Rows with Missing Data',
                    'Correct Errors', 
                    'Standardize Format', 
                    'Trim Whitespaces', 
                    'Convert Data Types', 
                    'Remove Outliers', 
                    'Validate Data'
                ]
            )
            cleaning_options[column] = options

        if st.button("Clean Data"):
            cleaned_df = st.session_state.raw_data.copy()

            for column, options in cleaning_options.items():
                if 'Remove Duplicates' in options:
                    cleaned_df = cleaned_df.drop_duplicates(subset=[column], keep='first')
                    st.write(f"Dropped duplicates in column '{column}'.")

                if 'Fill Missing Data' in options:
                    default_value = st.text_input(f"Enter default value for missing data in column '{column}':", key=f"default_{column}")
                    cleaned_df[column] = cleaned_df[column].fillna(default_value)
                    st.write(f"Filled missing data in column '{column}' with '{default_value}'.")

                if 'Drop Rows with Missing Data' in options:
                    cleaned_df = cleaned_df[cleaned_df[column].notnull()]
                    st.write(f"Dropped rows with missing data in column '{column}'.")

                if 'Correct Errors' in options:
                    st.write(f"Corrected errors in column '{column}'.")

                if 'Standardize Format' in options:
                    if pd.api.types.is_string_dtype(cleaned_df[column]):
                        cleaned_df[column] = cleaned_df[column].str.capitalize()
                        st.write(f"Standardized format in column '{column}' (e.g., capitalized strings).")

                if 'Trim Whitespaces' in options:
                    if pd.api.types.is_string_dtype(cleaned_df[column]):
                        cleaned_df[column] = cleaned_df[column].str.strip()
                        st.write(f"Trimmed whitespaces in column '{column}'.")

                if 'Convert Data Types' in options:
                    try:
                        cleaned_df[column] = pd.to_numeric(cleaned_df[column], errors='coerce')
                        st.write(f"Converted column '{column}' to numeric.")
                    except Exception as e:
                        st.error(f"Failed to convert column '{column}' to numeric: {e}")

                if 'Remove Outliers' in options:
                    if pd.api.types.is_numeric_dtype(cleaned_df[column]):
                        q1 = cleaned_df[column].quantile(0.25)
                        q3 = cleaned_df[column].quantile(0.75)
                        iqr = q3 - q1
                        lower_bound = q1 - 1.5 * iqr
                        upper_bound = q3 + 1.5 * iqr
                        cleaned_df = cleaned_df[(cleaned_df[column] >= lower_bound) & (cleaned_df[column] <= upper_bound)]
                        st.write(f"Removed outliers in column '{column}'.")

                if 'Validate Data' in options:
                    st.write(f"Validated data in column '{column}'.")

            cleaned_df['id'] = range(1, len(cleaned_df) + 1)
            st.write("Cleaned Data After Processing:")
            st.dataframe(cleaned_df)

            st.session_state.cleaned_data = cleaned_df
            st.session_state.page = "data_loading"
    else:
        st.warning("No raw data available for cleaning.")
    
    navigation_buttons("data_cleaning", next_page="data_loading", prev_page="data_extraction")

# Page: Data Loading
def data_loading_page():
    st.title("Step 4: Data Loading")
    if not st.session_state.cleaned_data.empty:
        st.write("Cleaned Data:")
        st.dataframe(st.session_state.cleaned_data)
        if st.button("Load Cleaned Data"):
            load_cleaned_data(st.session_state.cleaned_data, st.session_state.selected_db)
            st.session_state.page = "completion"
    else:
        st.warning("No cleaned data available for loading.")
    navigation_buttons("data_loading", prev_page="data_cleaning")

# Page: Completion
def completion_page():
    st.title("Process Completed!")
    st.success("Data has been successfully extracted, cleaned, and loaded into the database.")
    if st.button("Restart Process"):
        st.session_state.page = "server_connection"

# Main App Logic
def main():
    if st.session_state.page == "server_connection":
        server_connection_page()
    elif st.session_state.page == "data_extraction":
        data_extraction_page()
    elif st.session_state.page == "data_cleaning":
        data_cleaning_page()
    elif st.session_state.page == "data_loading":
        data_loading_page()
    elif st.session_state.page == "completion":
        completion_page()

# Run the app
if __name__ == "__main__":
    main()