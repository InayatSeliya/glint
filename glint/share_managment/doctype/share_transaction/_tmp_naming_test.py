import frappe
from frappe.model.naming import _format_autoname


def run():
    doc = frappe.new_doc("Share Transaction")
    doc.naming_series = "ShTr-"
    results = []
    for s in [
        "format:{naming_series}{####}",
        "format:{naming_series}.{####}",
        "format:{naming_series}{#####}",
        "format:{naming_series}.{#####}"
    ]:
        try:
            results.append(f"{s} -> {_format_autoname(s, doc)}")
        except Exception as e:
            results.append(f"{s} ERROR {type(e).__name__}: {e}")
    return "\n".join(results)


def run_series():
    import frappe
    current = frappe.db.sql("select name, current from `tabSeries` where name=%s", ("ShTr-",), as_dict=True)
    return current
