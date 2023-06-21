# Copyright (c) 2023, Ritvik and Contributors
# See license.txt

import frappe
import frappe.defaults
from frappe.tests.utils import FrappeTestCase
from inventory_management.inventory_management.sle_utils import create_sle_entry
from inventory_management.inventory_management.test_utils import create_item, create_warehouse,create_stock_entry


class TestItem(FrappeTestCase):

    def setUp(self):
        item = create_item("Test Item")
        warehouse = create_warehouse("Test Warehouse")


    def tearDown(self):
        frappe.db.delete("Stock Ledger Entry", filters={
            "item": "Test Item"
        })
        frappe.db.delete("Item", filters={
            "item_name": "Test Item"
        })
        # frappe.db.commit()

    def test_save_stock_entry_receipt(self):
            
        item = frappe.db.get_all("Item")[0]['name']
        warehouse = frappe.db.get_all("Warehouse")[0]['name']


        doc = create_stock_entry(
            doctype="Stock Entry", 
            stock_entry_type="Material Receipt", 
            items=[{
                "item": item,
                "qty": 2,
                "price": 10,
            }]
        )

        self.assertRaises(frappe.ValidationError, doc.save)
        doc.items[0].target_warehouse = warehouse
        doc.submit()

        # Check whether a new entry was created or not
        doc_entry_exits = frappe.db.exists("Stock Ledger Entry", { "voucher": doc.name})
        if doc_entry_exits:
            self.assertTrue(doc_entry_exits,True)
        


    def test_save_stock_entry_consume(self):
        item = frappe.db.get_all("Item")[0]['name']
        warehouse = frappe.db.get_all("Warehouse")[0]['name']

        receipt_doc = create_stock_entry(
            doctype="Stock Entry", 
            stock_entry_type="Material Receipt", 
            items=[{
                "item": item,
                "qty": 2,
                "price": 10,
                "target_warehouse": warehouse
            }],
            submit_item_flag=True
        )

        doc = create_stock_entry(
            doctype="Stock Entry", 
            stock_entry_type="Material Consume", 
            items=[{
                "item": item,
                "qty": 2,
                "price": 10,
            }]
        )

        self.assertRaises(frappe.ValidationError, doc.save)

        receipt_doc_qty = frappe.get_value("Stock Entry Item", fieldname = "qty", filters={"parent":receipt_doc} )

        if doc.items[0].qty > receipt_doc_qty:
            self.assertRaises(frappe.ValidationError, doc.submit)
        else:
            doc.items[0].source_warehouse = warehouse
            doc.submit()
            
            # Check whether a new entry was created or not
            doc_entry_exits = frappe.db.exists("Stock Ledger Entry", { "voucher": receipt_doc})
            if doc_entry_exits:
                self.assertTrue(doc_entry_exits,True)

    def test_save_stock_entry_transfer(self):
        item = frappe.db.get_all("Item")[0]['name']
        warehouse = frappe.db.get_all("Warehouse")[0]['name']

        receipt_doc = create_stock_entry(
            doctype="Stock Entry", 
            stock_entry_type="Material Receipt", 
            items=[{
                "item": item,
                "qty": 5,
                "price": 10,
                "target_warehouse": warehouse
            }],
            submit_item_flag=True
        )

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
        # frappe.db.commit()

        doc_entry_exits = frappe.db.exists("Stock Ledger Entry", { "voucher": doc.name})
        if doc_entry_exits:
            self.assertTrue(doc_entry_exits,True)

    def test_valuation(self):
        item = frappe.db.get_all("Item")[0]['name']
        warehouse = frappe.db.get_all("Warehouse")[0]['name']
        receipt_doc = create_stock_entry(
            doctype="Stock Entry", 
            stock_entry_type="Material Receipt", 
            items=[{
                "item": item,
                "qty": 2,
                "price": 10,
                "target_warehouse": warehouse
            }],
            submit_item_flag=True
        )
        receipt_doc_2 = create_stock_entry(
            doctype="Stock Entry", 
            stock_entry_type="Material Receipt", 
            items=[{
                "item": item,
                "qty": 2,
                "price": 5,
                "target_warehouse": warehouse
            }],
            submit_item_flag=True
        )

        sle_data = frappe.db.get_all(
            "Stock Ledger Entry",
            filters={"voucher": ("in", [receipt_doc,receipt_doc_2])},
            fields=["price","qty_change"]
        )
        
        total_value = 0
        total_qty = 0
        for i in sle_data:
            total_value += i['price']*i['qty_change']
            total_qty += i['qty_change']
        calculated_valuation = total_value/total_qty
        expected_valuation = 7.5

        self.assertEqual(expected_valuation, calculated_valuation)
