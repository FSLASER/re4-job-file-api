import requests
import json

def test_get_standard_png_lap(server, pass_code, device_id, png_file_path, json_file_path, transform_params, output_file_path, auth_code=None):
    """
    Test the standard-png-lap endpoint.

    Args:
        server (str): The server URL.
        pass_code (str): Pass code for authentication.
        device_id (str): Device ID for authentication.
        png_file_path (str): Path to the PNG file.
        json_file_path (str): Path to the JSON file.
        transform_params (list): List of transformation parameters [sx, shx, shy, sy, tx, ty].
        output_file_path (str): Path to save the output file.
        auth_code (str, optional): Device authentication code. If not provided, will be omitted (for same-network requests).
    """
    try:
        url = f"{server}/api/jobs/standard-png-lap"
        # Open the files to upload
        with open(png_file_path, "rb") as png_file, open(json_file_path, "rb") as json_file:
            # Prepare the data and files for the POST request
            data = {
                "pass_code": pass_code,
                "device_id": device_id,
                "transform_params": json.dumps(transform_params),  # Convert to JSON-like string
            }
            
            # Only include auth_code if provided
            if auth_code:
                data["device_auth_code"] = auth_code
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
    pass_code = "Pork_Hacking_98" #Pass code for authentication. -> get the user passcode from the website
    device_id = "AE356O3E89D" #Device ID for device authentication.
    png_file_path = "test.png"  # Path to a sample PNG file
    json_file_path = "color_settings.json"  # Path to a sample JSON file
    transform_params = [0.1, 0.0, 0.0, 0.1, 20.0, 15.25]  # Example transform parameters
    output_file_path = "output_standard_png.lap"  # Path to save the LAP file

    # Option 1: Same network - no auth code needed
    print("Testing without auth code (same network)...")
    test_get_standard_png_lap(server, pass_code, device_id, png_file_path, json_file_path, transform_params, output_file_path)
    
    # Option 2: Using TOTP auth code (uncomment if needed)
    # from auth_code_grabber import get_device_auth_code
    # print("Testing with auth code (TOTP)...")
    # try:
    #     device_ip = "192.168.1.100"  # Define device IP only when using TOTP
    #     auth_code = get_device_auth_code(device_ip)
    #     test_get_standard_png_lap(server, pass_code, device_id, png_file_path, json_file_path, transform_params, "output_standard_png_with_totp.lap", auth_code=auth_code)
    # except Exception as e:
    #     print(f"Could not use TOTP authentication: {e}")
