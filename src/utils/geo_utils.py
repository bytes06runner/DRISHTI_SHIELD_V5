def convert_pixels_to_geojson(pixel_data: list, aoi_bounds: dict, image_dims: tuple):
    
    img_height, img_width = image_dims
    
    min_lng = aoi_bounds["south_west"]["lng"]
    min_lat = aoi_bounds["south_west"]["lat"]
    max_lng = aoi_bounds["north_east"]["lng"]
    max_lat = aoi_bounds["north_east"]["lat"]
    
    span_lng = max_lng - min_lng
    span_lat = max_lat - min_lat
    
    def pixel_to_geo(px, py):
        percent_x = px / img_width
        percent_y = py / img_height
        
        lng = min_lng + (percent_x * span_lng)
        lat = max_lat - (percent_y * span_lat)
        
        return [lng, lat]

    features = []
    for item in pixel_data:
        if "bbox_pixels" not in item:
            continue
            
        x1, y1, x2, y2 = item["bbox_pixels"]
        
        center_x_pixel = (x1 + x2) / 2
        center_y_pixel = (y1 + y2) / 2
        
        [lng, lat] = pixel_to_geo(center_x_pixel, center_y_pixel)
        
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [lng, lat]
            },
            "properties": {
                "type": item.get("type", "Unknown"),
                "class": item.get("class", "Unknown"),
                "confidence": item.get("confidence", 0.0)
            }
        }
        features.append(feature)

    return {
        "type": "FeatureCollection",
        "features": features
    }


def convert_to_geojson(fused_data, image_bounds_latlng):

    (min_lat, min_lng) = image_bounds_latlng[0]
    (max_lat, max_lng) = image_bounds_latlng[1]

    img_width_pixels = 1024
    img_height_pixels = 1024

    pixel_width_geo = (max_lng - min_lng) / img_width_pixels
    pixel_height_geo = (max_lat - min_lat) / img_height_pixels

    def pixel_to_geo(px, py):
        lng = min_lng + (px * pixel_width_geo)
        lat = max_lat - (py * pixel_height_geo)
        return [lng, lat]

    features = []
    for item in fused_data:
        if "bbox_pixels" in item:
            x1, y1, x2, y2 = item["bbox_pixels"]

            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2

            [lng, lat] = pixel_to_geo(center_x, center_y)

            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [lng, lat]
                },
                "properties": {
                    "type": item.get("type"),
                    "class": item.get("class"),
                    "details": str(item)
                }
            }
            features.append(feature)

    return {
        "type": "FeatureCollection",
        "features": features
    }
