from __future__ import unicode_literals
import frappe
from erpnext.accounts.utils import get_fiscal_year
import datetime

@frappe.whitelist()
def get_project_name():
	frappe.flags.ignore_account_permission = True
	project_name = frappe.db.get_value("Global Defaults", "Global Defaults","project_name")
	
	return {"project_name":project_name}

def get_fiscal(date):
	fy = get_fiscal_year(date)[0]
	fiscal = frappe.db.get_value("Fiscal Year", fy, 'fiscal')

	return fiscal if fiscal else fy.split("-")[0][2:] + fy.split("-")[1][2:]

def before_naming(self, method):
	if not self.get('amended_from') and not self.get('name'):
		date = self.get("transaction_date") or self.get("posting_date") or  self.get("manufacturing_date") or getdate()
		fiscal = get_fiscal(date)
		self.fiscal = fiscal
		if not self.get('company_series'):
			self.company_series = None
		if self.get('series_value'):
			if self.series_value > 0:
				name = naming_series_name(self.naming_series, fiscal, self.company_series)
				
				check = frappe.db.get_value('Series', name, 'current', order_by="name")
				if check == 0:
					pass
				elif not check:
					frappe.db.sql(f"insert into tabSeries (name, current) values ('{name}', 0)")
				
				frappe.db.sql(f"update `tabSeries` set current = {int(self.series_value) - 1} where name = '{name}'")

def naming_series_name(name, fiscal, company_series=None):
	if company_series:
		name = name.replace('company_series', str(company_series))
	
	name = name.replace('YYYY', str(datetime.date.today().year))
	name = name.replace('YY', str(datetime.date.today().year)[2:])
	name = name.replace('MM', f'{datetime.date.today().month:02d}')
	name = name.replace('DD', f'{datetime.date.today().day:02d}')
	name = name.replace('fiscal', str(fiscal))
	name = name.replace('#', '')
	name = name.replace('.', '')
	
	return name