// Copyright (c) 2023, Ritvik and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Stock Balance Report"] = {
  filters: [
    {
      label: __("From Date"),
      fieldname: "from_date",
      fieldtype: "Date",
      default: frappe.datetime.add_months(frappe.datetime.now_date(), -1),
    },
    {
      label: __("To Date"),
      fieldname: "to_date",
      fieldtype: "Date",
      default: frappe.datetime.now_date(),
    },
  ],
};
