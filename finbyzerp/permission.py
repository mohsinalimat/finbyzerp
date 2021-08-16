from __future__ import unicode_literals

import frappe
from frappe import _

from frappe.modules.import_file import get_file_path, read_doc_from_file
from frappe.translate import send_translations
from frappe.core.doctype.doctype.doctype import (clear_permissions_cache,
	validate_permissions_for_doctype)
from frappe.permissions import (reset_perms, get_linked_doctypes, get_all_perms,
	setup_custom_perms, add_permission, update_permission_property)

not_allowed_in_permission_manager = ["DocType", "DocField", "DocPerm", "System Manager", "Has Role",
	"Page", "Module Def", "Print Format", "Report", "Customize Form", "DocShare",
	"Customize Form Field", "Property Setter", "Custom Field", "Custom Script", "Patch Log", "Transaction Log"]

@frappe.whitelist()
def get_roles_and_doctypes():
	frappe.only_for(("System Manager","Local Admin"))
	send_translations(frappe.get_lang_dict("doctype", "DocPerm"))

	active_domains = frappe.get_active_domains()

	doctypes = frappe.get_all("DocType", filters={
		"istable": 0,
		"name": ("not in", ",".join(not_allowed_in_permission_manager)),
	}, or_filters={
		"ifnull(restrict_to_domain, '')": "",
		"restrict_to_domain": ("in", active_domains)
	}, fields=["name"])

	roles = frappe.get_all("Role", filters={
		"name": ("not in", "Administrator", "System Manager"),
		"disabled": 0,
	}, or_filters={
		"ifnull(restrict_to_domain, '')": "",
		"restrict_to_domain": ("in", active_domains)
	}, fields=["name"])

	doctypes_list = [ {"label":_(d.get("name")), "value":d.get("name")} for d in doctypes]
	roles_list = [ {"label":_(d.get("name")), "value":d.get("name")} for d in roles if d.get('name') != "System Manager"]

	return {
		"doctypes": sorted(doctypes_list, key=lambda d: d['label']),
		"roles": sorted(roles_list, key=lambda d: d['label'])
	}

@frappe.whitelist()
def get_permissions(doctype=None, role=None):
	frappe.only_for(("System Manager","Local Admin"))
	if role:
		out = get_all_perms(role)
		if doctype:
			out = [p for p in out if p.parent == doctype]
	else:
		out = frappe.get_all('Custom DocPerm', fields='*', filters=dict(parent = doctype), order_by="permlevel")
		if not out:
			out = frappe.get_all('DocPerm', fields='*', filters=dict(parent = doctype), order_by="permlevel")

	linked_doctypes = {}
	for d in out:
		if not d.parent in linked_doctypes:
			linked_doctypes[d.parent] = get_linked_doctypes(d.parent)
		d.linked_doctypes = linked_doctypes[d.parent]
		meta = frappe.get_meta(d.parent)
		if meta:
			d.is_submittable = meta.is_submittable

	return out

@frappe.whitelist()
def add(parent, role, permlevel):
	frappe.only_for(("System Manager","Local Admin"))
	add_permission(parent, role, permlevel)

@frappe.whitelist()
def update(doctype, role, permlevel, ptype, value=None):
	frappe.only_for(("System Manager","Local Admin"))
	out = update_permission_property(doctype, role, permlevel, ptype, value)
	return 'refresh' if out else None

@frappe.whitelist()
def remove(doctype, role, permlevel):
	frappe.only_for(("System Manager","Local Admin"))
	setup_custom_perms(doctype)

	name = frappe.get_value('Custom DocPerm', dict(parent=doctype, role=role, permlevel=permlevel))

	frappe.db.sql('delete from `tabCustom DocPerm` where name=%s', name)
	if not frappe.get_all('Custom DocPerm', dict(parent=doctype)):
		frappe.throw(_('There must be atleast one permission rule.'), title=_('Cannot Remove'))

	validate_permissions_for_doctype(doctype, for_remove=True)

@frappe.whitelist()
def reset(doctype):
	frappe.only_for(("System Manager","Local Admin"))
	reset_perms(doctype)
	clear_permissions_cache(doctype)

@frappe.whitelist()
def get_users_with_role(role):
	frappe.only_for(("System Manager","Local Admin"))
	return [p[0] for p in frappe.db.sql("""select distinct tabUser.name
		from `tabHas Role`, tabUser where
			`tabHas Role`.role=%s
			and tabUser.name != "Administrator"
			and `tabHas Role`.parent = tabUser.name
			and tabUser.enabled=1""", role)]

@frappe.whitelist()
def get_standard_permissions(doctype):
	frappe.only_for(("System Manager","Local Admin"))
	doc = frappe.get_doc('DocType', doctype)
	return [p.as_dict() for p in doc.permissions]
	
from frappe.utils.response import send_private_file
from frappe.core.doctype.access_log.access_log import make_access_log

def download_backup(path):
	try:
		frappe.only_for(("System Manager", "Administrator","Local Admin"))
		make_access_log(report_name='Backup')
	except frappe.PermissionError:
		raise Forbidden(_("You need to be logged in and have System Manager Role to be able to access backups."))

	return send_private_file(path)