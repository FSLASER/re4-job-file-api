import requests

def test_stop_job(server, pass_code, device_access_code):
    """
    Test the api-stop-job endpoint.

    Args:
        server (str): The server URL.
        pass_code (str): Pass code for authentication.
        device_access_code (str): Device access code for authentication.
    """
    try:
        url = server + "/api/jobs/api-stop-job"

        # Prepare the data and files for the POST request
        data = {
            "pass_code": pass_code,
            "device_access_code": device_access_code,
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
    pass_code = "Pork_Hacking_98"
    device_access_code = "Chastity:Lasso:87"

    test_stop_job(server, pass_code, device_access_code)
