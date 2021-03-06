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

# from erpnext.regional.doctype.gstr_3b_report.gstr_3b_report import GSTR3BReport
# from finbyzerp.finbyzerp.override.gstr_3b_report import prepare_data, get_itc_details, get_inter_state_supplies, get_tax_amounts
# GSTR3BReport.prepare_data = prepare_data
# GSTR3BReport.get_itc_details = get_itc_details
# GSTR3BReport.get_inter_state_supplies = get_inter_state_supplies
# GSTR3BReport.get_tax_amounts = get_tax_amounts

from erpnext.setup.doctype.naming_series.naming_series import NamingSeries
from finbyzerp.finbyzerp.override.naming_series import get_transactions
NamingSeries.get_transactions = get_transactions

from erpnext.accounts.doctype.opening_invoice_creation_tool.opening_invoice_creation_tool import OpeningInvoiceCreationTool
from finbyzerp.finbyzerp.doc_events.opening_invoice_creation_tool import get_invoice_dict, make_invoices

OpeningInvoiceCreationTool.get_invoice_dict = get_invoice_dict
OpeningInvoiceCreationTool.make_invoices = make_invoices


from frappe.core.doctype.report.report import Report
from finbyzerp.api import report_validate
Report.validate = report_validate


# e_invoice overrides
# import erpnext
# # from finbyzerp.e_invoice_override import validate_einvoice_fields,get_transaction_details,get_item_list,make_einvoice,get_invoice_value_details,update_invoice_taxes
# from finbyzerp.e_invoice_override import get_item_list,validate_einvoice_fields
# erpnext.regional.india.e_invoice.utils.validate_einvoice_fields = validate_einvoice_fields
# erpnext.regional.india.e_invoice.utils.get_item_list = get_item_list
# erpnext.regional.india.e_invoice.utils.get_transaction_details = get_transaction_details
# erpnext.regional.india.e_invoice.utils.make_einvoice = make_einvoice
# erpnext.regional.india.e_invoice.utils.get_invoice_value_details=get_invoice_value_details
# erpnext.regional.india.e_invoice.utils.update_invoice_taxes = update_invoice_taxes
#erpnext.regional.india.e_invoice.utils.update_item_taxes = update_item_taxes
#erpnext.regional.india.e_invoice.utils.get_party_details = get_party_details

#from erpnext.regional.india.e_invoice.utils import GSPConnector
#GSPConnector.set_einvoice_data = set_einvoice_data

# email Campaign override
from finbyzerp.finbyzerp.doc_events.email_campaign import send_email_to_leads_or_contacts
from erpnext.crm.doctype.email_campaign import email_campaign
email_campaign.send_email_to_leads_or_contacts = send_email_to_leads_or_contacts

app_include_css = ["assets/css/finbyzerp.min.css", "assets/finbyzerp/css/permission.css","/assets/finbyzerp/css/finbyz-theme.css"]
app_include_js = [
	"assets/js/finbyzerp.min.js" 
	#"assets/finbyzerp/js/frappe/ui/page.js"
]

doctype_list_js = {
	"Batch" : "public/js/doctype_js/batch_list.js",
	"Fiscal Year" : "public/js/doctype_js/fiscal_year.js"
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
	"Account":"public/js/doctype_js/account.js",
	"GST Settings":"public/js/doctype_js/gst_settings.js",
	"Lead":"public/js/doctype_js/lead.js",
	"Customer":"public/js/doctype_js/customer.js",
	"Opportunity":"public/js/doctype_js/opportunity.js",
	"Opening Invoice Creation Tool":"public/js/doctype_js/opening_invoice_creation_tool.js",
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
	"erpnext.regional.india.e_invoice.utils.cancel_eway_bill": "finbyzerp.e_invoice_override.cancel_eway_bill" # cancel eway bill override for enable cancel_eway_bill api
}

override_doctype_dashboards = {
	"Lead": "finbyzerp.finbyzerp.dashboard.lead.get_data",
	"Customer":"finbyzerp.finbyzerp.dashboard.customer.get_data",
	"Opportunity":"finbyzerp.finbyzerp.dashboard.opportunity.get_data"
}

doc_events = {
	"Customer": {
		"validate":"finbyzerp.api.customer_validate"
	},
	"Supplier": {
		"validate":"finbyzerp.api.supplier_validate"
	},
	"Item": {
		"validate":"finbyzerp.finbyzerp.doc_events.item.validate"
	},
	"User": {
		"validate":"finbyzerp.api.validate_user_mobile_no"
	},
	"Sales Invoice": {
		"before_insert": "finbyzerp.api.before_insert",
		"validate":[
			"finbyzerp.finbyzerp.doc_events.sales_invoice.validate",
			"finbyzerp.api.si_validate"
		],
		'on_submit': "finbyzerp.api.sales_invoice_on_submit"
	},
	"Purchase Invoice": {
		"before_insert": "finbyzerp.api.before_insert",
		"validate": "finbyzerp.api.pi_validate"
	},
	"Stock Entry": {
		"validate": [
			"finbyzerp.api.stock_entry_validate",
			"finbyzerp.finbyzerp.doc_events.stock_entry.validate",
		],
		"before_insert": "finbyzerp.api.before_insert",
	},
	"Journal Entry":{
		"before_insert": "finbyzerp.api.before_insert",
	},
	("Pick List","Expense Claim", "Sales Invoice", "Purchase Invoice", "Payment Request", "Payment Entry", "Journal Entry", "Material Request", "Purchase Order", "Work Order", "Production Plan", "Stock Entry", "Quotation", "Sales Order", "Delivery Note", "Purchase Receipt", "Packing Slip","Jobwork Challan","Jobwork Finish","Outward Sample","Inward Sample"): {
		"before_naming": "finbyzerp.api.before_naming",
	},
}

scheduler_events = {
	"daily":[
		"finbyzerp.api.daily_entry_summary_mail",
		"finbyzerp.api.daily_transaction_summary_mail"
	]
}

# # BOM Stock Calculated Report Override:
# from finbyzerp.finbyzerp.report.bom_stock_calculated import execute as bsc_execute
# from erpnext.manufacturing.report.bom_stock_calculated import bom_stock_calculated
# bom_stock_calculated.execute = bsc_execute

# Item wise sales register and purchase register reports changes for selecting account_head instead of description from tax table
from finbyzerp.finbyzerp.report.item_wise_sales_register import execute as item_wise_sales_register_execute
from erpnext.accounts.report.item_wise_sales_register import item_wise_sales_register
item_wise_sales_register.execute = item_wise_sales_register_execute

from finbyzerp.finbyzerp.report.item_wise_purchase_register import execute as item_wise_purchase_register_execute
from erpnext.accounts.report.item_wise_purchase_register import item_wise_purchase_register
item_wise_purchase_register.execute = item_wise_purchase_register_execute

from finbyzerp.finbyzerp.report.gst_itemised_sales_register import execute as gst_itemised_sales_register_execute
from erpnext.regional.report.gst_itemised_sales_register import gst_itemised_sales_register
gst_itemised_sales_register.execute = gst_itemised_sales_register_execute

from finbyzerp.finbyzerp.report.gst_itemised_purchase_register import execute as gst_itemised_purchase_register_execute
from erpnext.regional.report.gst_itemised_purchase_register import gst_itemised_purchase_register
gst_itemised_purchase_register.execute = gst_itemised_purchase_register_execute