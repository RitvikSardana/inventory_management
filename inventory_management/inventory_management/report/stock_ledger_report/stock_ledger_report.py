# Copyright (c) 2023, Ritvik and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):

    columns, data = [], []

    columns = get_columns(filters)
    cs_data = get_cs_data(filters)
    print(cs_data)
    if not cs_data:
        frappe.msgprint("No records found")
        return column, cs_data

    data = []
    for d in cs_data:
        row = frappe._dict({
            'item_name': d.item_name
        })
        data.append(row)

    print(data)
    return columns, data


def get_columns(filters):

    return [
        # {
        #     "label": _("Date"),
        #     "fieldname": "date",
        #     "fieldtype": "Datetime",
        #     "width": 150
        # },
        {
            "label": _("Item"),
            "fieldname": "item_name",
            "fieldtype": "Link",
            "options": "Item",
            "width": 100,
        },
    ]


def get_cs_data(filters):
    conditions = get_conditions(filters)
    data = frappe.get_all(
        doctype="Item",
        fields=["item_name"],
        filters=conditions
    )


def get_conditions(filters):
    conditions = {}

    for key, value in filters.items():
        conditions[key] = value

    return conditions
