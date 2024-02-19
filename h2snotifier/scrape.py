import logging

import requests
import json


# Define the GraphQL query payload
def scrape(cities=[], page_size=30):
    payload = {
        "operationName": "GetCategories",
        "variables": {
            "currentPage": 1,
            "id": "Nw==",
            "filters": {
                "available_to_book": {"in": ["179", "336"]},
                "city": {"in": cities},
                "category_uid": {"eq": "Nw=="},
            },
            "pageSize": page_size,
            "sort": {"available_startdate": "ASC"},
        },
        "query": """
            query GetCategories($id: String!, $pageSize: Int!, $currentPage: Int!, $filters: ProductAttributeFilterInput!, $sort: ProductAttributeSortInput) {
              categories(filters: {category_uid: {in: [$id]}}) {
                items {
                  uid
                  ...CategoryFragment
                  __typename
                }
                __typename
              }
              products(
                pageSize: $pageSize
                currentPage: $currentPage
                filter: $filters
                sort: $sort
              ) {
                ...ProductsFragment
                __typename
              }
            }
    
            fragment CategoryFragment on CategoryTree {
              uid
              meta_title
              meta_keywords
              meta_description
              __typename
            }
    
            fragment ProductsFragment on Products {
              items {
                name
                sku
                city
                url_key
                available_to_book
                available_startdate
                building_name
                finishing
                living_area
                no_of_rooms
                resident_type
                offer_text_two
                offer_text
                maximum_number_of_persons
                type_of_contract
                price_analysis_text
                allowance_price
                floor
                basic_rent
                lumpsum_service_charge
                inventory
                caretaker_costs
                cleaning_common_areas
                energy_common_areas
                allowance_price
                small_image {
                  url
                  label
                  position
                  disabled
                  __typename
                }
                thumbnail {
                  url
                  label
                  position
                  disabled
                  __typename
                }
                image {
                  url
                  label
                  position
                  disabled
                  __typename
                }
                media_gallery {
                  url
                  label
                  position
                  disabled
                  __typename
                }
                price_range {
                  minimum_price {
                    regular_price {
                      value
                      currency
                      __typename
                    }
                    final_price {
                      value
                      currency
                      __typename
                    }
                    discount {
                      amount_off
                      percent_off
                      __typename
                    }
                    __typename
                  }
                  maximum_price {
                    regular_price {
                      value
                      currency
                      __typename
                    }
                    final_price {
                      value
                      currency
                      __typename
                    }
                    discount {
                      amount_off
                      percent_off
                      __typename
                    }
                    __typename
                  }
                  __typename
                }
                __typename
              }
              page_info {
                total_pages
                __typename
              }
              total_count
              __typename
            }
        """,
    }
    # Send POST request to the GraphQL endpoint
    response = requests.post("https://api.holland2stay.com/graphql/", json=payload)
    data = response.json()["data"]
    cities_dict = {}
    for c in cities:
        cities_dict[c] = []
    for house in data["products"]["items"]:
        city_id = str(house["city"])
        try:
            cities_dict[city_id].append(
                {
                    "url_key": house["url_key"],
                    "city": str(house["city"]),
                    "area": str(house["living_area"]),
                    "price_exc": str(house["basic_rent"]),
                    "price_inc": str(
                        house["price_range"]["maximum_price"]["final_price"]["value"]
                    ),
                    "available_from": house["available_startdate"],
                    "max_register": str(
                        max_register_id_to_str(str(house["maximum_number_of_persons"])),
                    ),
                    "contract_type": contract_type_id_to_str(
                        str(house["type_of_contract"])
                    ),
                    "rooms": room_id_to_room(str(house["no_of_rooms"])),
                }
            )
        except Exception as err:
            logging.error("Error in parsing house")
            logging.error(house)
    return cities_dict


def city_id_to_city(city_id):
    return {
        "24": "Amsterdam",
        "320": "Arnhem",
        "619": "Capelle aan den IJssel",
        "26": "Delft",
        "28": "Den Bosch",
        "90": "Den Haag",
        "110": "Diemen",
        "620": "Dordrecht",
        "29": "Eindhoven",
        "545": "Groningen",
        "616": "Haarlem",
        "6099": "Helmond",
        "6209": "Maarssen",
        "6090": "Maastricht",
        "6051": "Nieuwegein",
        "6217": "Nijmegen",
        "25": "Rotterdam",
        "6224": "Rijswijk",
        "6211": "Sittard",
        "6093": "Tilburg",
        "27": "Utrecht",
        "6145": "Zeist",
        "6088": "Zoetermeer",
    }.get(city_id)


def contract_type_id_to_str(contract_type_id):
    mapping = {
        "21": "Indefinite",
        "6125": "2 years",
        "20": "1 year max",
        "318": "6 months max",
        "606": "4 months max",
    }
    return mapping.get(contract_type_id, "Unknown")


def room_id_to_room(room_id):
    mapping = {
        "104": "Studio",
        "6137": "Loft (open bedroom area)",
        "105": "1",
        "106": "2",
        "108": "3",
        "382": "4",
    }
    return mapping.get(room_id, "Unknown")


def max_register_id_to_str(maxregister_id):
    mapping = {
        "22": "One",
        "23": "Two (only couples)",
        "500": "Two",
        "380": "Family (parents with children)",
        "501": "Three",
        "502": "Four",
    }
    return mapping.get(maxregister_id, "Unknown")


def url_key_to_link(url_key):
    return f"https://holland2stay.com/residences/{url_key}.html"


def house_to_msg(house):
    return f"""
New house in #{city_id_to_city(house['city'])}!
{url_key_to_link(house['url_key'])}
Area: {house['area']}m2
Final price: {house['price_inc']:3,}💶 (Basic rent: {house['price_exc']:3,}💶)

Available from: {house['available_from']}
Bedrooms: {house['rooms']}
Max occupancy: {house['max_register']}
Contract type: {house['contract_type']}


Make sure to check everything before apply on Holland2Stay website before apply!
    """.strip()
