import requests

def test_gantry_move(server, pass_code, device_id, x_mm=None, y_mm=None, z_mm=None, auth_code=None):
    """
    Test the gantry-move endpoint.

    Args:
        server (str): The server URL.
        pass_code (str): Pass code for authentication.
        device_id (str): Device ID for authentication.
        auth_code (str, optional): Device authentication code. If not provided, will be omitted (for same-network requests).
        x_mm (float, optional): X position in millimeters. Default is None (do not move X).
        y_mm (float, optional): Y position in millimeters. Default is None (do not move Y).
        z_mm (float, optional): Z position in millimeters. Default is None (do not move Z).
    """
    try:
        url = server + "/api/jobs/gantry-move"

        # Prepare the data for the POST request
        data = {
            "pass_code": pass_code,
            "device_id": device_id,
        }
        
        # Only include auth_code if provided
        if auth_code:
            data["device_auth_code"] = auth_code
        if x_mm is not None:
            data["x_mm"] = str(x_mm)
        if y_mm is not None:
            data["y_mm"] = str(y_mm)
        if z_mm is not None:
            data["z_mm"] = str(z_mm)

        print(f"Sending request to {url} with data: {data}")
        response = requests.post(url, data=data)

        # Check the response
        print(f"Status code: {response.status_code}")
        try:
            print("Response:", response.json())
        except Exception:
            print("Raw response:", response.text)

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    server = "https://beta.fslaser.com"  # Replace with your server URL
    pass_code = "Pork_Hacking_98" #Pass code for authentication. -> get the user passcode from the website
    device_id = "AE356O3E89D" #Device ID for device authentication.
    # Option 1: Same network - no auth code needed
    print("Testing without auth code (same network)...")
    print("\n--- Move X only ---")
    test_gantry_move(server, pass_code, device_id, x_mm=100.0)

    print("\n--- Move Y only ---")
    test_gantry_move(server, pass_code, device_id, y_mm=50.0)

    print("\n--- Move X and Y ---")
    test_gantry_move(server, pass_code, device_id, x_mm=100.0, y_mm=50.0)

    print("\n--- Move all axes ---")
    test_gantry_move(server, pass_code, device_id, x_mm=100.0, y_mm=50.0, z_mm=10.0)

    print("\n--- No axes (should fail) ---")
    test_gantry_move(server, pass_code, device_id)
    
    # Option 2: Using TOTP auth code (uncomment if needed)
    # from auth_code_grabber import get_device_auth_code
    # print("Testing with auth code (TOTP)...")
    # try:
    #     device_ip = "192.168.1.100"  # Define device IP only when using TOTP
    #     auth_code = get_device_auth_code(device_ip)
    #     print("\n--- Move X only (with TOTP) ---")
    #     test_gantry_move(server, pass_code, device_id, x_mm=100.0, auth_code=auth_code)
    # except Exception as e:
    #     print(f"Could not use TOTP authentication: {e}")
