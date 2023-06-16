// Copyright (c) 2023, Ritvik and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Stock Ledger Report"] = {
  filters: [
    {
      fieldname: "warehouse",
      label: __("Warehouse"),
      fieldtype: "Link",
      options: "Warehouse",
    },
    {
      fieldname: "item",
      label: __("Item"),
      fieldtype: "Link",
      options: "Item",
    },
    // {
    //   fieldname: "from_date",
    //   label: __("From Date"),
    //   fieldtype: "Date",
    //   default: frappe.datetime.add_months(frappe.datetime.now_date(), -1),
    // },
    // {
    //   fieldname: "to_date",
    //   label: __("To Date"),
    //   fieldtype: "Date",
    //   default: frappe.datetime.now_date(),
    // },
  ],
};
