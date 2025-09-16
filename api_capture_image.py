import requests
import shutil

# --- Configuration ---
BASE_URL = "https://beta.fslaser.com/api/jobs"  # Replace with your actual server URL
DEVICE_ID = "AE356O3E89D"  # Replace with a valid device ID
PASS_CODE = "Pork_Hacking_98"  # Replace with a valid pass code
# --- End Configuration ---

def test_capture_image(is_corrected_value=None, output_filename="captured_image.jpg", auth_code=None):
    """
    Tests the /api/jobs/capture-image endpoint.

    Args:
        is_corrected_value (bool, optional): Whether the captured image is corrected using calibrated homography data.
        output_filename (str): Name of the file to save the captured image.
        auth_code (str, optional): Device authentication code. If not provided, will be omitted (for same-network requests).
    """
    endpoint = f"{BASE_URL}/capture-image"
    
    form_data = {
        "device_id": DEVICE_ID,
        "pass_code": PASS_CODE,
    }
    
    # Only include auth_code if provided
    if auth_code:
        form_data["device_auth_code"] = auth_code

    if is_corrected_value is not None:
        form_data["is_corrected"] = str(is_corrected_value).lower() # FastAPI expects 'true' or 'false' for bools in Form

    print(f"\nAttempting to capture image with is_corrected={is_corrected_value if is_corrected_value is not None else 'Default (False)'}...")
    print(f"Endpoint: {endpoint}")
    print(f"Form data: {form_data}")

    try:
        response = requests.post(endpoint, data=form_data, stream=True)

        print(f"Status Code: {response.status_code}")
        print(f"Headers: {response.headers}")

        if response.status_code == 200 and response.headers.get("content-type") == "image/jpeg":
            with open(output_filename, "wb") as f:
                response.raw.decode_content = True # Ensure content is de-gzipped if necessary
                shutil.copyfileobj(response.raw, f)
            print(f"Image successfully captured and saved to '{output_filename}'")
        elif response.headers.get("content-type") == "application/json":
            print("Error response (JSON):")
            try:
                print(response.json())
            except requests.exceptions.JSONDecodeError:
                print("Could not decode JSON response.")
                print(f"Raw content: {response.text}")
        else:
            print("Unexpected response format or error.")
            print(f"Raw content: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the request: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    # --- Test Cases ---
    
    # Option 1: Same network - no auth code needed
    print("Testing without auth code (same network)...")
    test_capture_image(is_corrected_value=True, output_filename="captured_image_corrected.jpg")
    test_capture_image(is_corrected_value=False, output_filename="captured_image_uncorrected.jpg")
    test_capture_image(output_filename="captured_image_default.jpg")
    
    # Option 2: Using TOTP auth code (uncomment if needed)
    # from auth_code_grabber import get_device_auth_code
    # print("Testing with auth code (TOTP)...")
    # try:
    #     device_ip = "192.168.1.100"  # Define device IP only when using TOTP
    #     auth_code = get_device_auth_code(device_ip)
    #     test_capture_image(is_corrected_value=True, output_filename="captured_image_corrected_with_totp.jpg", auth_code=auth_code)
    # except Exception as e:
    #     print(f"Could not use TOTP authentication: {e}")

    print("\n--- All tests finished ---")
    