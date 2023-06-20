# Copyright (c) 2023, Ritvik and Contributors
# See license.txt

import frappe
import frappe.defaults
from frappe.tests.utils import FrappeTestCase
from inventory_management.inventory_management.sle_utils import create_sle_entry
from inventory_management.inventory_management.test_utils import create_item, create_warehouse


class TestItem(FrappeTestCase):

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

    def test_save_stock_entry_receipt(self):

        item = frappe.db.get_all("Item")[0]['name']
        warehouse = frappe.db.get_all("Warehouse")[0]['name']

        initial_sle_count = frappe.db.count("Stock Ledger Entry")

        doc = frappe.get_doc({
            "doctype": "Stock Entry",
            "stock_entry_type": "Material Receipt",
            "items": [{
                "item": item,
                "qty": 2,
                "price": 10,
            }]
        })

        self.assertRaises(frappe.ValidationError, doc.save)
        doc.items[0].target_warehouse = warehouse
        doc.submit()
        frappe.db.commit()

        new_sle_count = frappe.db.count("Stock Ledger Entry")
        self.assertEqual(new_sle_count, initial_sle_count + 1)

    def test_save_stock_entry_consume(self):
        item = frappe.db.get_all("Item")[0]['name']
        warehouse = frappe.db.get_all("Warehouse")[0]['name']
        receipt_doc = frappe.get_doc({
            "doctype": "Stock Entry",
            "stock_entry_type": "Material Receipt",
            "items": [{
                "item": item,
                "qty": 1,
                "price": 5,
                "target_warehouse": warehouse
            }]
        }).insert().submit()

        initial_sle_count = frappe.db.count("Stock Ledger Entry")

        doc = frappe.get_doc({
            "doctype": "Stock Entry",
            "stock_entry_type": "Material Consume",
            "items": [{
                "item": item,
                "qty": 3,
                "price": 10,
            }]
        })

        self.assertRaises(frappe.ValidationError, doc.save)

        if doc.items[0].qty > receipt_doc.items[0].qty:
            self.assertRaises(frappe.ValidationError, doc.submit)
        else:
            doc.items[0].source_warehouse = warehouse
            frappe.db.commit()
            new_sle_count = frappe.db.count("Stock Ledger Entry")
            self.assertEqual(new_sle_count, initial_sle_count + 1)

    def test_save_stock_entry_transfer(self):
        item = frappe.db.get_all("Item")[0]['name']
        warehouse = frappe.db.get_all("Warehouse")[0]['name']

        receipt_doc = frappe.get_doc({
            "doctype": "Stock Entry",
            "stock_entry_type": "Material Receipt",
            "items": [{
                "item": item,
                "qty": 1,
                "price": 5,
                "target_warehouse": warehouse
            }]
        }).insert().submit()

        initial_sle_count = frappe.db.count("Stock Ledger Entry")

        doc = frappe.get_doc({
            "doctype": "Stock Entry",
            "stock_entry_type": "Material Transfer",
            "items": [{
                "item": item,
                "qty": 3,
                "price": 20,
            }]
        })
        self.assertRaises(frappe.ValidationError, doc.save)
        doc.items[0].source_warehouse = warehouse
        doc.items[0].target_warehouse = "Andheri Warehouse"
        doc.submit()
        frappe.db.commit()

        new_sle_count = frappe.db.count("Stock Ledger Entry")
        self.assertEqual(new_sle_count, initial_sle_count + 2)
