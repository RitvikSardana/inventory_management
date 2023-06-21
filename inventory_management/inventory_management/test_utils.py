import frappe


def create_item(name):
    if frappe.db.exists("Item", name):
        return
    item = frappe.get_doc({
        "doctype": "Item",
        "item_name": name,
    }).insert()


def create_warehouse(warehouse):
    if frappe.db.exists("Warehouse", warehouse):
        return
    warehouse = frappe.get_doc({
        "doctype": "Warehouse",
        "warehouse_name": warehouse,
        "parent_warehouse": "Mumbai Warehouses"
    }).insert()


def create_stock_entry(doctype, stock_entry_type, submit_item_flag=False, items=[]):
    if submit_item_flag:
        doc = frappe.get_doc({
            "doctype": doctype,
            "stock_entry_type": stock_entry_type,
            "items": items
        }).insert().submit()

        return doc.name

    else:
        doc = frappe.get_doc({
            "doctype": doctype,
            "stock_entry_type": stock_entry_type,
            "items": items
        })
        return doc
