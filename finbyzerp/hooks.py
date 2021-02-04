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


after_install = "finbyzerp.install.after_install"

from erpnext.regional.doctype.gstr_3b_report.gstr_3b_report import GSTR3BReport
from finbyzerp.finbyzerp.override.gstr_3b_report import prepare_data, get_itc_details, get_inter_state_supplies, get_tax_amounts
GSTR3BReport.prepare_data = prepare_data
GSTR3BReport.get_itc_details = get_itc_details
GSTR3BReport.get_inter_state_supplies = get_inter_state_supplies
GSTR3BReport.get_tax_amounts = get_tax_amounts

from erpnext.setup.doctype.naming_series.naming_series import NamingSeries
from finbyzerp.finbyzerp.override.naming_series import get_transactions
NamingSeries.get_transactions = get_transactions

app_include_css = ["assets/css/finbyzerp.min.css", "assets/finbyzerp/css/permission.css","/assets/finbyzerp/css/finbyz-theme.css"]
app_include_js = [
	"assets/js/finbyzerp.min.js" 
	#"assets/finbyzerp/js/frappe/ui/page.js"
]

doctype_list_js = {
	"Batch" : "public/js/doctype_js/batch_list.js"
}

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
	"Stock Entry": "public/js/doctype_js/stock_entry.js",
	"Account":"public/js/doctype_js/account.js"
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
	"erpnext.setup.doctype.company.delete_company_transactions.delete_company_transactions": "finbyzerp.finbyzerp.override.delete_company_transactions.delete_company_transactions",
	"frappe.desk.moduleview.get_desktop_settings": "finbyzerp.api.get_desktop_settings",
	"frappe.desk.moduleview.get_options_for_global_modules": "finbyzerp.api.get_options_for_global_modules",
	"frappe.utils.print_format.download_pdf": "finbyzerp.print_format.download_pdf",
}

doc_events = {
	"Sales Invoice": {
		'on_submit': "finbyzerp.api.sales_invoice_on_submit"
	},
	"Stock Entry": {
		"validate": "finbyzerp.api.stock_entry_validate"
	},
	("Pick List","Expense Claim", "Sales Invoice", "Purchase Invoice", "Payment Request", "Payment Entry", "Journal Entry", "Material Request", "Purchase Order", "Work Order", "Production Plan", "Stock Entry", "Quotation", "Sales Order", "Delivery Note", "Purchase Receipt", "Packing Slip"): {
		"before_naming": "finbyzerp.api.before_naming",
	},
}

scheduler_events = {
	"daily":[
		"finbyzerp.api.daily_entry_summary_mail",
		"finbyzerp.api.daily_transaction_summary_mail"
	]
}

# BOM Stock Calculated Report Override:
from finbyzerp.finbyzerp.report.bom_stock_calculated import execute as bsc_execute
from erpnext.manufacturing.report.bom_stock_calculated import bom_stock_calculated
bom_stock_calculated.execute = bsc_execute