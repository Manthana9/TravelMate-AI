# agent/tools.py

def fetch_destination_alerts(destination: str) -> str:
    """
    Fetches active weather and safety risk alerts for a given destination.
    
    Args:
        destination: The city or region name to inspect.
        
    Returns:
        A string containing current risk details.
    """
    # Member 4 will replace this string with a real 'requests.get()' API call later!
    if "manali" in destination.lower():
        return "Heavy sub-zero snowfall predicted. High threat of black ice and road blockages near Rohtang Pass."
    return "No major environmental risks detected."