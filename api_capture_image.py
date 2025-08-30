import requests
import shutil

# --- Configuration ---
BASE_URL = "https://beta.fslaser.com/api/jobs"  # Replace with your actual server URL
DEVICE_ID = "AE356O3E89D"  # Replace with a valid device ID
PASS_CODE = "Pork_Hacking_98"  # Replace with a valid pass code
# --- End Configuration ---

def test_capture_image(is_corrected_value=None, output_filename="captured_image.jpg"):
    """
    Tests the /api/jobs/capture-image endpoint.

    Args:
        is_corrected_value (bool, optional): Whether the captured image is corrected using calibrated homography data.
        output_filename (str): Name of the file to save the captured image.
    """
    endpoint = f"{BASE_URL}/capture-image"
    
    form_data = {
        "device_id": DEVICE_ID,
        "pass_code": PASS_CODE,
    }

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

    # 1. Test with is_corrected explicitly set to True
    test_capture_image(is_corrected_value=True, output_filename="captured_image_corrected.jpg")

    # 2. Test with is_corrected explicitly set to False
    test_capture_image(is_corrected_value=False, output_filename="captured_image_uncorrected.jpg")

    # 3. Test with is_corrected not provided (should default to False on the server)
    test_capture_image(output_filename="captured_image_default.jpg")

    print("\n--- All tests finished ---")
    