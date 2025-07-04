import requests
import json

def test_get_project3d_png_lap(server, pass_code, device_access_code, png_file_path, json_file_path, mesh_file_path, transform_params, output_file_path):
    """
    Test the standard-png-lap endpoint.

    Args:
        server (str): The server URL.
        pass_code (str): Pass code for authentication.
        device_access_code (str): Device access code for authentication.
        png_file_path (str): Path to the PNG file.
        json_file_path (str): Path to the JSON file.
        transform_params (list): List of transformation parameters [sx, shx, shy, sy, tx, ty].
        output_file_path (str): Path to save the output file.
    """
    try:
        url = f"{server}/api/jobs/project3d-png-lap"

        # Open the files to upload
        with open(png_file_path, "rb") as png_file, open(json_file_path, "rb") as json_file, open(mesh_file_path, "rb") as mesh_file:
            # Prepare the data and files for the POST request
            data = {
                "pass_code": pass_code,
                "device_access_code": device_access_code,
                "transform_params": json.dumps(transform_params),  # Convert to JSON-like string
            }
            files = {
                "png_file": png_file,
                "json_file": json_file,
                "mesh_file": mesh_file
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
    device_access_code = "Chastity:Lasso:87" #Device access code for device authentication. -> get the device access code from the device touchscreen
    png_file_path = "test.png"  # Path to a sample PNG file
    json_file_path = "color_settings.json"  # Path to a sample JSON file
    transform_params = [0.1, 0.0, 0.0, 0.1, 0, 0]  # Example transform parameters
    mesh_file_path = "sub.obj"
    output_file_path = "output_project3d_png.lap"
    # Run the test
    test_get_project3d_png_lap(server, pass_code, device_access_code, png_file_path, json_file_path, mesh_file_path, transform_params, output_file_path)
