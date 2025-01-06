from process_poi.POI_Reader import POIReader
from process_poi.side_detector import (
     POIProcessor , 
     RoutePOIVisualizer
)

def main():
    # CSV,HTML input and output paths
    input_csv = "route_points.csv"
    output_csv_nearby = "./results/poi_results1.csv"
    final_output_csv = "./results/output.csv"
    html_output = "./results/route_and_poi_side_verification.html"

    # Request API-key and base URL for nearby-search
    api_key = "eaecf61a20ca4edbe1024d31d6595b71"
    base_url = "https://api.map4d.vn/sdk/place/nearby-search"

    # Step 1: Find nearby POI and save the results to a CSV file
    print("=== STEP 1: FINDING NEARBY POI ===")
    poi_reader = POIReader(api_key, base_url, radius=10, place_type="point")
    results = poi_reader.process(input_csv, output_csv_nearby)

    # Step 2: Side Detection
    print("=== STEP 2: SIDE DETECTING ===")
    side_processor = POIProcessor(results)
    side_processor.process_pois()
    side_processor.write_to_csv(final_output_csv)

    print(f"THE FINAL RESULT: {final_output_csv}")

    # Bước 3: Vẽ tuyến đường và POI lên bản đồ
    print("=== STEP 3: MAP IS BEING CREATED ===")
    visualizer = RoutePOIVisualizer(final_output_csv)
    visualizer.visualize_route_and_poi(html_output)
if __name__ == "__main__":
    main()
