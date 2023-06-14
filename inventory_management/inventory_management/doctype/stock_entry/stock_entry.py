# Copyright (c) 2023, Ritvik and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class StockEntry(Document):

    def validate(self):
        children_items_list = self.formatted_child_table()

        for index, item in enumerate(children_items_list):

            stock_entry_type = self.stock_entry_type
            # Validate the stock entry type and return qty
            qty = self.stock_entry_method_validate_return_quantity(
                stock_entry_type, item)

            # For Receipt We should not check if stock is available or not
            if stock_entry_type != 'Material Receipt' and int(item['qty']) > qty:
                frappe.throw(f"Stock Unavailable in Row {index+1}")

            if stock_entry_type == 'Material Receipt':
                self.material_receipt_stock_ledger_entry()

            elif stock_entry_type == 'Material Consume':
                self.material_consume_stock_ledger_entry()

            elif stock_entry_type == 'Material Transfer':
                self.material_transfer_stock_ledger_entry()

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

        # Only Once we have to query
        item_qty = frappe.qb.from_(item_doc).select(
            "qty").where(item_doc.item_name == item['item']).run()

        if len(item_qty) > 0:
            item_qty = item_qty[0][0]
        else:
            item_qty = 0

        return item_qty

    def on_submit(self):
        pass

    def material_receipt_stock_ledger_entry(self):
        pass

    def material_consume_stock_ledger_entry(self):
        pass

    def material_transfer_stock_ledger_entry(self):
        pass