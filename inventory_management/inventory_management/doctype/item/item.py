# Copyright (c) 2023, Ritvik and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Item(Document):
    def before_save(self):
        if not self.warehouse:
            default_warehouse = frappe.db.get_single_value(
                "Stock Settings", "default_warehouse")
            self.warehouse = default_warehouse
