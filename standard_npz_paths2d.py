import requests

def test_get_standard_paths2d_lap(server, pass_code, device_id, npz_file_path, json_file_path, color, output_file_path, auth_code=None):
    """
    Test script for the '/api/jobs/standard-npz-paths2d-lap' endpoint.

    Args:
        server (str): Server URL.
        pass_code (str): User's pass code.
        device_id (str): Device ID for authentication.
        auth_code (str, optional): Device authentication code. If not provided, will be omitted (for same-network requests).
        npz_file_path (str): Path to the input NPZ file.
        json_file_path (str): Path to the input JSON file.
        color (str): Stroke color for the vector.
        output_file_path (str): Path to save the output LAP file.
    """
    try:
        url = f"{server}/api/jobs/standard-npz-paths2d-lap"  # Endpoint URL

        # Open the files to upload
        with open(npz_file_path, "rb") as npz_file, open(json_file_path, "rb") as json_file:
            # Prepare the request data
            data = {
                "pass_code": pass_code,
                "device_id": device_id,
                "color": color,
            }
            
            # Only include auth_code if provided
            if auth_code:
                data["device_auth_code"] = auth_code
            files = {
                "npz_file": npz_file,
                "json_file": json_file,
            }

            # Send the POST request
            print(f"Sending request to {url}...")
            response = requests.post(url, data=data, files=files)

            # Check the response
            if response.status_code == 200:
                with open(output_file_path, "wb") as f:
                    f.write(response.content)
                print(f"Received LAP file. Saved to {output_file_path}")
            else:
                print(f"Error: Received status code {response.status_code}")
                try:
                    print("Response content:", response.json())
                except Exception:
                    print("Response content could not be parsed as JSON.")
                    print(response.content)

    except Exception as e:
        print(f"An error occurred: {e}")
import numpy as np

def generate_star_vectors(box_min=10, box_max=50, num_points=5, file_path="test_paths.npz"):
    """
    Generate vectors for a star shape and save them in an .npz file.

    Args:
        box_min (float): Minimum coordinate value for the bounding box.
        box_max (float): Maximum coordinate value for the bounding box.
        num_points (int): Number of star points (must be at least 5).
        file_path (str): Path to save the .npz file.

    Returns:
        None
    """
    if num_points < 5:
        raise ValueError("num_points must be at least 5 for a star shape.")
    
    # Center of the bounding box
    center_x = (box_min + box_max) / 2
    center_y = (box_min + box_max) / 2

    # Radius for the star
    outer_radius = (box_max - box_min) / 2
    inner_radius = outer_radius / 2

    # Generate points for the star
    angles = np.linspace(0, 2 * np.pi, num_points * 2, endpoint=False)
    star_points = []
    for i, angle in enumerate(angles):
        radius = outer_radius if i % 2 == 0 else inner_radius
        x = center_x + radius * np.cos(angle)
        y = center_y + radius * np.sin(angle)
        star_points.append([x, y])

    # Close the star by adding the first point at the end
    star_points.append(star_points[0])

    # Convert to numpy array
    star_path = np.array(star_points, dtype=np.float32)

    # Save the star path as an array of object type in an .npz file
    np.savez_compressed(file_path, paths=np.array([star_path], dtype=object))  #set attribute name to "paths"
    print(f"Star vectors saved to {file_path}")

if __name__ == "__main__":
    # Define the server and input parameters
    server = "https://beta.fslaser.com"  # Replace with your server URL
    pass_code = "Pork_Hacking_98" #Pass code for authentication. -> get the user passcode from the website
    device_id = "AE356O3E89D" #Device ID for device authentication.
    npz_file_path = "test_paths.npz"  # Path to a sample NPZ file
    json_file_path = "color_settings.json"  # Path to a sample JSON file
    color = "#000000"  # Example color for the vector
    output_file_path = "output_npz_paths2d.lap"

    generate_star_vectors(file_path=npz_file_path)
    
    # Option 1: Same network - no auth code needed
    print("Testing without auth code (same network)...")
    test_get_standard_paths2d_lap(server, pass_code, device_id, npz_file_path, json_file_path, color, output_file_path)
    
    # Option 2: Using TOTP auth code (uncomment if needed)
    # from auth_code_grabber import get_device_auth_code
    # print("Testing with auth code (TOTP)...")
    # try:
    #     device_ip = "192.168.1.100"  # Define device IP only when using TOTP
    #     auth_code = get_device_auth_code(device_ip)
    #     test_get_standard_paths2d_lap(server, pass_code, device_id, npz_file_path, json_file_path, color, "output_npz_paths2d_with_totp.lap", auth_code=auth_code)
    # except Exception as e:
    #     print(f"Could not use TOTP authentication: {e}")
