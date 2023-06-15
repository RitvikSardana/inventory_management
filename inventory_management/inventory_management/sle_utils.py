import frappe


def create_sle_entry(**fields):

    sle_doc = frappe.get_doc({
        "doctype": "Stock Ledger Entry",
        **fields
    })

    sle_doc.insert()
