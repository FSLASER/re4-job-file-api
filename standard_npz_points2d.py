import requests

def test_get_standard_points2d_lap(server, pass_code, device_id, npz_file_path, json_file_path, output_file_path):
    """
    Test the standard-npz-points2d-lap endpoint.

    Args:
        server (str): The server URL.
        pass_code (str): Pass code for authentication.
        device_id (str): Device ID for authentication.
        npz_file_path (str): Path to the .npz file.
        json_file_path (str): Path to the JSON file.
        output_file_path (str): Path to save the output file.
    """
    try:
        url = f"{server}/api/jobs/standard-npz-points2d-lap"

        # Open the files to upload
        with open(npz_file_path, "rb") as npz_file, open(json_file_path, "rb") as json_file:
            # Prepare the data and files for the POST request
            data = {
                "pass_code": pass_code,
                "device_id": device_id,
            }
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
                print("Response content:", response.json())

    except Exception as e:
        print(f"An error occurred: {e}")

import numpy as np
from PIL import Image

def generate_npz_from_png(png_file_path, npz_file_path):
    """
    Generate an .npz file containing x and y coordinates of black pixels from a PNG file.

    Args:
        png_file_path (str): Path to the input PNG file.
        npz_file_path (str): Path to save the generated .npz file.

    Returns:
        None
    """
    try:
        # Load the image
        image = Image.open(png_file_path).convert("L")  # Convert to grayscale

        # Convert the image to a numpy array
        image_array = np.array(image)

        # Find the positions of black pixels (value == 0)
        black_pixel_positions = np.argwhere(image_array == 0)

        # Convert to (x, y) format (argwhere gives (row, col))
        points = black_pixel_positions[:, [1, 0]]  # Swap columns to get (x, y)

        # Scale down the points by 96
        points = points / 96.0
        # Save the points to an .npz file
        np.savez(npz_file_path, points=points)  #set attribute name to "points"
        print(f"Generated .npz file with {len(points)} points at '{npz_file_path}'")
    except Exception as e:
        print(f"An error occurred: {e}")
if __name__ == "__main__":
    # Define test parameters
    server = "https://beta.fslaser.com"  # Replace with your server URL
    pass_code = "Pork_Hacking_98" #Pass code for authentication. -> get the user passcode from the website
    device_id = "AE356O3E89D" #Device ID for device authentication.
    npz_file_path = "test_points.npz"  # Path to a sample .npz file
    json_file_path = "color_settings.json"  # Path to a sample JSON file
    output_file_path = "output_npz_points2d.lap"  # Path to save the LAP file

    png_file_path = "test.png"
    generate_npz_from_png(png_file_path, npz_file_path)

    # Run the test
    test_get_standard_points2d_lap(server, pass_code, device_id, npz_file_path, json_file_path, output_file_path)
