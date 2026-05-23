from tools import build_travel_context

result = build_travel_context(
    user_input="Plan a 3 day trip from Bangalore to Manali in December under 10000",
    origin="Bangalore",
    city="Manali",
    month="December",
    budget=10000
)

print("\nFINAL OUTPUT\n")

print("WEATHER:")
print(result["weather"])

print("\nRISK:")
print(result["risk"])

print("\nLOCATION:")
print(result["destination_location"])

print("\nBEST HOTELS:")
for hotel in result["hotels"]:
    print("\nName:", hotel.get("name"))
    print("Location:", hotel.get("location"))
    print("Rating:", hotel.get("rating"))
    print("Reviews:", hotel.get("reviews"))
    print("Price:", hotel.get("price_label"))
    print("Tag:", hotel.get("quality_tag"))
    print("Image URL:", hotel.get("image_url"))

print("\nMAP VIEW DATA:")
print(result["map_view"])

print("\nTRAVEL ROUTE:")
print(result["travel_route"])

print("\nTOTAL LOGS:")
print(len(result["logs"]))