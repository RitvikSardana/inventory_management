import frappe


def create_item(name):
    item = frappe.get_doc({
        "doctype": "Item",
        "item_name": name,
    }).insert()


def create_warehouse(warehouse):
    warehouse = frappe.get_doc({
        "doctype": "Warehouse",
        "warehouse_name": warehouse,
        "parent_warehouse": "Mumbai Warehouses"
    }).insert()
