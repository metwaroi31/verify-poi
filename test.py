from process_poi.side_detector import  RoutePOIVisualizer


def main():
    # CSV,HTML input and output paths
    optimized_csv = "./results/optimized_poi_positions.csv"
    html_output = "./results/route_and_poi_side_verification.html"

    print("=== STEP 4: CREATING MAP ===")
    visualizer = RoutePOIVisualizer(optimized_csv)
    visualizer.visualize_route_and_poi(html_output)


if __name__ == "__main__":
    main()
