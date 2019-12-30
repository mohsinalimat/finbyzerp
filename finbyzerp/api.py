from __future__ import unicode_literals
import frappe

@frappe.whitelist()
def get_project_name():
    doc = frappe.get_doc("Global Defaults", "Global Defaults")
    
    doc.flags.ignore_permissions = True

    return {"project_name":doc.project_name}