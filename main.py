import streamlit as st
import pandas as pd
import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Decorator function to manage database connection
def connector(func):
    def wrapper(self, *args, **kwargs):
        try:
            # Establish database connection
            self.conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.db_name,
                auth_plugin='mysql_native_password'
            )
            self.cursor = self.conn.cursor()
            # Execute the decorated function
            result = func(self, *args, **kwargs)
        except mysql.connector.Error as e:
            result = f"Database error: {e}"
        finally:
            # Ensure connection is closed
            if hasattr(self, "conn"):
                self.conn.close()
        return result
    return wrapper

# Database class
class Database:
    def __init__(self, table_name):
        self.table_name = table_name
        self.db_name = os.getenv("database")
        self.user = os.getenv("user")
        self.password = str(os.getenv("password"))
        self.host = os.getenv("host")

    @connector
    def get_all_records(self):
        # Use parameterized query for safety
        query = f"SELECT * FROM {self.table_name}"
        self.cursor.execute(query)
        records = self.cursor.fetchall()
        return records

    @connector
    def add_record(self, values):
        # Adjust this query based on your table schema
        placeholders = ", ".join(["%s"] * len(values))
        query = f"INSERT INTO {self.table_name} VALUES ({placeholders})"
        self.cursor.execute(query, values)
        self.conn.commit()
        return "Record added successfully"

# Initialize session state for navigation
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "home"

def navigate_to(page_name: str):
    st.session_state["current_page"] = page_name

# Main application
if __name__ == "__main__":
    current_page = st.session_state.get("current_page", "home")

    if current_page == "home":
        st.title("DBMS Projects")
        st.write("WELCOME to DBMS Projects")
        if st.button("Getting Started ->"):
            navigate_to("dashboard")

    elif current_page == "dashboard":
        st.title("Dashboard")
        st.write("Select which operation you want to perform")
        if st.button("See all records ->"):
            navigate_to("records")
        elif st.button("Add a new record ->"):
            navigate_to("add_record")
        elif st.button("Delete a record ->"):
            navigate_to("delete_record")
        elif st.button("Update a record ->"):
            navigate_to("update_record")
        elif st.button("Search a record ->"):
            navigate_to("search_record")
        elif st.button("Create a new table ->"):
            navigate_to("create_table")

    elif current_page == "records":
        st.title("Display All Records")
        st.write("Enter the table name to see all records")
        table_name = st.text_input("Table Name")
        if st.button("See all records"):
            if not table_name:
                st.error("Please enter a valid table name.")
            else:
                db = Database(table_name)
                records = db.get_all_records()
                if isinstance(records, str):  # Check for error message
                    st.error(records)
                elif records:
                    records_df = pd.DataFrame(
                        records, columns=[desc[0] for desc in db.cursor.description]
                    )
                    st.write(records_df)
                else:
                    st.write("No records found in the table.")
