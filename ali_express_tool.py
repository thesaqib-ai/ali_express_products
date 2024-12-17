import streamlit as st
import requests
import pandas as pd
from io import BytesIO

# Streamlit UI
st.title("AliExpress Product Search")
st.write("Enter a query to search for products on AliExpress and download the results in an Excel file.")

# Input field for the query
query = st.text_input("Search Query", value="iphone")
search_button = st.button("Search")

if search_button:
    # API request setup
    url = "https://aliexpress-datahub.p.rapidapi.com/item_search_2"
    x_rapidapi_key = st.secrets["X-RAPIDAPI-KEY"]
    headers = {
        "x-rapidapi-key": x_rapidapi_key,
        "x-rapidapi-host": "aliexpress-datahub.p.rapidapi.com"
    }

    all_products = []  # List to collect data from all pages

    # Loop through 10 pages
    for page in range(1, 11):
        st.write(f"Fetching page {page}...")  # Display progress
        querystring = {"q": query, "page": str(page), "sort": "default"}

        # API request
        response = requests.get(url, headers=headers, params=querystring)

        if response.status_code == 200:
            data = response.json()

            # Extract relevant data
            result_list = data.get("result", {}).get("resultList", [])
            for item in result_list:
                product = item.get("item", {})
                all_products.append({
                    "Item ID": product.get("itemId"),
                    "Title": product.get("title"),
                    "Sales": product.get("sales"),
                    "Item URL": f"https:{product.get('itemUrl')}" if product.get("itemUrl") else None,
                    "Image URL": f"https:{product.get('image')}" if product.get("image") else None,
                    "Promotional Price": product.get("sku", {}).get("def", {}).get("promotionPrice"),
                    "Average Star Rate": product.get("averageStarRate")
                })
        else:
            st.error(f"Failed to fetch data on page {page}: {response.status_code}")
            break  # Stop fetching pages if an error occurs

    # Check if any products were fetched
    if all_products:
        # Create DataFrame
        df = pd.DataFrame(all_products)

        # Convert DataFrame to Excel in-memory
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name="Products")

        # File download
        st.success("Data fetched successfully!")
        st.download_button(
            label="Download Excel File",
            data=output.getvalue(),
            file_name=f"{query}_results.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.error("No products were fetched. Please try again.")
