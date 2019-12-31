from __future__ import unicode_literals
import frappe

@frappe.whitelist()
def get_project_name():
    frappe.flags.ignore_account_permission = True
    project_name = frappe.db.get_value("Global Defaults", "Global Defaults","project_name")
    
    return {"project_name":project_name}