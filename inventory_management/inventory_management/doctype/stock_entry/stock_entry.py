# Copyright (c) 2023, Ritvik and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from inventory_management.inventory_management.sle_utils import create_sle_entry


class StockEntry(Document):

    def validate(self):
        children_items_list = self.formatted_child_table()
        # enumerate used to get index of the child,and increment it by 1 to get the row value for better UX
        for index, item in enumerate(children_items_list):

            stock_entry_type = self.stock_entry_type

            # Validate the stock entry type and return opening stock
            opening_stock = self.stock_entry_method_validate_return_quantity(
                stock_entry_type, item)
            # For Receipt We should not check if stock is available or not
            if stock_entry_type != 'Material Receipt' and item['qty'] > opening_stock:
                frappe.throw(f"Stock Unavailable in Row {index+1}")

        # Make a list of warehouse and items and query once

    def formatted_child_table(self):
        items_list = []
        for row in self.items:
            # d is for Child Doc
            d = {}
            d['target_warehouse'] = row.target_warehouse or None
            d['source_warehouse'] = row.source_warehouse or None
            d['item'] = row.item
            d['qty'] = row.qty
            d['price'] = row.price
            items_list.append(d)
        return items_list

    def stock_entry_method_validate_return_quantity(self, method, item):
        item_doc = frappe.qb.DocType("Item")

        if method == "Material Receipt":
            if item['target_warehouse'] == None:
                frappe.throw("Target Warehouse is Required")

        elif method == "Material Consume":
            if item['source_warehouse'] == None:
                frappe.throw("Source Warehouse is Required")

        elif method == "Material Transfer":
            if item['target_warehouse'] == None or item['source_warehouse'] == None:
                frappe.throw(
                    "Both Target Warehouse and Source Warehouse are Required")

        # query to get the item's opening stock
        item_opening_stock = frappe.qb.from_(item_doc).select("opening_stock").where(
            item_doc.item_name == item['item']).run()

        # Above query returns a tuple so unpack it
        if len(item_opening_stock) > 0:
            item_opening_stock = item_opening_stock[0][0]
        else:
            item_opening_stock = 0

        return item_opening_stock

    def on_submit(self):
        # For each item create SLE
        if self.stock_entry_type == 'Material Receipt':
            self.material_receipt_stock_ledger_entry()

        elif self.stock_entry_type == 'Material Consume':
            self.material_consume_stock_ledger_entry()

        elif self.stock_entry_type == 'Material Transfer':
            self.material_transfer_stock_ledger_entry()

    def material_receipt_stock_ledger_entry(self):
        children_items_list = self.formatted_child_table()
        for item in children_items_list:
            create_sle_entry(
                item=item['item'],
                warehouse=item['target_warehouse'],
                qty_change=item['qty'],
                price=item['price'],
                balance_stock_value=item['qty'] * item['price']
            )

    def material_consume_stock_ledger_entry(self):
        children_items_list = self.formatted_child_table()
        for item in children_items_list:
            create_sle_entry(
                item=item['item'],
                warehouse=item['source_warehouse'],
                qty_change=-1 * item['qty'],
                price=item['price'],
                stock_value_change=-1 * item['qty'] * item['price']
            )

    def material_transfer_stock_ledger_entry(self):
        children_items_list = self.formatted_child_table()
        for item in children_items_list:
            create_sle_entry(
                item=item['item'],
                warehouse=item['target_warehouse'],
                qty_change=item['qty'],
                price=item['price'],
                stock_value_change=item['qty'] * item['price']
            )
            create_sle_entry(
                item=item['item'],
                warehouse=item['source_warehouse'],
                qty_change=-1 * item['qty'],
                price=item['price'],
                stock_value_change=-1 * item['qty'] * item['price']
            )
