import json
import os

# Ruta absoluta basada en la ubicación de storage.py — funciona en cualquier PC
_PROJECT_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "process")
_STORAGE_DIR = os.path.join(_PROJECT_ROOT, "data", "process")


def _sorted_files() -> list[str]:
    if not os.path.exists(_STORAGE_DIR):
        return []
    return sorted(f for f in os.listdir(_STORAGE_DIR) if f.endswith(".json"))


def save_invoices(data, name_archivo):
    os.makedirs(_STORAGE_DIR, exist_ok=True)
    ruta = os.path.join(_STORAGE_DIR, f"{name_archivo}.json")
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def load_invoices() -> list[dict]:
    invoices = []
    for filename in _sorted_files():
        with open(os.path.join(_STORAGE_DIR, filename), "r", encoding="utf-8") as f:
            invoices.append(json.load(f))
    return invoices


def get_invoice(idx: int) -> dict | None:
    files = _sorted_files()
    if idx < 0 or idx >= len(files):
        return None
    with open(os.path.join(_STORAGE_DIR, files[idx]), "r", encoding="utf-8") as f:
        return json.load(f)


def update_invoice(idx: int, new_data: dict):
    files = _sorted_files()
    if idx < 0 or idx >= len(files):
        raise IndexError(f"Índice {idx} fuera de rango ({len(files)} facturas)")
    path = os.path.join(_STORAGE_DIR, files[idx])
    with open(path, "r", encoding="utf-8") as f:
        current = json.load(f)
    current.update({k: v for k, v in new_data.items() if v != ""})
    # Convertir total a float si viene como string
    if "total" in current and isinstance(current["total"], str):
        try:
            current["total"] = float(current["total"].replace(",", "."))
        except ValueError:
            current["total"] = None
    with open(path, "w", encoding="utf-8") as f:
        json.dump(current, f, indent=4, ensure_ascii=False)


def delete_invoice(idx: int):
    files = _sorted_files()
    if idx < 0 or idx >= len(files):
        raise IndexError(f"Índice {idx} fuera de rango ({len(files)} facturas)")
    os.remove(os.path.join(_STORAGE_DIR, files[idx]))