import requests

def test_get_standard_svg_lap(server, pass_code, device_access_code, svg_file_path, json_file_path, output_file_path, workspace_width_mm=0, workspace_height_mm=0):
    """
    Test the standard-svg-lap endpoint.

    Args:
        server (str): The server URL.
        pass_code (str): Pass code for authentication.
        device_access_code (str): Device access code for authentication.
        svg_file_path (str): Path to the svg file.
        json_file_path (str): Path to the JSON file.
        output_file_path (str): Path to save the output file.
    """
    try:
        url = server + "/api/jobs/standard-svg-lap"

        # Open the files to upload
        with open(svg_file_path, "rb") as svg_file, open(json_file_path, "rb") as json_file:
            # Prepare the data and files for the POST request
            data = {
                "pass_code": pass_code,
                "device_access_code": device_access_code,
                "workspace_width_mm": workspace_width_mm,
                "workspace_height_mm": workspace_height_mm,
            }
            files = {
                "svg_file": svg_file,
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
    server = "https://beta.fslaser.com"  # Replace with your server URL
    pass_code = "Pork_Hacking_98" #Pass code for authentication. -> get the user passcode from the website
    device_access_code = "Chastity:Lasso:87" #Device access code for device authentication. -> get the device access code from the device touchscreen
    svg_file_path = "test.svg"  # Path to a sample SVG file
    json_file_path = "color_settings.json"  # Path to a sample JSON file
    output_file_path = "output_standard_svg.lap"
    # Optional: Set workspace size
    workspace_width_mm = 100
    workspace_height_mm = 100
    test_get_standard_svg_lap(
        server=server,
        pass_code=pass_code,
        device_access_code=device_access_code,
        svg_file_path=svg_file_path,
        json_file_path=json_file_path,
        output_file_path=output_file_path,
        workspace_width_mm=workspace_width_mm,
        workspace_height_mm=workspace_height_mm
    )
