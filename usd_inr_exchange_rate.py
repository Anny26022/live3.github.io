# This module fetches the latest USD to INR exchange rate using an open API
import requests

def get_usd_inr_rate():
    try:
        resp = requests.get("https://api.exchangerate.host/latest?base=USD&symbols=INR", timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return float(data['rates']['INR'])
    except Exception:
        return 83.0  # fallback to a reasonable default if API fails
