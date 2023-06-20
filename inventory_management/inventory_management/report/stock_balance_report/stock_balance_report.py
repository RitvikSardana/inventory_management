# Copyright (c) 2023, Ritvik and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):

    columns, data = [], []
    columns = get_columns(filters)
    query_data = get_query_data(filters)
    if not query_data:
        frappe.msgprint("No records found")
        return columns, query_data

    data = []
    for d in query_data:
        row = frappe._dict({
            'item': d.item,
            'warehouse': d.warehouse,
            'qty_after_transaction': d.qty_after_transaction,
            'balance_stock_value': d.valuation * d.qty_after_transaction,
            'date': d.date
        })
        data.append(row)
    return columns, data


def get_columns(filters):

    return [
        {
            "label": _("Date"),
            "fieldname": "date",
            "fieldtype": "Date",
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
            "label": _("Balance Qty"),
            "fieldname": "qty_after_transaction",
            "fieldtype": "Float",
            "width": 100,
        },
        {
            "label": _("Balance Stock Value"),
            "fieldname": "balance_stock_value",
            "fieldtype": "Float",
        }
    ]


def get_query_data(filters):
    conditions = {}
    from_date = filters.get("from_date")
    to_date = filters.get("to_date")

    if from_date and to_date:
        if from_date > to_date:
            frappe.throw("From Date can't be greater than To Date")

        conditions['date'] = ('between', [from_date, to_date])
    elif from_date:
        conditions['date'] = ('between', [from_date])

    elif to_date:
        conditions['date'] = ('between', [to_date, to_date])
    else:
        conditions = {}

    query_data = frappe.db.get_all(
        doctype="Stock Ledger Entry",
        fields=[
            "item",
            "warehouse",
            "qty_change",
            "qty_after_transaction",
            "valuation",
            "creation",
            "date"
        ],
        filters=conditions,
    )

    grouped_data = {}

    for record in query_data:
        item = record.item
        warehouse = record.warehouse
        valuation = record.valuation

        if (item, warehouse) not in grouped_data:
            grouped_data[(item, warehouse)] = record
        else:
            latest_record = grouped_data[(item, warehouse)]
            if record.creation > latest_record.creation:
                grouped_data[(item, warehouse)] = record

    result = list(grouped_data.values())

    return result