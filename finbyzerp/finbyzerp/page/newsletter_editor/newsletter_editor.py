import frappe

@frappe.whitelist()
def get_email_detail(email_template):
    doc = frappe.get_doc("Email Template",email_template)
    return doc

@frappe.whitelist()
def get_doctype(doctype):
    doc = frappe.get_doc("DocType",doctype)
    return doc

@frappe.whitelist()
def get_doc_field_list(doc_type):
    filed_list = []
    fields = frappe.get_meta(doc_type).fields
    exclude_fields = ['naming_series']
    for d in fields:
        if d.fieldname not in exclude_fields and \
			d.fieldtype not in ['HTML', 'Section Break', 'Column Break', 'Button', 'Read Only','Table']:
            filed_list.append(d.fieldname)
    return filed_list


