# Copyright (c) 2023, Ritvik and Contributors
# See license.txt

# import frappe
from frappe.tests.utils import FrappeTestCase
from inventory_management.inventory_management.test_utils import create_item, create_warehouse
from inventory_management.inventory_management.sle_utils import create_sle_entry


class TestStockLedgerEntry(FrappeTestCase):
    def setUp(self):
        if frappe.db.exists("Item", "M2"):
            return

        item = create_item("M2")
        warehouse = create_warehouse("Test Warehouse")

    def tearDown(self):
        item = frappe.db.get_all("Item")[0]['name']
        frappe.db.delete("Stock Ledger Entry", filters={
            "item": item
        })
        frappe.db.commit()

    def test_valuation(self):
        item = frappe.db.get_all("Item")[0]['name']
        warehouse = frappe.db.get_all("Warehouse")[0]['name']
