import requests

def get_device_auth_code(device_ip):
    """
    Get device authentication code from the device's /2fa endpoint.
    
    Args:
        device_ip (str): The IP address of the device.
        
    Returns:
        str: The TOTP authentication code.
        
    Raises:
        Exception: If failed to get TOTP or device is unreachable.
    """
    try:
        # Try HTTPS first, then fallback to HTTP
        try:
            totp_response = requests.post(f"https://{device_ip}/2fa", verify=False, timeout=10).json()
        except:
            totp_response = requests.post(f"http://{device_ip}/2fa", timeout=10).json()
            
        if not totp_response.get("success"):
            raise Exception(f"Failed to get TOTP: {totp_response}")
            
        return totp_response["totp"]["totp"]
        
    except Exception as e:
        raise Exception(f"Could not get device auth code from {device_ip}: {e}")
