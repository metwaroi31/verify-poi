import csv
import requests
import time

class POIReader:
    def __init__(self, api_key, base_url, radius, place_type):
        """
        Initialize POIReader with API parameters and search configuration.
        """
        self.api_key = api_key
        self.base_url = base_url
        self.radius = radius
        self.place_type = place_type

    def read_coordinates_from_csv(self, file_path):
        """
        Read a list of coordinates from a CSV file.
        """
        coordinates = []
        try:
            with open(file_path, mode="r") as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    coordinates.append({"lat": float(row["lat"]), "lon": float(row["lon"])})
            return coordinates
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            return []


    def nearby_search(self, lat, lon):
        """
        Perform Nearby Search for a given coordinate, returning the result as JSON.
        """
        params = {
            "key": self.api_key,
            "location": f"{lat},{lon}",
            "radius": self.radius,
            "types": self.place_type,
        }
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error making Nearby Search request: {e}")
            return None

    def write_poi_to_csv(self, output_path, results):
        """
        Write Nearby Search results to a CSV file.
        """
        header = ["source_lat", "source_lon", "poi_name", "poi_lat", "poi_lon", "poi_type", "distance"]

        try:
            with open(output_path, mode="w", newline="", encoding="utf-8-sig") as file:
                writer = csv.writer(file)
                writer.writerow(header)

                for result in results:
                    source_lat = result["lat"]
                    source_lon = result["lon"]
                    nearby = result.get("nearby", {})
                    nearby_results = nearby.get("result", [])
                    code = nearby.get("code", "error")

                    if not nearby_results and code == "ok":
                        writer.writerow([source_lat, source_lon, None, None, None, None, None])
                        continue

                    for poi in nearby_results:
                        name = poi.get("name", None)
                        location = poi.get("location", {})
                        poi_lat = location.get("lat", None)
                        poi_lon = location.get("lon", None)  
                        poi_type = poi.get("types", [None])[0]  
                        row = [source_lat, source_lon, name, poi_lat, poi_lon, poi_type, None]  # Distance not yet calculated
                        writer.writerow(row)
            print(f"Results have been saved to:  {output_path}")
        except Exception as e:
            print(f"Error writing to CSV file:{e}")

    def process(self, input_csv, output_csv, batch_size=200):
        """
        Read coordinates from a CSV file, perform Nearby Search, and save results to a CSV file.
        """
        coordinates = self.read_coordinates_from_csv(input_csv)
        if not coordinates:
            print("No valid coordinates to process.")
            return []

        results = []

        for i in range(0, len(coordinates), batch_size):
            batch = coordinates[i:i + batch_size]
            for coord in batch:
                print(f"Performing nearby search for coordinate: {coord['lat']}, {coord['lon']}")
                result = self.nearby_search(coord["lat"], coord["lon"])
                if result:
                    results.append({"coordinate": coord, "nearby": result})
                time.sleep(1)  # Avoid sending too many requests in quick succession

            print(f"Nearby Search results for batch {i // batch_size + 1}:")
            for res in results[-len(batch):]:  #  Print results for the current batch
                print(res)

            user_input = input("Do you want to continue with the next batch? (y/n): ").strip().lower()
            if user_input != "y":
                break

        self.write_poi_to_csv(output_csv, results)
        return results


# Ví dụ sử dụng:
# Thay YOUR_API_KEY bằng khóa API thật.
# processor = POIProcessor(api_key="YOUR_API_KEY", base_url="https://api.map4d.vn/sdk/place/nearby-search", radius=10, place_type="point")
# processor.process("input.csv", "output.csv")
