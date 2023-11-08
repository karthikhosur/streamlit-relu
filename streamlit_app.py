import streamlit as st
from supabase import create_client, Client
import requests
import json 
import uuid


# Supabase settings
SUPABASE_URL = "https://vqssuexxzajyciiqdnek.supabase.co"
SUPABASE_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZxc3N1ZXh4emFqeWNpaXFkbmVrIiwicm9sZSI6ImFub24iLCJpYXQiOjE2OTY1NjM2NTcsImV4cCI6MjAxMjEzOTY1N30.PdFq6mep2N8dU1vDXd6lofL8krKPjK8FA17lNYrm_N8"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_API_KEY)


# Define a dictionary to map page names to their corresponding content
pages = {
    "Home": "Welcome to the Home Page!",
    "Containers": "Containers Management",
    "Customers": "You can contact us here.",
}

# Create a sidebar with navigation options
selected_page = st.sidebar.radio("Navigation", list(pages.keys()), index=0)

# Display the content based on the selected page
st.title(selected_page)
st.write(pages[selected_page])

data,count = supabase.table("webhook_listener").select('*').neq('processed','done').execute()
# .eq('processed','new')

result = data[1]


for r in result:
    if 'method' not in r and 'body' in r and 'type' in r['body']:
        if r['body']['type'] == 'payment.created':
            payment_id = ""
            customer_id = ""
            container_id =""
            merchant_id = r['body']['merchant_id']
            if 'id' in r['body']['data']:
                payment_id = r['body']['data']['id']
            if  'customer_id' in r['body']['data']['object']['payment'] :
                customer_id = r['body']['data']['object']['payment']['customer_id']
            if 'note' in r['body']['data']['object']['payment']:
                container_id = r['body']['data']['object']['payment']['note']
            
            supabase.table("container_transaction").insert({'merchant_id': merchant_id,'payment_id' : payment_id,
                'customer_id' : customer_id,
                'container_id' : container_id,
                'status' : 'New'}).execute()
            supabase.table('webhook_listener').update({'processed': 'done'}).eq('id',r['id']).execute()

data1, count1 = supabase.table('webhook_listener').update({'processed': 'done'}).neq('processed','done').execute()
if selected_page == "Containers":
#     # View all the distributed containers 
#     # Mark a container Recieved 
#     # Or Mark a container Not Recieved
    
#     # Add a button to charge back for container not recieved
#     # On creating charge back, change all status to Recieved
#     # Get container id and store it in a table 
    data,count = supabase.table("container_transaction").select('*').execute()
    x = data[1]
    st.table(x)

    container_id = st.text_input("Enter the Container Number Returned:")
    if st.button("Submit"):
        supabase.table('container_transaction').update({'status': 'Returned'}).eq('container_id',container_id).execute()
        st.write("Container Marked Returned")
        st.experimental_rerun()
    customer_id = st.text_input("Enter the Customer ID to be charged:")
    
    
    if st.button("Charge Back"):
        random_uuid = uuid.uuid4()

        uuid_str = str(random_uuid)
        url = "https://connect.squareupsandbox.com/v2/payments"

        payload = json.dumps({
        "amount_money": {
            "currency": "USD",
            "amount": 5
        },
        "idempotency_key":uuid_str,
        "source_id": "ccof:customer-card-id-ok",
        "accept_partial_authorization": True,
        "autocomplete": False,
        "customer_details": {
            "customer_initiated": False,
            "seller_keyed_in": True
        },
        "customer_id": customer_id,
        })
        headers = {
        'Square-Version': '2023-10-18',
        'Authorization': 'Bearer EAAAEI8s4HH7l_c3MaQQyKzs1pUzJBVh8Ecltg6jVpotispTElb1esm-zE2cqO5f',
        'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        st.write("Customer was charged")
        st.write(response.text)
        supabase.table('container_transaction').update({'status': 'Charged'}).eq('customer_id',customer_id).execute()

# if selected_page == "Customers":
#     # View the Customers Charged and the corresponding containers
    
