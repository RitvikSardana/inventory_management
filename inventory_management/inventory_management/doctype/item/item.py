# Copyright (c) 2023, Ritvik and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from inventory_management.inventory_management.sle_utils import create_sle_entry


class Item(Document):
    def before_save(self):
        if not self.warehouse:
            default_warehouse = frappe.db.get_single_value(
                "Stock Settings", "default_warehouse")
            self.warehouse = default_warehouse

    def after_insert(self):

        sle_doc = frappe.qb.DocType("Stock Ledger Entry")
        # frappe.qb.from_(sle_doc).sum.select(sle_doc['qty_after_transaction'])

        if self.qty:
            create_sle_entry(
                item=self.item_name,
                warehouse=self.warehouse,
                qty_change=self.qty,
                qty_after_transaction=self.qty,
                price=self.price,
                balance_stock_value=self.qty * self.price
            )
