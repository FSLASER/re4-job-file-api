import requests

def test_gantry_move(server, pass_code, device_access_code, x_mm=None, y_mm=None, z_mm=None):
    """
    Test the gantry-move endpoint.

    Args:
        server (str): The server URL.
        pass_code (str): Pass code for authentication.
        device_access_code (str): Device access code for authentication.
        x_mm (float, optional): X position in millimeters. Default is None (do not move X).
        y_mm (float, optional): Y position in millimeters. Default is None (do not move Y).
        z_mm (float, optional): Z position in millimeters. Default is None (do not move Z).
    """
    try:
        url = server + "/api/jobs/gantry-move"

        # Prepare the data for the POST request
        data = {
            "pass_code": pass_code,
            "device_access_code": device_access_code,
        }
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
    device_access_code = "Chastity:Lasso:87" #Device access code for device authentication. -> get the device access code from the device touchscreen

    # Example test cases
    print("\n--- Move X only ---")
    test_gantry_move(server, pass_code, device_access_code, x_mm=100.0)

    print("\n--- Move Y only ---")
    test_gantry_move(server, pass_code, device_access_code, y_mm=50.0)

    print("\n--- Move X and Y ---")
    test_gantry_move(server, pass_code, device_access_code, x_mm=100.0, y_mm=50.0)

    print("\n--- Move all axes ---")
    test_gantry_move(server, pass_code, device_access_code, x_mm=100.0, y_mm=50.0, z_mm=10.0)

    print("\n--- No axes (should fail) ---")
    test_gantry_move(server, pass_code, device_access_code)
