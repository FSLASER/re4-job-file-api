import requests
import json
from PIL import Image  # Add Pillow import
import math # Add math import

def test_get_standard_png_lap(server, pass_code, device_id, device_ip, png_file_path, json_file_path, transform_params, output_file_path):
    """
    Test the standard-png-lap endpoint.

    Args:
        server (str): The server URL.
        pass_code (str): Pass code for authentication.
        device_id (str): Device ID for authentication.
        device_ip (str): Device IP for authentication.
        png_file_path (str): Path to the PNG file.
        json_file_path (str): Path to the JSON file.
        transform_params (list): List of transformation parameters [sx, shx, shy, sy, tx, ty].
        output_file_path (str): Path to save the output file.
    """
    try:
        url = f"{server}/api/jobs/standard-png-lap"

        # get the device auth code from the {device_ip}/2fa
        device_auth_code = requests.get(f"http://{device_ip}/2fa").json()["totp"]
        # Open the files to upload
        with open(png_file_path, "rb") as png_file, open(json_file_path, "rb") as json_file:
            # Prepare the data and files for the POST request
            data = {
                "pass_code": pass_code,
                "device_id": device_id,
                "device_auth_code": device_auth_code,
                "transform_params": json.dumps(transform_params),  # Convert to JSON-like string
            }
            files = {
                "png_file": png_file,
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
                print("Response content:", response.json())

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    # Define test parameters
    server = "https://beta.fslaser.com"  # Replace with your server URL
    pass_code = "_your_passcode_here_" #Pass code for authentication. -> get the user passcode from the website ensure you get it from the same server above eg https://beta.fslaser.com
    device_id = "AE356O3E89D" #Device ID for device authentication.
    device_ip = "192.168.1.100" #Device IP for authentication.
    png_file_path = "test.png"  # Path to a sample PNG file
    #png_file_path = "alice.png"  # Path to a sample PNG file
    json_file_path = "color_settings.json"  # Path to a sample JSON file
    
    # Read image dimensions and DPI
    try:
        with Image.open(png_file_path) as img:
            width_px, height_px = img.size
    except FileNotFoundError:
        print(f"Error: Input PNG file not found at {png_file_path}")
        exit()
    except Exception as e:
        print(f"Error reading image properties: {e}")
        exit()

    # Convert dimensions from pixels to millimeters
    mm_per_inch = 25.4
    # Always use 96 DPI, ignore image DPI
    dpi_x, dpi_y = 96, 96 
    width_mm = width_px / dpi_x * mm_per_inch
    height_mm = height_px / dpi_y * mm_per_inch

    # Define initial scale factors
    sx_scale = 0.1
    sy_scale = 0.1

    # Debug: Print calculated dimensions
    print(f"DEBUG: Calculated dimensions (mm): width={width_mm}, height={height_mm}")

    # Calculate image center in mm
    center_x_mm = width_mm / 2
    center_y_mm = height_mm / 2

    # Define rotation angle (clockwise in degrees)
    angle_degrees = 45.0 
    angle_rad = math.radians(angle_degrees)
    cos_theta = math.cos(angle_rad)
    sin_theta = math.sin(angle_rad)

    # Calculate final transformation parameters [a, b, c, d, e, f]
    # Based on Y-UP clockwise rotation + standard centering (with empirical sign fix for f)
    
    # Linear part (Clockwise Rotation(theta) * Scaling)
    # R = [[cos, sin], [-sin, cos]], S = [[sx, 0], [0, sy]]
    # L = R * S = [[sx*cos, sy*sin], [-sx*sin, sy*cos]]
    final_a = sx_scale * cos_theta
    final_b = -sx_scale * sin_theta 
    final_c = sy_scale * sin_theta  
    final_d = sy_scale * cos_theta

    # Translation part (e, f) 
    # Map original center (W/2, H/2) to final center (0,0)
    # Using standard derivation for e, and empirically corrected sign for f
    final_e = -final_a * center_x_mm - final_c * center_y_mm 
    final_f = final_b * center_x_mm + final_d * center_y_mm # Empirically corrected sign

    transform_params = [final_a, final_b, final_c, final_d, final_e, final_f]
    output_file_path = "output_standard_png.lap"  # Path to save the LAP file

    # Run the test
    test_get_standard_png_lap(server, pass_code, device_id, device_ip, png_file_path, json_file_path, transform_params, output_file_path)
