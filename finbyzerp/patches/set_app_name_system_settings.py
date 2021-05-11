from __future__ import unicode_literals
import frappe

def execute():
    doc = frappe.get_doc("System Settings")
    if hasattr(doc,'app_name'):
        if doc.app_name != "Finbyz ERP":
            doc.app_name = "Finbyz ERP"
            doc.save()