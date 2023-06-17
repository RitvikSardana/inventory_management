# Copyright (c) 2023, Ritvik and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):

    columns, data = [], []

    columns = get_columns(filters)
    cs_data = get_query_data(filters)
    if not cs_data:
        frappe.msgprint("No records found")
        return columns, cs_data

    data = []
    for d in cs_data:
        row = frappe._dict({
            'date': d.creation,
            'item': d.item,
            'warehouse': d.warehouse,
            "voucher": d.voucher,
            'in_qty': d.qty_change if d.qty_change > 0 else 0,
            'out_qty': d.qty_change if d.qty_change < 0 else 0,
            'qty_after_transaction': d.qty_after_transaction,
            'valuation': d.valuation,
            'posting_date': d.date
        })
        data.append(row)
    return columns, data


def get_columns(filters):

    return [
        {
            "label": _("Date"),
            "fieldname": "date",
            "fieldtype": "Datetime",
            "width": 150
        },
        {
            "label": _("Item"),
            "fieldname": "item",
            "fieldtype": "Link",
            "options": "Item",
            "width": 100,
        },
        {
            "label": _("Warehouse"),
            "fieldname": "warehouse",
            "fieldtype": "Link",
            "options": "Warehouse",
            "width": 100,
        },
        {
            "label": _("Vouncher #"),
            "fieldname": "voucher",
            "fieldtype": "Link",
            "options": "Stock Entry",
            "width": 120,
        },
        {
            "label": _("In Qty"),
            "fieldname": "in_qty",
            "fieldtype": "Float",
            "width": 80,
        },
        {
            "label": _("Out Qty"),
            "fieldname": "out_qty",
            "fieldtype": "Float",
            "width": 80,
        },
        {
            "label": _("Balance Qty"),
            "fieldname": "qty_after_transaction",
            "fieldtype": "Float",
            "width": 100,
        },
        {
            "label": _("Valuation"),
            "fieldname": "valuation",
            "fieldtype": "Float",
        },
        {
            "label": _("Posting Date"),
            "fieldname": "posting_date",
            "fieldtype": "Date",
        },
    ]


def get_query_data(filters):

    conditions = {}
    for key, value in filters.items():
        if key == 'warehouse' or key == 'item':
            conditions[key] = value

    from_date = filters.get("from_date")
    to_date = filters.get("to_date")

    if from_date and to_date:
        if from_date > to_date:
            frappe.throw("From Date can't be greater than To Date")
        conditions['date'] = ('between', [from_date, to_date])
    elif from_date:
        conditions['date'] = ('between', [from_date])
    elif to_date:
        conditions['date'] = ('between', [to_date])

    query_data = frappe.db.get_all(
        doctype="Stock Ledger Entry",
        fields=["item", "warehouse", "qty_change",
                "qty_after_transaction", "valuation", "creation", "name", "date", "voucher"],
        filters=conditions
    )

    return query_data
