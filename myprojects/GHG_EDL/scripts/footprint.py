# File of data for the GHG Footprint BlockChain Project
# Data is stored in a dictionary with the key being the name of the data and the value being the data itself
# The data is stored in a nested dictionary with the first key being the company name and the second key being the product name
# The value of the product key is a dictionary with the first key being the description of the product
# and the second key value being a list of the GHG Footprints stored as dictionaries.

data = {
    "Company A": {
        "Product1": {
            "description": {
                "owner_name": "Company A",
                "productID": "1",
                "product_name": "Heat Pump",
                "product_type": "Consumer",
                "units": "Unit",
                "date_created": "22/10/2024",
                "date_updated": "",
                "status": "Active",
            },
            "GHG_Footprints": [
                {
                    "GHGFootPrint_ID": 1000,
                    "GHGFootPrint_scope": 1,
                    "GHGFootPrint_disaggregation": 0,
                    "GHGFootPrint_category": "Gross Scope 1 greenhouse gas emissions",
                    "GHGFootprint_value": 1000,
                },
                {
                    "GHGFootPrint_ID": 1001,
                    "GHGFootPrint_scope": 2,
                    "GHGFootPrint_disaggregation": 1,
                    "GHGFootPrint_category": "Gross location based Scope 2 greenhouse gas emissions",
                    "GHGFootprint_value": 300,
                },
                {
                    "GHGFootPrint_ID": 1002,
                    "GHGFootPrint_scope": 2,
                    "GHGFootPrint_disaggregation": 1,
                    "GHGFootPrint_category": "Gross market based Scope 2 greenhouse gas emissions",
                    "GHGFootprint_value": 300,
                },
                {
                    "GHGFootPrint_ID": 1003,
                    "GHGFootPrint_scope": 3,
                    "GHGFootPrint_disaggregation": 0,
                    "GHGFootPrint_category": "Total indirect Scope 3 greenhouse gas emissions",
                    "GHGFootprint_value": 2300,
                },
                {
                    "GHGFootPrint_ID": 1004,
                    "GHGFootPrint_scope": 3,
                    "GHGFootPrint_disaggregation": 1,
                    "GHGFootPrint_category": "Purchased Goods and services",
                    "GHGFootprint_value": 1300,
                },
                {
                    "GHGFootPrint_ID": 1005,
                    "GHGFootPrint_scope": 3,
                    "GHGFootPrint_disaggregation": 2,
                    "GHGFootPrint_category": "Purchased Goods and services",
                    "GHGFootprint_supplier": "Company B",
                    "GHGFootprint_no_units": 1,
                    "GHGFootprint_linked_product": "Product1",
                    "GHGFootprint_IDs": [1000, 1002, 1004, 1005],
                },
                {
                    "GHGFootPrint_ID": 1006,
                    "GHGFootPrint_scope": 3,
                    "GHGFootPrint_disaggregation": 1,
                    "GHGFootPrint_category": "Downstream transportation and distribution",
                    "GHGFootprint_value": 1000,
                },
            ],
        },
    },
    "Company B": {
        "Product1": {
            "description": {
                "owner_name": "Company B",
                "productID": "1",
                "product_name": "Pump",
                "product_type": "Business",
                "units": "Unit",
                "date_created": "22/10/2024",
                "date_updated": "",
                "status": "Active",
            },
            "GHG_Footprints": [
                {
                    "GHGFootPrint_ID": 1000,
                    "GHGFootPrint_scope": 1,
                    "GHGFootPrint_disaggregation": 0,
                    "GHGFootPrint_category": "Gross Scope 1 greenhouse gas emissions",
                    "GHGFootprint_value": 300,
                },
                {
                    "GHGFootPrint_ID": 1001,
                    "GHGFootPrint_scope": 2,
                    "GHGFootPrint_disaggregation": 1,
                    "GHGFootPrint_category": "Gross location based Scope 2 greenhouse gas emissions",
                    "GHGFootprint_value": 50,
                },
                {
                    "GHGFootPrint_ID": 1002,
                    "GHGFootPrint_scope": 2,
                    "GHGFootPrint_disaggregation": 1,
                    "GHGFootPrint_category": "Gross market based Scope 2 greenhouse gas emissions",
                    "GHGFootprint_value": 30,
                },
                {
                    "GHGFootPrint_ID": 1003,
                    "GHGFootPrint_scope": 3,
                    "GHGFootPrint_disaggregation": 0,
                    "GHGFootPrint_category": "Total indirect Scope 3 greenhouse gas emissions",
                    "GHGFootprint_value": 60,
                },
                {
                    "GHGFootPrint_ID": 1004,
                    "GHGFootPrint_scope": 3,
                    "GHGFootPrint_disaggregation": 1,
                    "GHGFootPrint_category": "Purchased Goods and services",
                    "GHGFootprint_value": 40,
                },
                {
                    "GHGFootPrint_ID": 1005,
                    "GHGFootPrint_scope": 3,
                    "GHGFootPrint_disaggregation": 1,
                    "GHGFootPrint_category": "Downstream transportation and distribution",
                    "GHGFootprint_value": 20,
                },
                {
                    "GHGFootPrint_ID": 1006,
                    "GHGFootPrint_scope": 3,
                    "GHGFootPrint_disaggregation": 1,
                    "GHGFootPrint_category": "Product usage",
                    "GHGFootprint_value": 50,
                },
            ],
        },
    },
}
