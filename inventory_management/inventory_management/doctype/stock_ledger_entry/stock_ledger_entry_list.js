frappe.listview_settings["Stock Ledger Entry"] = {
  refresh: function (listview) {
    listview.page.add_inner_button("Stock Ledger Report", () => {
      frappe.set_route("query-report", "Stock Ledger Report");
    });
    listview.page.add_inner_button("Stock Balance Report", () => {
      frappe.set_route("query-report", "Stock Balace Report");
    });
  },
};
