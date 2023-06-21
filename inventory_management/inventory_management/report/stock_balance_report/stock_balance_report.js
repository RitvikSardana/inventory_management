// Copyright (c) 2023, Ritvik and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Stock Balance Report"] = {
  filters: [
    {
      label: __("Date"),
      fieldname: "to_date",
      fieldtype: "Date",
      default: frappe.datetime.now_date(),
    },
  ],
};
