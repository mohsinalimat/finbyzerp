import frappe

@frappe.whitelist()
def after_install():
    """ Function to set docperm for Local Admin """
	if not frappe.db.exists("Role", "Local Admin"):
		role_doc = frappe.new_doc("Role")

		role_doc.desk_access = 1
		role.save()
		frappe.db.commit()
	
	count = frappe.db.sql("select count(*) from tabDocPerm where idx = 2 and role = 'Local Admin' And parent = 'Custom DocPerm'")
	if not count[0][0]:
		doc = frappe.new_doc("DocPerm")
		doc.read = 1
		doc.write = 1
		doc.create = 1
		doc.delete = 1
		doc.idx = 2
		doc.parent = "Custom DocPerm" #"Role"
		doc.role = "Local Admin"
		doc.parentfield = 'permissions'
		doc.parenttype = "DocType"

		doc.db_insert()
	
	count = frappe.db.sql("select count(*) from tabDocPerm where idx = 2 and role = 'Local Admin' And parent = 'Role'")
	if not count[0][0]:
		doc1 = frappe.new_doc("DocPerm")
		doc1.read = 1
		doc1.write = 1
		doc1.create = 1
		doc1.delete = 1
		doc1.idx = 2
		doc1.parent = "Role"
		doc1.role = "Local Admin"
		doc1.parentfield = 'permissions'
		doc1.parenttype = "DocType"
		
		doc1.db_insert()
	
	frappe.db.commit()
