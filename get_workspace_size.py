import requests

def test_get_workspace_bounds(server, device_id):
    """
    Test the standard-svg-lap endpoint.

    Args:
        server (str): The server URL.
        pass_code (str): Pass code for authentication.
        device_id (str): Device ID for authentication.
    """
    try:
        url = server + "/api/jobs/get-workspace-bounds"

        # Open the files to upload
        # Prepare the data and files for the POST request
        data = {
            "device_id": device_id,
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
    device_id = "AE356O3E89D" #Device ID for device authentication.
    test_get_workspace_bounds(server, device_id)
