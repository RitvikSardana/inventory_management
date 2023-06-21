# Copyright (c) 2023, Ritvik and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from inventory_management.inventory_management.sle_utils import create_sle_entry


class StockEntry(Document):

    def validate(self):
        # enumerate used to get index of the child,and increment it by 1 to get the row value for better UX
        for item in self.items:
            stock_entry_type = self.stock_entry_type

            self.validate_method(item)


    def validate_method(self, item):
        if self.stock_entry_type == "Material Receipt":
            if not item.target_warehouse:
                frappe.throw("Target Warehouse is Required")

        elif self.stock_entry_type == "Material Consume":
            if not item.source_warehouse:
                frappe.throw("Source Warehouse is Required")

        elif self.stock_entry_type == "Material Transfer":
            if not item.target_warehouse or not item.source_warehouse:
                frappe.throw(
                    "Both Target Warehouse and Source Warehouse are Required")



    def on_submit(self):
        # For each item create SLE
        if self.stock_entry_type == 'Material Receipt':
            self.material_receipt_stock_ledger_entry()

        elif self.stock_entry_type == 'Material Consume':
            self.material_consume_stock_ledger_entry()

        elif self.stock_entry_type == 'Material Transfer':
            self.material_transfer_stock_ledger_entry()

    def material_receipt_stock_ledger_entry(self):
        for item in self.items:
            total_value, total_qty = self.get_stock_ledger_entry_totals(
                item.item, item.target_warehouse)
            # print("POSTING",self.posting_date)
            valuation = 0
            if total_value != 0 or total_qty != 0:
                valuation = (
                    total_value + (item.price*item.qty)) / (total_qty + item.qty)
            else:
                valuation = (item.qty * item.price) / item.qty

            create_sle_entry(
                item=item.item,
                warehouse=item.target_warehouse,
                qty_change=item.qty,
                price=item.price,
                stock_value_change=item.qty * item.price,
                qty_after_transaction=total_qty + item.qty,
                valuation=valuation,
                voucher=self.name,
                date=self.posting_date
            )

    def material_consume_stock_ledger_entry(self):
        for item in self.items:

            total_value, total_qty = self.get_stock_ledger_entry_totals(
                item.item, item.source_warehouse)

            if total_qty <= 0:
                frappe.throw("No Stock Available at row {item.idx}")

            old_valuation = total_value / total_qty


            if item.qty > total_qty:
                frappe.throw(
                    f"Stock Unavailable at row {item.idx}, Available Stock is {total_qty}")

            outgoing_qty = -1 * item.qty

            if total_qty + outgoing_qty == 0:
                valuation = 0

            else:
                valuation = (
                    total_value + (old_valuation * (outgoing_qty))) / (total_qty + (outgoing_qty))

            create_sle_entry(
                item=item.item,
                warehouse=item.source_warehouse,
                qty_change=outgoing_qty,
                price=item.price,
                stock_value_change=-1 * old_valuation,
                qty_after_transaction=total_qty + (outgoing_qty),
                valuation=valuation,
                voucher=self.name
            )

    def material_transfer_stock_ledger_entry(self):
        for item in self.items:
            # For Target Warehouse
            total_value_in, total_qty_in = self.get_stock_ledger_entry_totals(
                item.item, item.target_warehouse)
            valuation_in = 0

            if total_value_in != 0 or total_qty_in != 0:
                valuation_in = (
                    total_value_in + (item.price*item.qty)) / (total_qty_in + item.qty)
            else:
                valuation_in = (item.qty * item.price) / item.qty

            # For Source Warehouse
            total_value_out, total_qty_out = self.get_stock_ledger_entry_totals(
                item.item, item.source_warehouse)

            old_valuation = total_value_out / total_qty_out

            outgoing_qty = -1 * item.qty
            valuation_out = (
                total_value_out + (old_valuation * (outgoing_qty))) / (total_qty_out + (outgoing_qty))

            # Create Target SLE Entry
            create_sle_entry(
                item=item.item,
                warehouse=item.target_warehouse,
                qty_change=item.qty,
                price=item.price,
                stock_value_change=item.qty * item.price,
                qty_after_transaction=total_qty_in + item.qty,
                valuation=valuation_in,
                voucher=self.name

            )

            # Create Source SLE Entry
            create_sle_entry(
                item=item.item,
                warehouse=item.source_warehouse,
                qty_change=outgoing_qty,
                price=item.price,
                stock_value_change=-1 * old_valuation,
                qty_after_transaction=total_qty_out + (outgoing_qty),
                valuation=valuation_out,
                voucher=self.name

            )

    def get_stock_ledger_entry_totals(self, item, warehouse):
        q = frappe.db.get_all(
            "Stock Ledger Entry",
            filters={
                "item": item,
                "warehouse": warehouse,
            },
            fields=[
                "SUM(qty_change * price) as total_value",
                "SUM(qty_change) as total_qty"
            ]
        )
        total_value = q[0]['total_value'] if q and q[0]['total_value'] is not None else 0
        total_qty = q[0]['total_qty'] if q and q[0]['total_value'] is not None else 0
        return total_value, total_qty
