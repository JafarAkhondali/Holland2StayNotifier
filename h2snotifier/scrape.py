import logging

import requests

from dotenv import dotenv_values
from telegram import TelegramBot

env = dotenv_values(".env")
TELEGRAM_API_KEY = env.get("TELEGRAM_API_KEY")
DEBUGGING_CHAT_ID = env.get("DEBUGGING_CHAT_ID")

debug_telegram = TelegramBot(apikey=TELEGRAM_API_KEY, chat_id=DEBUGGING_CHAT_ID)


def generate_payload(cities, page_size):
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
    return payload


CITY_IDS = {
    "24": "Amsterdam",
    "6249": "Amersfoort",
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
}

CONTRACT_TYPES = {
    "21": "Indefinite",
    "6125": "2 years",
    "20": "1 year max",
    "318": "6 months max",
    "606": "4 months max",
}

ROOM_TYPES = {
    "104": "Studio",
    "6137": "Loft (open bedroom area)",
    "105": "1",
    "106": "2",
    "108": "3",
    "382": "4",
}

MAX_REGISTER_TYPES = {
    "22": "One",
    "23": "Two (only couples)",
    "500": "Two",
    "380": "Family (parents with children)",
    "501": "Three",
    "502": "Four",
}


def city_id_to_city(city_id):
    # Use CITY_IDS dictionary for city lookup
    return CITY_IDS.get(city_id)


def contract_type_id_to_str(contract_type_id):
    # Use CONTRACT_TYPES dictionary for contract type lookup
    return CONTRACT_TYPES.get(contract_type_id, "Unknown")


def room_id_to_room(room_id):
    # Use ROOM_TYPES dictionary for room type lookup
    return ROOM_TYPES.get(room_id, "Unknown")


def max_register_id_to_str(maxregister_id):
    # Use MAX_REGISTER_TYPES dictionary for max occupancy lookup
    return MAX_REGISTER_TYPES.get(maxregister_id, "Unknown")


def url_key_to_link(url_key):
    return f"https://holland2stay.com/residences/{url_key}.html"


def clean_img(url):
    try:
        if 'cache' not in url:
            return url
        parts = url.split('/')
        ci = parts.index('cache')
        return '/'.join(parts[:ci] + parts[ci + 2:])
    except Exception as error:
        debug_telegram.send_simple_msg(url)
        debug_telegram.send_simple_msg(str(error))


def house_to_msg(house):
    return f"""
New house in #{city_id_to_city(house['city'])}!
{url_key_to_link(house['url_key'])}

Living area: {house['area']}m²
Price: {float(house['price_inc'].replace(',', '.')):,}€ (excl. {float(house['price_exc'].replace(',', '.')):,}€ basic rent)
Price per meter: {float(float(house['price_inc']) / float(house['area'])):.2f} €\\m²

Available from: {house['available_from']}
Bedrooms: {house['rooms']}
Max occupancy: {house['max_register']}
Contract type: {house['contract_type']}

# See details and apply on Holland2Stay website."""


# Define the GraphQL query payload
def scrape(cities=[], page_size=30):
    payload = generate_payload(cities, page_size)
    response = requests.post("https://api.holland2stay.com/graphql/", json=payload)
    data = response.json()["data"]
    cities_dict = {}
    for c in cities:
        cities_dict[c] = []
    for house in data["products"]["items"]:
        city_id = str(house["city"])
        try:
            cleaned_images = [clean_img(img['url']) for img in house['media_gallery']]

            # For now, this image is making an issue. Maybe we need to add similar images later
            cleaned_images = list(filter(lambda x: "logo-blue-1.jpg" not in x, cleaned_images))

            cities_dict[city_id].append(
                {
                    "url_key": house["url_key"],
                    "city": str(house["city"]),
                    "area": str(house["living_area"]).replace(",", "."),
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
                    "images": cleaned_images
                }
            )
        except Exception as err:
            debug_telegram.send_simple_msg(f"Error in parsing house!")
            debug_telegram.send_simple_msg(str(err))
            debug_telegram.send_simple_msg(str(house))
            logging.error("Error in parsing house")
            logging.error(str(err))
    return cities_dict
