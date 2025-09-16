import requests

def test_run_lap_job(server, pass_code, device_id, lap_file_path, soft_limit_check, auth_code=None):
    """
    Test the api-run-lap-job endpoint.

    Args:
        server (str): The server URL.
        pass_code (str): Pass code for authentication.
        device_id (str): Device ID for authentication.
        auth_code (str, optional): Device authentication code. If not provided, will be omitted (for same-network requests).
    """
    try:
        url = server + "/api/jobs/api-run-lap-job"

        # Prepare the data and files for the POST request
        data = {
            "pass_code": pass_code,
            "device_id": device_id,
            "soft_limit_check": soft_limit_check,
        }
        
        # Only include auth_code if provided
        if auth_code:
            data["device_auth_code"] = auth_code
        
        # Open and prepare the LAP file
        files = {
            "lap_file": open(lap_file_path, "rb")
        }

        # Send the POST request
        print(f"Sending request to {url}...")
        response = requests.post(url, data=data, files=files)

        # Check the response
        if response.status_code == 200:
            print(f"{response.json()}")
        else:
            print(f"Error: Received status code {response.status_code}")
            print("Response content:", response.json())

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    server = "https://beta.fslaser.com"  # Replace with your server URL
    pass_code = "Pork_Hacking_98" #Pass code for authentication. -> get the user passcode from the website
    device_id = "AE356O3E89D" #Device ID for device authentication.
    lap_file_path = "C:/Users/Administrator/Desktop/test.lap" #Path to the LAP file to be uploaded
    soft_limit_check = True
    
    # Option 1: Same network - no auth code needed
    print("Testing without auth code (same network)...")
    test_run_lap_job(server, pass_code, device_id, lap_file_path, soft_limit_check)
    
    # Option 2: Using TOTP auth code (uncomment if needed)
    # from auth_code_grabber import get_device_auth_code
    # print("Testing with auth code (TOTP)...")
    # try:
    #     device_ip = "192.168.1.100"  # Define device IP only when using TOTP
    #     auth_code = get_device_auth_code(device_ip)
    #     test_run_lap_job(server, pass_code, device_id, lap_file_path, soft_limit_check, auth_code=auth_code)
    # except Exception as e:
    #     print(f"Could not use TOTP authentication: {e}")
