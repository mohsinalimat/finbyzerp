# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "finbyzerp"
app_title = "FinByz ERP"
app_publisher = "Finbyz Tech Pvt Ltd"
app_description = "FinByz ERP"
app_icon = "octicon octicon-diff-ignored"
app_color = "blue"
app_email = "info@finbyz.com"
app_license = "GPL 3.0"
app_version = app_version
# app_logo_url = '/assets/erpnext/images/erp-icon.svg'

from erpnext.regional.doctype.gstr_3b_report.gstr_3b_report import GSTR3BReport
from finbyzerp.finbyzerp.override.gstr_3b_report import prepare_data, get_itc_details, get_inter_state_supplies, get_tax_amounts
GSTR3BReport.prepare_data = prepare_data
GSTR3BReport.get_itc_details = get_itc_details
GSTR3BReport.get_inter_state_supplies = get_inter_state_supplies
GSTR3BReport.get_tax_amounts = get_tax_amounts

from erpnext.setup.doctype.naming_series.naming_series import NamingSeries
from finbyzerp.finbyzerp.override.naming_series import get_transactions
NamingSeries.get_transactions = get_transactions

app_include_css = ["assets/css/finbyzerp.min.css", "assets/finbyzerp/css/permission.css"]
app_include_js = "assets/js/finbyzerp.min.js"

before_install = "finbyzerp.install.before_install"
doctype_js = {
	"Role Profile": "public/js/doctype_js/role_profile.js",
	"Sales Order": "public/js/doctype_js/sales_order.js",
	"Delivery Note": "public/js/doctype_js/delivery_note.js",
	"Sales Invoice": "public/js/doctype_js/sales_invoice.js",
	"Purchase Order": "public/js/doctype_js/purchase_order.js",
	"Purchase Receipt": "public/js/doctype_js/purchase_receipt.js",
	"Purchase Invoice": "public/js/doctype_js/purchase_invoice.js",
	"Payment Entry": "public/js/doctype_js/payment_entry.js",
}
website_context = {
	"favicon": 	"/assets/finbyzerp/images/favicon.ico",
	"splash_image": "/assets/finbyzerp/images/FinbyzLogo.svg"
}

override_whitelisted_methods = {
	"frappe.core.page.permission_manager.permission_manager.get_roles_and_doctypes": "finbyzerp.permission.get_roles_and_doctypes",
	"frappe.core.page.permission_manager.permission_manager.get_permissions": "finbyzerp.permission.get_permissions",
	"frappe.core.page.permission_manager.permission_manager.add": "finbyzerp.permission.add",
	"frappe.core.page.permission_manager.permission_manager.update": "finbyzerp.permission.update",
	"frappe.core.page.permission_manager.permission_manager.remove": "finbyzerp.permission.remove",
	"frappe.core.page.permission_manager.permission_manager.reset": "finbyzerp.permission.reset",
	"frappe.core.page.permission_manager.permission_manager.get_users_with_role": "finbyzerp.permission.get_users_with_role",
	"frappe.core.page.permission_manager.permission_manager.get_standard_permissions": "finbyzerp.permission.get_standard_permissions",
}

doc_events = {
	"Sales Invoice": {
		'on_submit': "finbyzerp.api.sales_invoice_on_submit"
	},
	("Pick List", "Sales Invoice", "Purchase Invoice", "Payment Request", "Payment Entry", "Journal Entry", "Material Request", "Purchase Order", "Work Order", "Production Plan", "Stock Entry", "Quotation", "Sales Order", "Delivery Note", "Purchase Receipt", "Packing Slip"): {
		"before_naming": "finbyzerp.api.before_naming",
	},
}