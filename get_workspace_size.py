import requests

def test_get_workspace_size(server, device_access_code):
    """
    Test the standard-svg-lap endpoint.

    Args:
        server (str): The server URL.
        pass_code (str): Pass code for authentication.
        device_access_code (str): Device access code for authentication.
    """
    try:
        url = server + "/api/jobs/get-workspace-size"

        # Open the files to upload
        # Prepare the data and files for the POST request
        data = {
            "device_access_code": device_access_code,
        }
        # Send the POST request
        print(f"Sending request to {url}...")
        response = requests.post(url, data=data)

        print(f"Error: Received status code {response.status_code}")
        print("Response content:", response.json())

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    server = "http://localhost:5005"  # Replace with your server URL
    device_access_code = "Chastity:Lasso:87" #Device access code for device authentication. -> get the device access code from the device touchscreen
    test_get_workspace_size(server, device_access_code)
