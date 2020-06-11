from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
import json
from six import iteritems
from frappe.utils import flt, getdate
from erpnext.regional.india import state_numbers

def prepare_data(self, doctype, tax_details, supply_type, supply_category, gst_category_list, reverse_charge="N"):
	
	# Finbyz Changes
	if supply_category == "isup_rev":
		gst_category_list.append("Unregistered")

	account_map = {
		'sgst_account': 'samt',
		'cess_account': 'csamt',
		'cgst_account': 'camt',
		'igst_account': 'iamt'
	}

	txval = 0
	total_taxable_value = self.get_total_taxable_value(doctype, reverse_charge)
	for gst_category in gst_category_list:
		txval += total_taxable_value.get(gst_category,0)
		for account_head in self.account_heads:
			for account_type, account_name in iteritems(account_head):
				if account_map.get(account_type) in self.report_dict.get(supply_type).get(supply_category):
					self.report_dict[supply_type][supply_category][account_map.get(account_type)] += \
						flt(tax_details.get((account_name, gst_category), {}).get("amount"), 2)
	# Finby Changes
	if supply_category != "osup_zero" or (supply_category != 'isup_rev' and reverse_charge == "Y"):
		for k, v in iteritems(account_map):
			txval -= self.report_dict.get(supply_type, {}).get(supply_category, {}).get(v, 0)
	
	self.report_dict[supply_type][supply_category]["txval"] += flt(txval, 2)

def get_itc_details(self, reverse_charge='N'):
	# tax_amount changed to base_tax_amount
	itc_amount = frappe.db.sql("""
		select s.gst_category, sum(t.base_tax_amount) as tax_amount, t.account_head, s.eligibility_for_itc, s.reverse_charge
		from `tabPurchase Invoice` s , `tabPurchase Taxes and Charges` t
		where s.docstatus = 1 and t.parent = s.name and s.reverse_charge = %s
		and month(s.posting_date) = %s and year(s.posting_date) = %s and s.company = %s
		and s.company_gstin = %s
		group by t.account_head, s.gst_category, s.eligibility_for_itc
		""",
		(reverse_charge, self.month_no, self.year, self.company, self.gst_details.get("gstin")), as_dict=1)

	itc_details = {}

	for d in itc_amount:
		itc_details.setdefault((d.gst_category, d.eligibility_for_itc, d.reverse_charge, d.account_head),{
			"amount": d.tax_amount
		})

	return itc_details

def get_inter_state_supplies(self, state_number):
	inter_state_supply_taxable_value = frappe.db.sql(""" select sum(s.net_total) as total, s.place_of_supply, s.gst_category
		from `tabSales Invoice` s where s.docstatus = 1 and month(s.posting_date) = %s and year(s.posting_date) = %s
		and s.company = %s and s.company_gstin = %s and s.gst_category in ('Unregistered', 'Registered Composition', 'UIN Holders')
		group by s.gst_category, s.place_of_supply""", (self.month_no, self.year, self.company, self.gst_details.get("gstin")), as_dict=1)
	# tax_amount changed to base_tax_amount
	inter_state_supply_tax = frappe.db.sql(""" select sum(t.base_tax_amount) as tax_amount, s.place_of_supply, s.gst_category
		from `tabSales Invoice` s, `tabSales Taxes and Charges` t
		where t.parent = s.name and s.docstatus = 1 and month(s.posting_date) = %s and year(s.posting_date) = %s
		and s.company = %s and s.company_gstin = %s and s.gst_category in ('Unregistered', 'Registered Composition', 'UIN Holders')
		group by s.gst_category, s.place_of_supply""", (self.month_no, self.year, self.company, self.gst_details.get("gstin")), as_dict=1)

	inter_state_supply_tax_mapping={}
	inter_state_supply_details = {}

	for d in inter_state_supply_tax:
		inter_state_supply_tax_mapping.setdefault(d.place_of_supply, d.tax_amount)

	for d in inter_state_supply_taxable_value:
		inter_state_supply_details.setdefault(
			d.gst_category, []
		)

		if d.place_of_supply:
			if state_number != d.place_of_supply.split("-")[0]:
				inter_state_supply_details[d.gst_category].append({
					"pos": d.place_of_supply.split("-")[0],
					"txval": flt(d.total, 2),
					"iamt": flt(inter_state_supply_tax_mapping.get(d.place_of_supply), 2)
				})
			else:
				osup_det = self.report_dict["sup_details"]["osup_det"]
				osup_det["txval"] = flt(osup_det["txval"] + d.total, 2)
				osup_det["camt"] = flt(osup_det["camt"] + inter_state_supply_tax_mapping.get(d.place_of_supply)/2, 2)
				osup_det["samt"] = flt(osup_det["samt"] + inter_state_supply_tax_mapping.get(d.place_of_supply)/2, 2)

	return inter_state_supply_details

def get_tax_amounts(self, doctype, reverse_charge="N"):
	if doctype == "Sales Invoice":
		tax_template = 'Sales Taxes and Charges'
	elif doctype == "Purchase Invoice":
		tax_template = 'Purchase Taxes and Charges'
	
	# tax_amount changed to base_tax_amount
	tax_amounts = frappe.db.sql("""
		select s.gst_category, sum(t.base_tax_amount) as tax_amount, t.account_head
		from `tab{doctype}` s , `tab{template}` t
		where s.docstatus = 1 and t.parent = s.name and s.reverse_charge = %s
		and month(s.posting_date) = %s and year(s.posting_date) = %s and s.company = %s
		and s.company_gstin = %s
		group by t.account_head, s.gst_category
		""" #nosec
		.format(doctype=doctype, template=tax_template),
		(reverse_charge, self.month_no, self.year, self.company, self.gst_details.get("gstin")), as_dict=1)

	tax_details = {}

	for d in tax_amounts:
		tax_details.setdefault(
			(d.account_head,d.gst_category),{
				"amount": d.get("tax_amount"),
			}
		)

	return tax_details
