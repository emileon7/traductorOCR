import json
import os

# Ruta absoluta a data/process/ sin importar desde dónde se ejecute la app
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_STORAGE_DIR = os.path.join(_PROJECT_ROOT, "data", "process")


def save_invoices(data, name_archivo):
    os.makedirs(_STORAGE_DIR, exist_ok=True)
    ruta = os.path.join(_STORAGE_DIR, f"{name_archivo}.json")
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def load_invoices():
    invoices = []
    if not os.path.exists(_STORAGE_DIR):
        return invoices
    for filename in os.listdir(_STORAGE_DIR):
        if filename.endswith(".json"):
            with open(os.path.join(_STORAGE_DIR, filename), "r", encoding="utf-8") as json_file:
                invoices.append(json.load(json_file))
    return invoices


        

    