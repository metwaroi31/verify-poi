import numpy as np
import csv
from sklearn.cluster import MeanShift
from fuzzywuzzy import fuzz

class POIOptimizer:
    @staticmethod
    def average_position(latitudes, longitudes):
        """
        Calculate the average position of a list of latitudes and longitudes.
        """
        avg_lat = np.mean(latitudes)
        avg_lon = np.mean(longitudes)
        return avg_lat, avg_lon

    @staticmethod
    def weighted_average_position(latitudes, longitudes, distances, epsilon=1e-5):
        """
        Calculate the weighted average position using distances as weights.
        Handle zero distances by applying a small epsilon.
        """
        weights = [1 / (d + epsilon) for d in distances]
        weighted_lat = np.sum(np.array(latitudes) * weights) / np.sum(weights)
        weighted_lon = np.sum(np.array(longitudes) * weights) / np.sum(weights)
        return weighted_lat, weighted_lon

    @staticmethod
    def geometric_median(latitudes, longitudes, max_iterations=100, tolerance=1e-5):
        """
        Calculate the geometric median of a list of latitudes and longitudes.
        Add robustness against outliers.
        """
        coords = np.array([latitudes, longitudes]).T
        median = np.mean(coords, axis=0)
        for _ in range(max_iterations):
            distances = np.linalg.norm(coords - median, axis=1)
            nonzero = distances > tolerance
            inv_distances = 1 / distances[nonzero]
            weights = inv_distances / np.sum(inv_distances)
            new_median = np.sum(weights[:, np.newaxis] * coords[nonzero], axis=0)
            if np.linalg.norm(new_median - median) < tolerance:
                return new_median
            median = new_median
        return median

    @staticmethod
    def cluster_optimized_position(latitudes, longitudes):
        coords = np.array([latitudes, longitudes]).T
        clustering = MeanShift().fit(coords)  # Sử dụng Mean Shift thay vì DBSCAN
        cluster_centers = clustering.cluster_centers_
        largest_cluster_center = cluster_centers[0]  # Lấy trung tâm của cụm lớn nhất
        return largest_cluster_center
    @staticmethod
    def calculate_average_distance(distances):
        """
        Calculate the average distance.
        """
        return np.mean(distances)

    @staticmethod
    def calculate_new_position(lat, lon, bearing, distance):
        """
        Calculate new latitude and longitude based on starting point, bearing, and distance.
        Uses haversine formula to calculate the new position.
        """
        R = 6371000  # Radius of Earth in meters
        bearing = np.radians(bearing)

        lat1 = np.radians(lat)
        lon1 = np.radians(lon)

        lat2 = np.arcsin(np.sin(lat1) * np.cos(distance / R) + np.cos(lat1) * np.sin(distance / R) * np.cos(bearing))
        lon2 = lon1 + np.arctan2(np.sin(bearing) * np.sin(distance / R) * np.cos(lat1),
                                 np.cos(distance / R) - np.sin(lat1) * np.sin(lat2))

        return np.degrees(lat2), np.degrees(lon2)

    @staticmethod
    def find_min_bearing(poi_group):
        """
        Find the point with the minimum bearing in the group.
        """
        min_bearing_point = min(poi_group, key=lambda x: x[2])  # Assuming bearing is at index 2
        return min_bearing_point
class POIOptimizationProcessor:
    def __init__(self, input_csv, output_csv_optimized):
        self.input_csv = input_csv
        self.output_csv_optimized = output_csv_optimized

    def group_similar_pois(self, poi_groups):
        """
        Merge POI groups with similar names using fuzzy matching.
        """
        merged_poi_groups = {}
        processed_names = set()

        for poi_name in poi_groups.keys():
            if poi_name in processed_names:
                continue

            merged_poi_groups[poi_name] = poi_groups[poi_name]
            processed_names.add(poi_name)

            for other_name in poi_groups.keys():
                if other_name in processed_names:
                    continue

                similarity = fuzz.ratio(poi_name.lower(), other_name.lower())
                if similarity > 85:  # Threshold for merging similar names
                    merged_poi_groups[poi_name].extend(poi_groups[other_name])
                    processed_names.add(other_name)

        return merged_poi_groups

    def optimize_poi_positions(self):
        """
        Optimize POI positions based on average distance and minimum bearing.
        """
        poi_groups = {}

        # Step 1: Read the input CSV and group POIs by name
        with open(self.input_csv, mode='r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for row in reader:
                poi_name = row['poi_name']
                if not poi_name:
                    continue

                source_lat = float(row['source_lat'])
                source_lon = float(row['source_lon'])
                poi_lat = float(row['poi_lat'])
                poi_lon = float(row['poi_lon'])
                distance = float(row['distance'])
                bearing = float(row['bearing'])
                side = row['side'].lower()
              # In giá trị 'side'
                if side != 'right':
                    continue
                
                if poi_name not in poi_groups:
                    poi_groups[poi_name] = []

                poi_groups[poi_name].append((poi_lat, poi_lon, bearing, distance, source_lat, source_lon))

        # Step 2: Optimize positions for each group
        optimized_results = []
        for poi_name, group in poi_groups.items():
            distances = [g[3] for g in group]  # Extract distances
            average_distance = POIOptimizer.calculate_average_distance(distances)

            # Find the POI with the minimum bearing
            min_bearing_point = POIOptimizer.find_min_bearing(group)

            # Use the average distance and minimum bearing point to determine new position
            optimal_lat, optimal_lon = POIOptimizer.calculate_new_position(
                min_bearing_point[0], min_bearing_point[1], min_bearing_point[2], average_distance
            )
            # Add optimized result for each original source point
            for _, _, _, _, source_lat, source_lon in group:
                optimized_results.append([source_lat, source_lon, poi_name, optimal_lat, optimal_lon])

        # Step 3: Write optimized results to a new CSV
        with open(self.output_csv_optimized, mode='w', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file)
            header = ["source_lat", "source_lon", "poi_name", "optimal_lat", "optimal_lon"]
            writer.writerow(header)
            writer.writerows(optimized_results)

        print(f"Optimized POI positions have been saved to: {self.output_csv_optimized}")