import json

def analyze_ticket(ticket_data):
    return json.dumps({
        "modulo": "FI",
        "transaccion": "ZFI_PRUEBA",
        "urgencia": 3,
        "impacto": 3,
    })