import requests

def test_run_lap_job(server, pass_code, device_access_code, lap_file_path, soft_limit_check):
    """
    Test the api-run-lap-job endpoint.

    Args:
        server (str): The server URL.
        pass_code (str): Pass code for authentication.
        device_access_code (str): Device access code for authentication.
    """
    try:
        url = server + "/api/jobs/api-run-lap-job"

        # Prepare the data and files for the POST request
        data = {
            "pass_code": pass_code,
            "device_access_code": device_access_code,
            "soft_limit_check": soft_limit_check,
        }
        
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
    device_access_code = "Chastity:Lasso:87" #Device access code for device authentication. -> get the device access code from the device touchscreen
    lap_file_path = "C:/Users/Administrator/Desktop/test.lap" #Path to the LAP file to be uploaded
    soft_limit_check = True
    test_run_lap_job(server, pass_code, device_access_code, lap_file_path, soft_limit_check)
