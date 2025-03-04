# Streamlit ETL Application

## GitHub Repo

### Overview
This Streamlit-based ETL (Extract, Transform, Load) application allows users to connect to a MySQL database, extract data from a selected table, clean the data based on customizable options, and load the cleaned data back into a target database. The app is designed to be interactive, user-friendly, and visually appealing, making it easy for users to perform data processing tasks without writing code.

### Features
- **Database Connection**: Connect to a MySQL database by providing host, username, and password.
- **Data Extraction**: Select a database and table to extract raw data.
- **Data Cleaning**: Apply customizable cleaning operations (e.g., drop duplicates, remove nulls, validate strings/numbers) to the extracted data.
- **Data Loading**: Load the cleaned data into a target database, either by creating a new table or appending to an existing one.
- **Interactive Interface**: Use navigation buttons, progress bars, and expandable sections for a seamless user experience.
- **Error Handling**: Provides descriptive error messages and warnings for failed operations.

### Prerequisites
Before running the application, ensure you have the following installed:

- Python 3.8 or higher
- **Streamlit**: Install using `pip install streamlit`
- **Pandas**: Install using `pip install pandas`
- **PyMySQL**: Install using `pip install pymysql`
- **SQLAlchemy**: Install using `pip install sqlalchemy`

You can install all dependencies at once using the following command:

```bash
pip install -r requirements.txt

````
## Requirements File (`requirements.txt`)

```plaintext
streamlit
pandas
pymysql
sqlalchemy
````
