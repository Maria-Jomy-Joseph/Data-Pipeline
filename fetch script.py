#---------------------------------------------------------
#Run the command below before executing the script

#pip install -r requirements.txt

#Modify the `api_key` and `db_params` as needed.
#---------------------------------------------------------
import psycopg2
import requests

# PostgreSQL database connection parameters
db_params = {
    "database": "postgres",
    "user": "postgres",
    "password": "admin",
    "host": "localhost",
    "port": "5432",
}

api_key = "provide api key here"

api_url = "https://api.apollo.io/v1/organizations/enrich"

def fetch_customer_industry(customer_name):
    try:
        headers = {
            'Cache-Control': 'no-cache',
            'Content-Type': 'application/json'
        }

        querystring = {
            "api_key": api_key,
            "domain": f"{customer_name}"
        }

        response = requests.request("GET", api_url, headers=headers, params=querystring)
        
        if response.status_code == 200:
            customer_data = response.json()
            industry = customer_data.get("organization", {}).get("industry")
            return industry
        else:
            return None
    except Exception as e:
        print(f"Error fetching data for customer {customer_name}: {e}")
        return None

    
def extract_domain(email):
    # Splitting the email address at the "@" symbol
    parts = email.split("@")
    
    # Checking if there are exactly two parts (username and domain)
    if len(parts) == 2:
        return parts[1]  # The second part is the domain
    else:
        return None  # Invalid email format

def update_customer_table():
    try:
        # Connecting to the PostgreSQL database
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()

        # Creating a new column "industry" in the "customers" table if it doesn't exist
        cursor.execute("ALTER TABLE customers ADD COLUMN IF NOT EXISTS industry text")

        # Execute a SELECT query to get customer IDs
        cursor.execute("SELECT customer_name,address_country_code,contact_email FROM customers")
        result = cursor.fetchall()

        for row in result:
            customer_name, code, email= row
            if " " in customer_name:
                # Replace spaces with hyphens
                customer_name_new = customer_name.replace(" ", "-")
            customer_name_new += "." + code.lower()
            industry = fetch_customer_industry(customer_name_new)
            if industry is None:
                email_domain = extract_domain(email) #as email is in the form "username@domain.com // a try to extract domain"
                if email_domain is not None:
                    industry = fetch_customer_industry(email_domain)  
                    
            elif industry is not None:
                # Update the "customers" table with the fetched industry data
                cursor.execute(
                    f"UPDATE customers SET industry = %s WHERE customer_name = %s",
                    (industry, customer_name)
                )

        # Commit the changes and close the database connection
        conn.commit()
        conn.close()
        print("Data updated successfully.")

    except Exception as e:
        print(f"Error updating data: {e}")

if __name__ == "__main__":
    update_customer_table()
