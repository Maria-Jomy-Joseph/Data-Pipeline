# Data-Pipeline

The program is extracting customer industry data from an external source and storing it in a PostgreSQL database.

For the organization enrichment API, the domain name was not an optional query parameter; instead, it was a mandatory and singular field. Since the domain name information was not readily available in the database, two methods were attempted to create it. 

The first method involved generating the domain name by combining the customer's name and the country code, with a period ('.') in between them. For example, "Aalto.fi."
The second approach aimed to extract the domain name from the contact email, which often follows the format "example@domain.com."

Despite these efforts, the API request rate was limited, which in turn restricted the ability to update the database effectively
