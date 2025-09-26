import requests

# --- Configuration ---
BASE_URL = "https://beta.fslaser.com/api/jobs"  # Replace with your actual server URL
DEVICE_ID = "AE356O3E89D"  # Replace with a valid device ID
PASS_CODE = "Pork_Hacking_98"  # Replace with a valid pass code
# --- End Configuration ---

def test_set_gpio(gpio_pin: int, device_totp_code=None):
    """
    Tests the /api/jobs/set-gpio endpoint.

    Args:
        gpio_pin (int): The GPIO pin to set.
    """
    endpoint = f"{BASE_URL}/set-gpio"
    
    form_data = {
        "device_id": DEVICE_ID,
        "pass_code": PASS_CODE,
    }
    
    # Only include device_totp_code if provided
    if device_totp_code:
        form_data["device_auth_code"] = device_totp_code

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

def test_clear_gpio(gpio_pin: int, device_totp_code=None):
    """
    Tests the /api/jobs/clear-gpio endpoint.

    Args:
        gpio_pin (int): The GPIO pin to clear.
    """
    endpoint = f"{BASE_URL}/clear-gpio"
    
    form_data = {
        "device_id": DEVICE_ID,
        "pass_code": PASS_CODE,
    }
    
    # Only include device_totp_code if provided
    if device_totp_code:
        form_data["device_auth_code"] = device_totp_code

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

def test_get_gpio(gpio_pin: int, device_totp_code=None):
    """
    Test the /api/jobs/get-gpio endpoint.

    Args:
        gpio_pin (int): The GPIO pin to get.
    """
    endpoint = f"{BASE_URL}/get-gpio"
    
    form_data = {
        "device_id": DEVICE_ID,
        "pass_code": PASS_CODE,
    }
    
    # Only include device_totp_code if provided
    if device_totp_code:
        form_data["device_auth_code"] = device_totp_code

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

def test_blink_gpio(gpio_pin: int, blink_duration_ms: int | None = None, device_totp_code=None):
    """
    Tests the /api/jobs/blink-gpio endpoint.

    Args:
        gpio_pin (int): The GPIO pin to set.
        blink_duration_ms (int): The duration of the blink in milliseconds.
        default duration is 1000ms
    """
    endpoint = f"{BASE_URL}/blink-gpio"
    
    form_data = {
        "device_id": DEVICE_ID,
        "pass_code": PASS_CODE,
    }
    
    # Only include device_totp_code if provided
    if device_totp_code:
        form_data["device_auth_code"] = device_totp_code

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

def test_send_gpio(gpio_command: str, device_totp_code=None):
    """
    Tests the /api/jobs/send-gpio endpoint.

    Args:
        gpio_command (str): The GPIO command to send.
    """
    endpoint = f"{BASE_URL}/send-gpio"
    
    form_data = {
        "device_id": DEVICE_ID,
        "pass_code": PASS_CODE,
    }
    
    # Only include device_totp_code if provided
    if device_totp_code:
        form_data["device_auth_code"] = device_totp_code

    if gpio_command is not None:
        form_data["gpio_command"] = gpio_command # FastAPI expects a string for the GPIO command

    print(f'\nAttempting to send GPIO command "{gpio_command}"...')
    print(f'Endpoint: {endpoint}')
    print(f'Form data: {form_data}')

    try:
        response = requests.post(endpoint, data=form_data)

        print(f"Status Code: {response.status_code}")
        print(f"Headers: {response.headers}")

        if response.status_code == 200:
            print("Successfully sent GPIO command")
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
    # Option 1: Same network - no auth code needed
    print("Testing without auth code (same network)...")
    
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

    # 11. Test with send_gpio with gpio_command = "set pin1"
    test_send_gpio(gpio_command="set pin1")

    # 12. Test with send_gpio with gpio_command = "clear pin1"
    test_send_gpio(gpio_command="clear pin1")
    
    # Option 2: Using TOTP auth code (uncomment if needed)
    # from auth_code_grabber import get_device_auth_code
    # print("Testing with auth code (TOTP)...")
    # try:
    #     device_ip = "192.168.1.100"  # Define device IP only when using TOTP
    #     device_totp_code = get_device_auth_code(device_ip)
    #     print("Testing GPIO operations with TOTP...")
    #     test_set_gpio(gpio_pin=1, device_totp_code=device_totp_code)
    #     test_clear_gpio(gpio_pin=1, device_totp_code=device_totp_code)
    #     test_get_gpio(gpio_pin=1, device_totp_code=device_totp_code)
    # except Exception as e:
    #     print(f"Could not use TOTP authentication: {e}")

    print("\n--- All tests finished ---")
    