from __future__ import unicode_literals
import frappe
from erpnext.accounts.utils import get_fiscal_year, flt
import datetime
from frappe.utils.background_jobs import enqueue
from frappe.utils import cint, getdate, get_fullname, get_url_to_form
from frappe.utils.pdf import get_pdf
from frappe.utils.file_manager import save_file
from frappe import _

import jsonpickle
import json
import os
import sys
import time


from WebWhatsappWrapper.webwhatsapi import WhatsAPIDriver
from WebWhatsappWrapper.webwhatsapi.objects.message import Message

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
	module_map = {'Desk':'icon finbyz-desk','Users and Permissions':'icon finbyz-users-and-permissions', \
		'Accounts':'icon finbyz-accounting','Getting Started':'icon finbyz-getting_started', \
		'Learn': 'icon finbyz-learn','Tools': 'icon finbyz-tools',  'Social': 'icon finbyz-social',  \
		'Leaderboard': 'icon finbyz-leaderboard','dashboard': 'icon finbyz-dashboard', \
		'Selling': 'icon finbyz-selling', 'Buying': 'icon finbyz-buying','Stock': 'icon finbyz-stock',\
		'Assets': 'icon finbyz-assets','Projects': 'icon finbyz-projects','CRM': 'icon finbyz-crm', \
		'Support': 'icon finbyz-support','HR': 'icon finbyz-hr', 'Quality Management': 'icon finbyz-quality-management', \
		'Manufacturing': 'icon finbyz-manufacturing', 'Help': 'icon finbyz-help', 'Chemical': 'icon finbyz-chemical', \
		'Exim': 'icon finbyz-exim', 'Settings' : 'icon finbyz-settings', 'Website' : 'icon finbyz-website', \
		'Customization' : 'icon finbyz-customization','Marketplace': 'icon finbyz-marketplace', \
		'Integrations':'icon finbyz-integrations','Core':'icon finbyz-developer', \
		'Ceramic': 'icon finbyz-ceramic','Finbyzweb': 'icon finbyz-finbyzweb',\
		'Engineering': 'icon finbyz-engineering','Transport':'icon finbyz-transport','Education': 'icon finbyz-education'}

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

	module_map = {'Desk':'icon finbyz-desk','Users and Permissions':'icon finbyz-users-and-permissions', \
	'Accounts':'icon finbyz-accounting','Getting Started':'icon finbyz-getting_started', \
	'Learn': 'icon finbyz-learn','Tools': 'icon finbyz-tools',  'Social': 'icon finbyz-social', \
	'Leaderboard': 'icon finbyz-leaderboard','dashboard': 'icon finbyz-dashboard', 'Selling': 'icon finbyz-selling', \
	'Buying': 'icon finbyz-buying','Stock': 'icon finbyz-stock','Assets': 'icon finbyz-assets', \
	'Projects': 'icon finbyz-projects','CRM': 'icon finbyz-crm', 'Support': 'icon finbyz-support',\
	'HR': 'icon finbyz-hr', 'Quality Management': 'icon finbyz-quality-management', \
	'Manufacturing': 'icon finbyz-manufacturing', 'Help': 'icon finbyz-help', 'Chemical': 'icon finbyz-chemical', \
	'Exim': 'icon finbyz-exim','Engineering': 'icon finbyz-engineering','Transport':'icon finbyz-transport'}
	
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

	recipients = doc.recipient.split(",") if doc.recipient.find(",") > 0 else doc.recipient
	if doc.daily_entry_summary:
		message = ""
		for dtype in doc.doctypes:
			body = ''
			total = 0

			table_data = """
				<table class="table table-bordered " style="font-size:100%; float: left;  width:auto; margin:10px 10px 10px 0;">
				<thead><tr><th colspan="2"><b><center>{dtype}</center></b></th></tr></thead>
			""".format(dtype=dtype.document_type)

			query = frappe.db.sql("select owner,count(name) as no_of_entries from `tab{dtype}` where docstatus=1 and CAST(creation AS DATE) = CURDATE() GROUP BY owner".format(dtype=dtype.document_type),as_dict=1)

			if query:
				for data in query:
					total += data.no_of_entries
					user = get_fullname(data.owner)
					body +="""<tr>
								<td><center>{user}</center></td> <td><center><b>{no_of_entries}</b></center></td>
							</tr>
					""".format(user = user,no_of_entries=data.no_of_entries)

				body += """<tr>
							<td><center><b>Total</h5></b><center></td> <td><center><b>{total}</h5></b><center></td>
						</tr>
				""".format(total=total)
			else:
				body += """<tr><td><b><center>0</center></b></td></tr>"""

			table_data += """
						<tbody>{body}</tbody>
				</table>
			""".format(body=body)

			message += """&nbsp;{table_data}&nbsp;
			""".format(table_data=table_data)

		frappe.sendmail(recipients=recipients,
			reference_doctype='User', reference_name="Administrator",
			subject='Daily Entry Summary', message="""<div style="width:100%;">""" + message + """</div>""", now=True)

def daily_transaction_summary_mail():
	doc = frappe.get_doc("Daily Entry Summary","DES-001")

	recipients = doc.recipient.split(",") if doc.recipient.find(",") > 0 else doc.recipient
	if doc.daily_transaction_summary:
		message = ""
		for dtype in doc.doctypes:
			query_col = body = thead = table_data = ''
			total = 0

			query_columns = frappe.db.sql("""select fieldname,label from `tabDocField` where parent='{}' and in_list_view=1 ORDER BY idx""".format(dtype.document_type),as_dict=1)
			thead += """<th><center>Name</center></th>"""

			query_col = "name,"
			for lview in query_columns:
				query_col += "{col},".format(col=lview.fieldname)
				thead += """<th><center>{col}</center></th>""".format(col=lview.label)

			query_columns = query_col[:-1]

			table_data = """<p><h4><b>{dtype}:</b></h4></p></br></br>
				<table class="table table-bordered" style="width:auto;">
				<thead><tr>{thead}</tr></thead>
			""".format(dtype=dtype.document_type,thead=thead)
			
			# select_date = 'transaction_date' if dtype.document_type in ['Purchase Order','Sales Order'] else 'posting_date'
			query = frappe.db.sql("""select {query_columns} from `tab{dtype}` where docstatus = 1 and CAST(creation AS DATE) = CURDATE()""".format(query_columns=query_columns,dtype=dtype.document_type),as_dict=1)
			
			if query:
				for data in query:
					body += "<tr>"
					for key in query_columns.split(","):
						if key == "name":
							url = get_url_to_form(dtype.document_type, data['{key}'.format(key=key)])
							body+= """<td><center><a href={}>{}</a></center></td>""".format(url,data['{key}'.format(key=key)])
						else:
							body += """<td><center>{}</center></td>
						""".format(data['{key}'.format(key=key)])
					body += "</tr>"

			table_data += """
						<tbody>{body}</tbody>
				</table>
			""".format(body=body)

			message += """<br>{table_data}</br>
			""".format(table_data=table_data)
		
		frappe.sendmail(recipients=recipients,
			reference_doctype='User', reference_name="Administrator",
			subject='Daily Transaction Summary', message=message, now=True)


def stock_entry_validate(self, method):
	if self._action == "submit":
		
		validate_additional_cost(self)

def validate_additional_cost(self):
	if self.purpose in ['Material Transfer','Material Transfer for Manufacture','Repack','Manufacture'] and self._action == "submit":
		if abs(round(flt(self.value_difference,1))) != abs(round(flt(self.total_additional_costs,1))):
			frappe.throw("ValuationError: Value difference between incoming and outgoing amount is higher than additional cost")

# Whatsapp Manager: Start

client_list = dict()

@frappe.whitelist()
def get_pdf_whatsapp(doctype,name,attach_document_print,print_format,selected_attachments,mobile_number,description,save_profile):
	selected_attachments = json.loads(selected_attachments)
	attach_document_print = json.loads(attach_document_print)
	if client_list and not frappe.cache().hget('whatsapp_user',frappe.session.user):
		json_driver = jsonpickle.encode(client_list[frappe.session.user],make_refs=False)
		frappe.cache().hset('whatsapp_user',frappe.session.user,json_driver)
	# background_msg_whatsapp(doctype,name,attach_document_print,print_format,selected_attachments,doc,mobile_number,description,save_profile)
	enqueue(background_msg_whatsapp,queue= "long", timeout= 1800, job_name= 'Whatsapp Message', doctype= doctype, name= name, attach_document_print=attach_document_print,print_format= print_format,selected_attachments=selected_attachments,mobile_number=mobile_number,description=description,save_profile=save_profile)

def background_msg_whatsapp(doctype,name,attach_document_print,print_format,selected_attachments,mobile_number,description,save_profile):

	if attach_document_print==1:
		html = frappe.get_print(doctype=doctype, name=name, print_format=print_format)
		filename = "{name}.pdf".format(name=name.replace(" ", "-").replace("/", "-"))
		filecontent = get_pdf(html)

		file_data = save_file(filename, filecontent, doctype,name,is_private=1)
		file_url = file_data.file_url
		site_path = frappe.get_site_path('private','files') + "/{}".format(filename)
		send_media_whatsapp(mobile_number,description,save_profile,selected_attachments,site_path)
		
		remove_file_from_os(site_path)
		frappe.db.sql("delete from `tabFile` where file_name='{}'".format(filename))
		frappe.db.sql("delete from `tabComment` where reference_doctype='{}' and reference_name='{}' and comment_type='Attachment' and comment_email = '{}' and content LIKE '%{}%'".format(doctype,name,frappe.session.user,file_url))

	else:
		send_media_whatsapp(mobile_number,description,save_profile,selected_attachments)


	comment_whatsapp = frappe.new_doc("Comment")
	comment_whatsapp.comment_type = "WhatsApp"
	comment_whatsapp.comment_email = frappe.session.user
	comment_whatsapp.reference_doctype = doctype
	comment_whatsapp.reference_name = name

	comment_whatsapp.content = "Have Sent the Whatsapp Message to <b>{}</b>".format(mobile_number)

	comment_whatsapp.save()

	qr_path = frappe.get_site_path('private','files') + "/{}.png".format(frappe.session.user)
	remove_file_from_os(qr_path)
	frappe.db.sql("delete from `tabFile` where file_name='{}'".format('{}.png'.format(frappe.session.user)))

	if selected_attachments:
		for f_name in selected_attachments:
			attach_url = frappe.get_site_path() + str(frappe.db.get_value('File',f_name,'file_url'))
			remove_file_from_os(attach_url)
			frappe.db.sql("delete from `tabFile` where name='{}'".format(f_name))

	return "Success"

def remove_file_from_os(path):
	if os.path.exists(path):
		os.remove(path)
	
def send_media_whatsapp(mobile_number,description,save_profile,selected_attachments,site_path=None):
	driver_json = frappe.cache().hget('whatsapp_user',frappe.session.user)
	driver = jsonpickle.decode(driver_json)
	driver.connect()
	driver.wait_for_login()
	attach_list = []
	if site_path:
		attach_list.append(site_path)
	if selected_attachments:
		for file_name in selected_attachments:
			attach_url = frappe.get_site_path() + str(frappe.db.get_value('File',file_name,'file_url'))
			attach_list.append(attach_url)

	if mobile_number.find(" ") != -1:
		mobile_number = mobile_number.replace(" ","")
	elif mobile_number.find("+") != -1:
		mobile_number = mobile_number.replace("+","")
	elif len(mobile_number) == 10:
		mobile_number = "91" + mobile_number
	try:
		phone_whatsapp = "{}@c.us".format(str(mobile_number))  # WhatsApp Chat ID # mobile_no with country code
		for path in attach_list:
			driver.send_media(path, phone_whatsapp, description)
		driver.chat_send_message(phone_whatsapp,description)
		frappe.msgprint("Media file was successfully sent to {}".format(mobile_number))

	except:
		frappe.log_error(frappe.get_traceback(),"Error while trying to send the media file.")

	
@frappe.whitelist()
def whatsapp_login_check():
	if frappe.cache().hget('whatsapp_user',frappe.session.user):
		driver_json = frappe.cache().hget('whatsapp_user',frappe.session.user)
		if driver_json:
			driver = jsonpickle.decode(driver_json)
			try:
				if driver.wait_for_login():
					return "Yes"
			except:
				pass
		frappe.cache().hset('whatsapp_user',frappe.session.user,None)
	os.environ["SELENIUM"] = "http://localhost:4444/wd/hub"	
	os.environ["MY_PHONE"] = "91" + frappe.db.get_value('User',frappe.session.user,'mobile_no')

	# profiledir = os.path.join(".", "firefox_cache")
	# if not os.path.exists(profiledir):
	# 	os.makedirs(profiledir)

	driver = WhatsAPIDriver(client="remote", command_executor=os.environ["SELENIUM"],username=frappe.session.user)
	driver.connect()
	if not driver.wait_for_login():
		path_private_files = frappe.get_site_path('private','files')
		path_private_files += '/{}.png'.format(frappe.session.user)

		driver.get_qr(path_private_files)

		doc = frappe.new_doc("File")
		doc.file_name = "{}.png".format(frappe.session.user)
		doc.is_private=1
		doc.file_url = "/private/files/{}.png".format(frappe.session.user)
		doc.save(ignore_permissions=True)

		file_url = "/private/files/{}.png".format(frappe.session.user)
		msg = "<img src={} alt='No Image'>".format(file_url)
		frappe.publish_realtime(event='display_qr_code_image', message=msg,user=frappe.session.user)
		client_list[frappe.session.user] = driver

	else:
		return "Yes"

def validate_user_mobile_no(self,method):
	if self.mobile_no:
		if not self.mobile_no.isdigit():
			frappe.throw("Please Enter Digits Only in Mobile Number.")
		elif len(self.mobile_no) != 10:
			frappe.throw("Please Enter 10 digit Mobile Number.")

@frappe.whitelist()
def get_whatsapp_settings():
	if frappe.db.get_value("System Settings","System Settings","enable_whatsapp"):
		if frappe.db.get_value('User',frappe.session.user,'mobile_no'):
			return "True"

# Whatsapp Manager: End
