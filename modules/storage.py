import json 
import os

def save_invoices(data, name_archivo):
    ruta = f"data/process/{name_archivo}.json"
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
        
def load_invoices():
    storage_dir = "data/process/"
    invoices = []
    
    if not os.path.exists(storage_dir):
        return invoices

    for filename in os.listdir(storage_dir):
        if filename.endswith(".json"):
            with open(os.path.join(storage_dir, filename), "r", encoding="utf-8") as json_file:
                invoices.append(json.load(json_file))
    return invoices


        

    