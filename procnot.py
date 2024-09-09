import requests
import psycopg2
import json

# Database connection parameters
db_name = 'RFPs'
db_user = 'postgres'
db_password = '0987'
db_host = 'localhost'
db_port = '5432'
table = 'world_bank_notices'

# Connect to PostgreSQL database
conn = psycopg2.connect(
    dbname=db_name,
    user=db_user,
    password=db_password,
    host=db_host,
    port=db_port
)
cursor = conn.cursor()

# Base URL for the World Bank API
base_url = "https://search.worldbank.org/api/v2/procnotices"

# Parameters for the API request
params = {
    "format": "json",
    "rows": 100000,  # Fetching up to 1000 records per request
    "os": 0,    # Starting offset
    "strdate": "2024-01-01",  # Start date filter
}

# Function to insert data into PostgreSQL
def insert_data(doc):
    try:
        cursor.execute(
            f"""
            INSERT INTO {table} 
            (id, notice_type, noticedate, notice_lang_name, notice_status, 
             submission_deadline_date, submission_deadline_time, project_ctry_name, 
             project_id, project_name, bid_reference_no, bid_description, 
             procurement_group, procurement_method_code, procurement_method_name, 
             contact_address, contact_ctry_name, contact_email, contact_name, 
             contact_organization, contact_phone_no, submission_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING;  -- Avoid duplicates
            """,
            (
                doc.get('id'),
                doc.get('notice_type'),
                doc.get('noticedate'),
                doc.get('notice_lang_name'),
                doc.get('notice_status'),
                doc.get('submission_deadline_date'),
                doc.get('submission_deadline_time'),
                doc.get('project_ctry_name'),
                doc.get('project_id'),
                doc.get('project_name'),
                doc.get('bid_reference_no'),
                doc.get('bid_description'),
                doc.get('procurement_group'),
                doc.get('procurement_method_code'),
                doc.get('procurement_method_name'),
                doc.get('contact_address'),
                doc.get('contact_ctry_name'),
                doc.get('contact_email'),
                doc.get('contact_name'),
                doc.get('contact_organization'),
                doc.get('contact_phone_no'),
                doc.get('submission_date')
            )
        )
        conn.commit()  # Commit after each successful insert
        print(f"Inserted notice with ID: {doc.get('id')}")
    except Exception as e:
        print(f"Error inserting data: {e}")

# Make the API request
response = requests.get(base_url, params=params)

# Check if the request was successful
if response.status_code == 200:
    data = response.json()

    # Print out the raw response for debugging
    print("Full API response:")
    print(json.dumps(data, indent=4))

    procnotices = data.get('procnotices', [])

    # Check if any procurement notices exist
    if procnotices:
        for doc in procnotices:
            # Insert each document into the database
            insert_data(doc)
    else:
        print("No procurement notices found in the 'procnotices' key.")
else:
    print(f"Request failed with status code {response.status_code}")

# Close the database connection
cursor.close()
conn.close()
