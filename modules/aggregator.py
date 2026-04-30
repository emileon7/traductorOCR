def _safe_total(invoice):
    t = invoice.get("total")
    return t if isinstance(t, (int, float)) else 0.0

def sum_all(invoices):
    return sum(_safe_total(inv) for inv in invoices)

def sum_selection(invoices, index):
    return sum(_safe_total(invoices[i]) for i in index)