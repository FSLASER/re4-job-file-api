import requests
import shutil

# --- Configuration ---
BASE_URL = "https://beta.fslaser.com/api/jobs"  # Replace with your actual server URL
DEVICE_ACCESS_CODE = "Chastity:Lasso:87"  # Replace with a valid device access code
PASS_CODE = "Pork_Hacking_98"  # Replace with a valid pass code
# --- End Configuration ---

def test_set_gpio(gpio_pin: int):
    """
    Tests the /api/jobs/set-gpio endpoint.

    Args:
        gpio_pin (int): The GPIO pin to set.
    """
    endpoint = f"{BASE_URL}/set-gpio"
    
    form_data = {
        "device_access_code": DEVICE_ACCESS_CODE,
        "pass_code": PASS_CODE,
    }

    if gpio_pin is not None:
        form_data["gpio_pin"] = int(gpio_pin) # FastAPI expects an integer for the GPIO pin

    print(f"\nAttempting to set GPIO pin {gpio_pin}...")
    print(f"Endpoint: {endpoint}")
    print(f"Form data: {form_data}")

    try:
        response = requests.post(endpoint, data=form_data)

        print(f"Status Code: {response.status_code}")
        print(f"Headers: {response.headers}")

        if response.status_code == 200:
            print("Successfully set GPIO pin")
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

def test_clear_gpio(gpio_pin: int):
    """
    Tests the /api/jobs/clear-gpio endpoint.

    Args:
        gpio_pin (int): The GPIO pin to clear.
    """
    endpoint = f"{BASE_URL}/clear-gpio"
    
    form_data = {
        "device_access_code": DEVICE_ACCESS_CODE,
        "pass_code": PASS_CODE,
    }

    if gpio_pin is not None:
        form_data["gpio_pin"] = int(gpio_pin) # FastAPI expects an integer for the GPIO pin

    print(f"\nAttempting to clear GPIO pin {gpio_pin}...")
    print(f"Endpoint: {endpoint}")
    print(f"Form data: {form_data}")

    try:
        response = requests.post(endpoint, data=form_data)

        print(f"Status Code: {response.status_code}")
        print(f"Headers: {response.headers}")

        if response.status_code == 200:
            print("Successfully cleared GPIO pin")
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

def test_get_gpio(gpio_pin: int):
    """
    Test the /api/jobs/get-gpio endpoint.

    Args:
        gpio_pin (int): The GPIO pin to get.
    """
    endpoint = f"{BASE_URL}/set-gpio"
    
    form_data = {
        "device_access_code": DEVICE_ACCESS_CODE,
        "pass_code": PASS_CODE,
    }

    if gpio_pin is not None:
        form_data["gpio_pin"] = int(gpio_pin) # FastAPI expects an integer for the GPIO pin

    print(f"\nAttempting to get GPIO pin status for {gpio_pin}...")
    print(f"Endpoint: {endpoint}")
    print(f"Form data: {form_data}")
    
    try:
        response = requests.post(endpoint, data=form_data)

        print(f"Status Code: {response.status_code}")
        print(f"Headers: {response.headers}")

        # Check the response
        if response.status_code == 200 and response.headers.get("content-type") == "application/json":
            print("Success response (JSON):")
            # Get the value of gpio_state from the response json content
            try:
                gpio_state = response.json()["gpio_state"]
                print(f"GPIO pin {gpio_pin} is {gpio_state}")
            except requests.exceptions.JSONDecodeError:
                print("Could not decode JSON response.")
                print(f"Raw content: {response.text}")
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

    except Exception as e:
        print(f"An error occurred: {e}")

def test_blink_gpio(gpio_pin: int, blink_duration_ms: int):
    """
    Tests the /api/jobs/blink-gpio endpoint.

    Args:
        gpio_pin (int): The GPIO pin to set.
        blink_duration_ms (int): The duration of the blink in milliseconds.
        default duration is 1000ms
    """
    endpoint = f"{BASE_URL}/blink-gpio"
    
    form_data = {
        "device_access_code": DEVICE_ACCESS_CODE,
        "pass_code": PASS_CODE,
    }

    if gpio_pin is not None:
        form_data["gpio_pin"] = int(gpio_pin) # FastAPI expects an integer for the GPIO pin

    if blink_duration_ms is not None:
        form_data["blink_duration_ms"] = int(blink_duration_ms) # FastAPI expects an integer for the blink duration

    blink_value = f'{blink_duration_ms}ms' if blink_duration_ms is not None else "1s"
    print(f"\nAttempting to blink GPIO pin {gpio_pin} for {blink_value}...")
    print(f"Endpoint: {endpoint}")
    print(f"Form data: {form_data}")

    try:
        response = requests.post(endpoint, data=form_data)

        print(f"Status Code: {response.status_code}")
        print(f"Headers: {response.headers}")

        if response.status_code == 200:
            print("Successfully blinked GPIO pin")
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

    # 1. Test with set_gpio with gpio_pin = 1
    test_set_gpio(gpio_pin=1)

    # 2. Test with set_gpio with gpio_pin = -1
    test_set_gpio(gpio_pin=-1)

    # 3. Test with clear_gpio with gpio_pin = 1
    test_clear_gpio(gpio_pin=1)

    # 4. Test with clear_gpio with gpio_pin = -1
    test_clear_gpio(gpio_pin=-1)

    # 5. Test with get_gpio with gpio_pin = 1
    test_get_gpio(gpio_pin=1)

    # 6. Test with get_gpio with gpio_pin = -1
    test_get_gpio(gpio_pin=-1)

    # 7. Test with blink_gpio with gpio_pin = 1 and blink_duration_ms = 250
    test_blink_gpio(gpio_pin=1, blink_duration_ms=250)

    # 8. Test with blink_gpio with gpio_pin = -1 and blink_duration_ms = 250
    test_blink_gpio(gpio_pin=-1, blink_duration_ms=250)

    # 9. Test with blink_gpio with gpio_pin = 1 and default blink_duration_ms
    test_blink_gpio(gpio_pin=1)

    # 10. Test with blink_gpio with gpio_pin = -1 and default blink_duration_ms
    test_blink_gpio(gpio_pin=-1)

    print("\n--- All tests finished ---")
    