import httpx

def get_blue_dolar() -> float:
    res = httpx.get('https://dolarapi.com/v1/dolares/blue')
    data = res.json()
    return float(data['compra'])