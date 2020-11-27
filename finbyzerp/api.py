from __future__ import unicode_literals
import frappe
from erpnext.accounts.utils import get_fiscal_year
import datetime
from frappe.utils import cint, getdate

def before_insert(self, method):
	opening_naming_series(self)

@frappe.whitelist()
def get_project_name():
	frappe.flags.ignore_account_permission = True
	project_name = frappe.db.get_value("Global Defaults", "Global Defaults","project_name")
	
	return {"project_name":project_name}


def sales_invoice_on_submit(self, method):
	if self.get('eway_bill_json_required'):
		if not self.billing_address_gstin:
			frappe.throw("Billing Address GSTIN is required.")
		
		if not self.customer_gstin:
			frappe.throw("Customer GSTIN is required.")
		
		if not self.distance:
			frappe.throw("Distance (in km) is required.")
		
		if self.distance > 4000:
			frappe.throw("Distance cannot be greater than 4000 kms")
		
		if not self.customer_address:
			frappe.throw("Customer Address is required.")

		if self.customer_address:
			if not frappe.db.get_value("Address", self.customer_address, 'pincode'):
				frappe.throw("Customer Postal Code is required.")
		
		for item in self.items:
			if not item.gst_hsn_code and not item.is_non_gst:
				frappe.throw("Row: {} HSN/SAC is reuired for item {}".format(item.idx, item.item_code))
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
					frappe.db.sql("insert into tabSeries (name, current) values ('{}', 0)".format(name))

				frappe.db.sql("update `tabSeries` set current = {} where name = '{}'".format(cint(self.series_value) - 1, name))

def naming_series_name(name, fiscal = None, company_series=None):
	if fiscal == None:
		fiscal = ''
	if company_series:
		name = name.replace('company_series', str(company_series))
	
	name = name.replace('YYYY', str(datetime.date.today().year))
	name = name.replace('YY', str(datetime.date.today().year)[2:])
	name = name.replace('MM', '{0:0=2d}'.format(datetime.date.today().month))
	name = name.replace('DD', '{0:0=2d}'.format(datetime.date.today().day))
	name = name.replace('fiscal', str(fiscal))
	name = name.replace('#', '')
	name = name.replace('.', '')
	
	return name

@frappe.whitelist()
def check_counter_series(name, company_series = None, date = None):
	
	if not date:
		date = datetime.date.today()
	
	
	fiscal = get_fiscal(date)
	
	name = naming_series_name(name, fiscal, company_series)
	
	check = frappe.db.get_value('Series', name, 'current', order_by="name")
	
	if check == 0:
		return 1
	elif check == None:
		frappe.db.sql("insert into tabSeries (name, current) values ('{}', 0)".format(name))
		return 1
	else:
		return int(frappe.db.get_value('Series', name, 'current', order_by="name")) + 1

def opening_naming_series(self):
	if not self.name and self.is_opening == "Yes":
		self.naming_series = 'O' + self.naming_series

@frappe.whitelist()
def get_desktop_settings():
	from frappe.config import get_modules_from_all_apps_for_user
	from frappe.desk.moduleview import get_home_settings, get_links
	all_modules = get_modules_from_all_apps_for_user()
	home_settings = get_home_settings()
	# module_map = {'Desk':'/files/desk_icon.png','Users and Permissions':'/files/desk_icon.png','Accounts':'icon finbyz-accounting','Getting Started':'icon finbyz-getting_started'}
	module_map = {'Desk':'icon finbyz-desk','Users and Permissions':'icon finbyz-users-and-permissions','Accounts':'icon finbyz-accounting','Getting Started':'icon finbyz-getting_started', 'Learn': 'icon finbyz-learn','Tools': 'icon finbyz-tools',  'Social': 'icon finbyz-social',  'Leaderboard': 'icon finbyz-leaderboard','dashboard': 'icon finbyz-dashboard', 'Selling': 'icon finbyz-selling', 'Buying': 'icon finbyz-buying','Stock': 'icon finbyz-stock','Assets': 'icon finbyz-assets','Projects': 'icon finbyz-projects','CRM': 'icon finbyz-crm', 'Support': 'icon finbyz-support','HR': 'icon finbyz-hr', 'Quality Management': 'icon finbyz-quality-management', 'Manufacturing': 'icon finbyz-manufacturing', 'Help': 'icon finbyz-help', 'Chemical': 'icon finbyz-chemical', 'Exim': 'icon finbyz-exim', 'Settings' : 'icon finbyz-settings', 'Website' : 'icon finbyz-website', 'Customization' : 'icon finbyz-customization','Marketplace': 'icon finbyz-marketplace','Integrations':'icon finbyz-integrations','Developer':'icon finbyz-developer'}
	modules_by_name = {}
	for m in all_modules:
		if m['module_name'] in module_map.keys():
			m['icon'] = module_map[m['module_name']]
		modules_by_name[m['module_name']] = m
	module_categories = ['Modules', 'Domains', 'Places', 'Administration']
	user_modules_by_category = {}

	user_saved_modules_by_category = home_settings.modules_by_category or {}
	user_saved_links_by_module = home_settings.links_by_module or {}

	def apply_user_saved_links(module):
		module = frappe._dict(module)
		all_links = get_links(module.app, module.module_name)
		module_links_by_name = {}
		for link in all_links:
			module_links_by_name[link['name']] = link

		if module.module_name in user_saved_links_by_module:
			user_links = frappe.parse_json(user_saved_links_by_module[module.module_name])
			module.links = [module_links_by_name[l] for l in user_links if l in module_links_by_name]

		return module

	for category in module_categories:
		if category in user_saved_modules_by_category:
			user_modules = user_saved_modules_by_category[category]
			user_modules_by_category[category] = [apply_user_saved_links(modules_by_name[m]) \
				for m in user_modules if modules_by_name.get(m)]
		else:
			user_modules_by_category[category] = [apply_user_saved_links(m) \
				for m in all_modules if m.get('category') == category]

	# filter out hidden modules
	if home_settings.hidden_modules:
		for category in user_modules_by_category:
			hidden_modules = home_settings.hidden_modules or []
			modules = user_modules_by_category[category]
			user_modules_by_category[category] = [module for module in modules if module.module_name not in hidden_modules]

	return user_modules_by_category

@frappe.whitelist()
def get_options_for_global_modules():
	# frappe.msgprint('call')
	from frappe.config import get_modules_from_all_apps
	all_modules = get_modules_from_all_apps()

	blocked_modules = frappe.get_doc('User', 'Administrator').get_blocked_modules()
	module_map = {'Desk':'icon finbyz-desk','Users and Permissions':'icon finbyz-users-and-permissions','Accounts':'icon finbyz-accounting','Getting Started':'icon finbyz-getting_started', 'Learn': 'icon finbyz-learn','Tools': 'icon finbyz-tools',  'Social': 'icon finbyz-social',  'Leaderboard': 'icon finbyz-leaderboard','dashboard': 'icon finbyz-dashboard', 'Selling': 'icon finbyz-selling', 'Buying': 'icon finbyz-buying','Stock': 'icon finbyz-stock','Assets': 'icon finbyz-assets','Projects': 'icon finbyz-projects','CRM': 'icon finbyz-crm', 'Support': 'icon finbyz-support','HR': 'icon finbyz-hr', 'Quality Management': 'icon finbyz-quality-management', 'Manufacturing': 'icon finbyz-manufacturing', 'Help': 'icon finbyz-help', 'Chemical': 'icon finbyz-chemical', 'Exim': 'icon finbyz-exim'}
	# frappe.msgprint(str(all_modules))
	options = []
	for module in all_modules:
		module = frappe._dict(module)
		# frappe.msgprint(str(module))
		options.append({
			'category': module.category,
			'label': module.label,
			'value': module.module_name,
			'checked': module.module_name not in blocked_modules
		})

	return options

def daily_entry_summary_mail():
	doc = frappe.get_doc("Daily Entry Summary","DES-001")
	header = body = ''
	for dtype in doc.doctypes:
		total = 0
		header += """<tr>
						<th>{dtype}</th>
					</tr>
		""".format(dtype=dtype.document_type)

		query = frappe.db.sql("select owner,count(name) as no_of_entries from `tab{dtype}` where CAST(creation AS DATE) = CURDATE() GROUP BY owner".format(dtype=dtype.document_type),as_dict=1)
		if query:
			for data in query:
				total += data.no_of_entries
				body +="""<tr>
							<td>{owner}: <b>{no_of_entries}</b></td>
						</tr>""".format(owner = data.owner,no_of_entries=data.no_of_entries)

			body += """<tr>
						<td>Total : <h4><b>{total}</b></h4></td>
						</tr>
			""".format(total=total)

	message = """<h3><b>Today Entry List</b></h3></br></br>
				<table class="table table-bordered" style="margin: 0; font-size:80%;">
				<thead>{header}</thead>
				<tbody>{body}</tbody>
				</table>
	""".format(header=header,body=body)

	frappe.sendmail(recipients=['milan.pethani@finbyz.tech'],
		sender="milanpethani592@gmail.com",
		reference_doctype='User', reference_name="Administrator",
		subject='Daily Entry Summary', message=message, now=True)