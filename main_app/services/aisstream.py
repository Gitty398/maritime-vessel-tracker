# import os
# import django
# import json
# import asyncio
# import websockets
# from django.conf import settings

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "maritime_vessel_tracker.settings")
# django.setup()

# BASE_URL = "wss://stream.aisstream.io/v0/stream"

# async def vessels_in_bbox(lat_min, lat_max, lon_min, lon_max):

#     subscription = {
#         "APIKey": settings.AISSTREAM_API_KEY,
#         "BoundingBoxes": [
#             [[lat_min, lon_min], [lat_max, lon_max]]
#         ],
#         "FilterMessageTypes": ["PositionReport"]
#     }

#     async with websockets.connect(BASE_URL) as websocket:

#         await websocket.send(json.dumps(subscription))

#         print("Connected to AISStream\n")

#         while True:
#             response = await websocket.recv()
#             data = json.loads(response)

#             print(data)

# async def updated_vessel_location(mmsi):

#     subscription = {
#         "APIKey": settings.AISSTREAM_API_KEY,
#         "FiltersShipMMSI": [mmsi],
#         "FilterMessageTypes": ["PositionReport"]
#     }

#     async with websockets.connect(BASE_URL) as websocket:

#         await websocket.send(json.dumps(subscription))

#         print(f"Tracking vessel {mmsi}\n")

#         while True:
#             response = await websocket.recv()
#             data = json.loads(response)

#             print(data)


# if __name__ == "__main__":
#     asyncio.run(vessels_in_bbox(25.6, 25.8, -80.2, -79.8))