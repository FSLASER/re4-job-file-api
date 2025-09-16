import requests

def test_gvdesign_lap(server, pass_code, device_id, gvdesign_file_path, json_file_path, output_file_path, auth_code=None, workspaceX_mm_min=0, workspaceX_mm_max=0, workspaceY_mm_min=0, workspaceY_mm_max=0):
    """
    Test the full-svg-lap endpoint.

    Args:
        server (str): The server URL.
        pass_code (str): Pass code for authentication.
        device_id (str): Device ID for authentication.
        auth_code (str, optional): Device authentication code. If not provided, will be omitted (for same-network requests).
        gvdesign_file_path (str): Path to the gvdesign file.
        json_file_path (str): Path to the JSON file.
        output_file_path (str): Path to save the output file.
    """
    try:
        url = server + "/api/jobs/standard-gvdesign-lap"

        # Open the files to upload
        with open(gvdesign_file_path, "rb") as gvdesign_file, open(json_file_path, "rb") as json_file:
            # Prepare the data and files for the POST request
            data = {
                "pass_code": pass_code,
                "device_id": device_id,
                "workspaceX_mm_min": workspaceX_mm_min,
                "workspaceX_mm_max": workspaceX_mm_max,
                "workspaceY_mm_min": workspaceY_mm_min,
                "workspaceY_mm_max": workspaceY_mm_max,
            }
            
            # Only include auth_code if provided
            if auth_code:
                data["device_auth_code"] = auth_code
            files = {
                "gvdesign_file": gvdesign_file,
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
    device_id = "AE356O3E89D" #Device ID for device authentication.
    gvdesign_file_path = "test2.gvdesign"  # Path to a sample SVG file
    json_file_path = "color_settings.json"  # Path to a sample JSON file
    output_file_path = "output_gvdesign.lap"
    # Optional: Set workspace size
    workspaceX_mm_min = -50
    workspaceX_mm_max = 50
    workspaceY_mm_min = -50
    workspaceY_mm_max = 50
    # Option 1: Same network - no auth code needed
    print("Testing without auth code (same network)...")
    test_gvdesign_lap(
        server=server,
        pass_code=pass_code,
        device_id=device_id,
        gvdesign_file_path=gvdesign_file_path,
        json_file_path=json_file_path,
        output_file_path=output_file_path,
        workspaceX_mm_min=workspaceX_mm_min,
        workspaceX_mm_max=workspaceX_mm_max,
        workspaceY_mm_min=workspaceY_mm_min,
        workspaceY_mm_max=workspaceY_mm_max
    )
    
    # Option 2: Using TOTP auth code (uncomment if needed)
    # from auth_code_grabber import get_device_auth_code
    # print("Testing with auth code (TOTP)...")
    # try:
    #     device_ip = "192.168.1.100"  # Define device IP only when using TOTP
    #     auth_code = get_device_auth_code(device_ip)
    #     test_gvdesign_lap(
    #         server=server,
    #         pass_code=pass_code,
    #         device_id=device_id,
    #         gvdesign_file_path=gvdesign_file_path,
    #         json_file_path=json_file_path,
    #         output_file_path="output_gvdesign_with_totp.lap",
    #         auth_code=auth_code,
    #         workspaceX_mm_min=workspaceX_mm_min,
    #         workspaceX_mm_max=workspaceX_mm_max,
    #         workspaceY_mm_min=workspaceY_mm_min,
    #         workspaceY_mm_max=workspaceY_mm_max
    #     )
    # except Exception as e:
    #     print(f"Could not use TOTP authentication: {e}")
