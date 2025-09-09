import requests

def test_stop_job(server, pass_code, device_id, device_ip):
    """
    Test the api-stop-job endpoint.

    Args:
        server (str): The server URL.
        pass_code (str): Pass code for authentication.
        device_id (str): Device ID for authentication.
        device_ip (str): Device IP for authentication.
    """
    try:
        url = server + "/api/jobs/api-stop-job"

        # get the device auth code from the {device_ip}/2fa
        # Note: Both HTTP and HTTPS work, but HTTPS requires verify=False to disable SSL verification
        totp_response = requests.post(f"https://{device_ip}/2fa", verify=False).json()
        if not totp_response.get("success"):
            raise Exception(f"Failed to get TOTP: {totp_response}")
        device_auth_code = totp_response["totp"]["totp"]
        # Prepare the data and files for the POST request
        data = {
            "pass_code": pass_code,
            "device_id": device_id,
            "device_auth_code": device_auth_code,
        }

        # Send the POST request
        print(f"Sending request to {url}...")
        response = requests.post(url, data=data)

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
    device_ip = "192.168.1.100" #Device IP for device authentication.
    test_stop_job(server, pass_code, device_id, device_ip)
