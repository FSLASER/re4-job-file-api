import requests

def test_get_project3d_svg_lap(server, pass_code, device_id, device_ip, svg_file_path, json_file_path, mesh_file_path, output_file_path, workspaceX_mm_min=0, workspaceX_mm_max=0, workspaceY_mm_min=0, workspaceY_mm_max=0):
    """
    Test the standard-svg-lap endpoint.

    Args:
        server (str): The server URL.
        pass_code (str): Pass code for authentication.
        device_id (str): Device ID for authentication.
        device_ip (str): Device IP for authentication.
        svg_file_path (str): Path to the svg file.
        json_file_path (str): Path to the JSON file.
        output_file_path (str): Path to save the output file.
    """
    try:
        url = server + "/api/jobs/project3d-svg-lap"

        # get the device auth code from the {device_ip}/2fa
        # Note: Both HTTP and HTTPS work, but HTTPS requires verify=False to disable SSL verification
        totp_response = requests.post(f"https://{device_ip}/2fa", verify=False).json()
        if not totp_response.get("success"):
            raise Exception(f"Failed to get TOTP: {totp_response}")
        device_auth_code = totp_response["totp"]["totp"]
        # Open the files to upload
        with open(svg_file_path, "rb") as svg_file, open(json_file_path, "rb") as json_file, open(mesh_file_path, "rb") as mesh_file:
            # Prepare the data and files for the POST request
            data = {
                "pass_code": pass_code,
                "device_id": device_id,
                "device_auth_code": device_auth_code,
                "workspaceX_mm_min": workspaceX_mm_min,
                "workspaceX_mm_max": workspaceX_mm_max,
                "workspaceY_mm_min": workspaceY_mm_min,
                "workspaceY_mm_max": workspaceY_mm_max,
            }
            files = {
                "svg_file": svg_file,
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
    server = "https://beta.fslaser.com"  # Replace with your server URL
    pass_code = "Pork_Hacking_98" #Pass code for authentication. -> get the user passcode from the website
    device_id = "AE356O3E89D" #Device ID for device authentication.
    device_ip = "192.168.1.100" #Device IP for device authentication.
    svg_file_path = "test3.svg"  # Path to a sample SVG file
    json_file_path = "color_settings.json"  # Path to a sample JSON file
    mesh_file_path = "sub.obj"
    output_file_path = "output_project3d_svg.lap"
    
    # Optional: Set workspace size
    workspaceX_mm_min = -50
    workspaceX_mm_max = 50
    workspaceY_mm_min = -50
    workspaceY_mm_max = 50
    test_get_project3d_svg_lap(
        server, pass_code, device_id, device_ip, svg_file_path, 
        json_file_path, mesh_file_path, output_file_path, 
        workspaceX_mm_min=workspaceX_mm_min, 
        workspaceX_mm_max=workspaceX_mm_max,
        workspaceY_mm_min=workspaceY_mm_min,
        workspaceY_mm_max=workspaceY_mm_max
    )
