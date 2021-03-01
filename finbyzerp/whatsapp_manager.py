from __future__ import unicode_literals
import frappe, os, sys, time, json, tempfile, shutil, datetime
from frappe.utils.pdf import get_pdf
from frappe.utils.file_manager import save_file
from frappe.utils.background_jobs import enqueue
from frappe import _

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
from selenium.common.exceptions import NoSuchElementException


@frappe.whitelist()
def get_whatsapp_settings():
	if frappe.db.get_value("System Settings","System Settings","enable_whatsapp"):
		if frappe.db.get_value('User',frappe.session.user,'mobile_no'):
			return "True"


@frappe.whitelist()
def whatsapp_login_check():
	profiledir = os.path.join(".", "firefox_cache")
	if not os.path.exists(profiledir):
		os.makedirs(profiledir)

	if profiledir:
		profile = webdriver.FirefoxProfile(profiledir)
	else:
		profile = webdriver.FirefoxProfile()
	options = Options()
	options.headless = True
	options.profile = profile

	driver = webdriver.Firefox(options=options,executable_path="/usr/local/bin/geckodriver")
	driver.get('https://web.whatsapp.com/')
	loggedin = False

	local_storage_file = os.path.join(profile.path, "{}.json".format(frappe.session.user))
	if os.path.exists(local_storage_file):
		with open(local_storage_file) as f:
			data = json.loads(f.read())
			driver.execute_script(
			"".join(
				[
					"window.localStorage.setItem('{}', '{}');".format(
						k, v.replace("\n", "\\n") if isinstance(v, str) else v
					)
					for k, v in data.items()
				]
			))
		driver.refresh()
	WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.two' + ',' + 'canvas')))
	try:
		driver.find_element_by_css_selector('.two')
		loggedin = True
	except NoSuchElementException:
		driver.find_element_by_css_selector('canvas')
	except:
		pass

	if not loggedin:
		generate_qr_code(driver,profile.path)
		enqueue(save_whatsapp_profile,queue= "long", timeout= 1800, job_name= 'Save Whatsapp Profile', command_executor = driver.command_executor._url,session_id = driver.session_id,profile_path=profile.path)

	else:
		driver.quit()

def generate_qr_code(driver,profile_path):
	path_private_files = frappe.get_site_path('private','files') + '/{}.png'.format(frappe.session.user)

	WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'canvas')))
	qr = driver.find_element_by_css_selector('canvas')
	fd = os.open(path_private_files, os.O_RDWR | os.O_CREAT)
	fn_png = os.path.abspath(path_private_files)
	qr.screenshot(fn_png)

	doc = frappe.new_doc("File")
	doc.file_name = "{}.png".format(frappe.session.user)
	doc.is_private=1
	doc.file_url = "/private/files/{}.png".format(frappe.session.user)
	doc.save(ignore_permissions=True)

	file_url = "/private/files/{}.png".format(frappe.session.user)
	msg = "<img src={} alt='No Image'>".format(file_url)
	# frappe.publish_realtime(event='display_qr_code_image', message=msg,user=frappe.session.user)
	frappe.msgprint(msg,title="Scan below QR Code in Whatsapp Web")

def save_whatsapp_profile(command_executor,session_id,profile_path):
	loggedin = False
	driver = create_driver_session(session_id, command_executor)
	WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.two')))
	try:
		driver.find_element_by_css_selector('.two')
		loggedin = True
	except:
		pass
	
	profiledir = os.path.join(".", "firefox_cache")
	if loggedin:
		for item in os.listdir(profile_path):
			if item in ["parent.lock", "lock", ".parentlock"]:
				continue
			s = os.path.join(profile_path, item)
			d = os.path.join(profiledir, item)
			if os.path.isdir(s):
				shutil.copytree(
					s,
					d,
					ignore=shutil.ignore_patterns(
						"parent.lock", "lock", ".parentlock"
					),
				)
			else:
				shutil.copy2(s, d)

		with open(os.path.join(profiledir,"{}.json".format(frappe.session.user)), "w") as f:
			f.write(json.dumps(driver.execute_script("return window.localStorage;")))
	
	else:
		frappe.log_error("Not LoggedIn")

	driver.quit()
			
@frappe.whitelist()
def get_pdf_whatsapp(doctype,name,attach_document_print,print_format,selected_attachments,mobile_number,description):
	selected_attachments = json.loads(selected_attachments)
	attach_document_print = json.loads(attach_document_print)

	if mobile_number.find(" ") != -1:
		mobile_number = mobile_number.replace(" ","")
	if mobile_number.find("+") != -1:
		mobile_number = mobile_number.replace("+","")
	if len(mobile_number) != 10:
		frappe.throw("Please Enter Only 10 Digit Contact Number.")
	whatsapp_login_check()
	# background_msg_whatsapp(doctype,name,attach_document_print,print_format,selected_attachments,mobile_number,description)
	enqueue(background_msg_whatsapp,queue= "long", timeout= 1800, job_name= 'Whatsapp Message', doctype= doctype, name= name, attach_document_print=attach_document_print,print_format= print_format,selected_attachments=selected_attachments,mobile_number=mobile_number,description=description)

def background_msg_whatsapp(doctype,name,attach_document_print,print_format,selected_attachments,mobile_number,description):
	if attach_document_print==1:
		html = frappe.get_print(doctype=doctype, name=name, print_format=print_format)
		filename = "{name}.pdf".format(name=name.replace(" ", "-").replace("/", "-"))
		filecontent = get_pdf(html)

		file_data = save_file(filename, filecontent, doctype,name,is_private=1)
		file_url = file_data.file_url
		site_path = frappe.get_site_path('private','files') + "/{}".format(filename)
		send_media_whatsapp(mobile_number,description,selected_attachments,site_path)
		
		remove_file_from_os(site_path)
		frappe.db.sql("delete from `tabFile` where file_name='{}'".format(filename))
		frappe.db.sql("delete from `tabComment` where reference_doctype='{}' and reference_name='{}' and comment_type='Attachment' and comment_email = '{}' and content LIKE '%{}%'".format(doctype,name,frappe.session.user,file_url))

	else:
		send_media_whatsapp(mobile_number,description,selected_attachments)


	comment_whatsapp = frappe.new_doc("Comment")
	comment_whatsapp.comment_type = "WhatsApp"
	comment_whatsapp.comment_email = frappe.session.user
	comment_whatsapp.reference_doctype = doctype
	comment_whatsapp.reference_name = name
	if attach_document_print==1:
		comment_whatsapp.content = "Have Sent the Whatsapp Message: <b>'{}'</b> to <b>{}</b> with Print <b>'{}'</b>".format(description,mobile_number,print_format)
	else:
		comment_whatsapp.content = "Have Sent the Whatsapp Message: <b>'{}'</b> to <b>{}</b>".format(description,mobile_number)

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

	
def send_media_whatsapp(mobile_number,description,selected_attachments,site_path=None):

	if len(mobile_number) == 10:
		mobile_number = "91" + mobile_number

	profiledir = os.path.join(".", "firefox_cache")
	profile = webdriver.FirefoxProfile(profiledir)

	options = Options()
	options.headless = True
	options.profile = profile

	driver = webdriver.Firefox(options=options,executable_path="/usr/local/bin/geckodriver")
	driver.get('https://web.whatsapp.com/')
	local_storage_file = os.path.join(profile.path, "{}.json".format(frappe.session.user))
	if os.path.exists(local_storage_file):
		with open(local_storage_file) as f:
			data = json.loads(f.read())
			driver.execute_script(
			"".join(
				[
					"window.localStorage.setItem('{}', '{}');".format(
						k, v.replace("\n", "\\n") if isinstance(v, str) else v
					)
					for k, v in data.items()
				]
			))
		driver.refresh()
	WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.two')))

	link = "https://web.whatsapp.com/send?phone='{}'&text&source&data&app_absent".format(mobile_number)
	driver.get(link)
	attach_list = []
	if site_path:
		attach_list.append(site_path)

	if selected_attachments:
		for file_name in selected_attachments:
			attach_url = frappe.get_site_path() + str(frappe.db.get_value('File',file_name,'file_url'))
			attach_list.append(attach_url)

	if description:
		WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="main"]/footer/div[1]/div[2]/div/div[2]')))
		try:
			input_box = driver.find_element_by_xpath('//*[@id="main"]/footer/div[1]/div[2]/div/div[2]')
			input_box.send_keys(description)
			input_box.send_keys(Keys.ENTER)
		except:
			frappe.log_error(frappe.get_traceback(),"Error while trying to send the media file.")
 
	if attach_list:
		try:
			for path in attach_list:
				path_url = frappe.utils.get_bench_path() + "/sites" + path[1:]
				WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'span[data-icon="clip"]')))
				driver.find_element_by_css_selector('span[data-icon="clip"]').click()
				attach=driver.find_element_by_css_selector('input[type="file"]')
				attach.send_keys(path_url)

				WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="app"]/div/div/div[2]/div[2]/span/div/span/div/div/div[2]/span/div/div')))
				whatsapp_send_button = driver.find_element_by_xpath('//*[@id="app"]/div/div/div[2]/div[2]/span/div/span/div/div/div[2]/span/div/div')
				whatsapp_send_button.click()
		except:
			frappe.log_error(frappe.get_traceback(),"Error while trying to send the whatsapp message.")
	time.sleep(10)
	driver.quit()

def remove_file_from_os(path):
	if os.path.exists(path):
		os.remove(path)

def create_driver_session(session_id, executor_url):

    # Save the original function, so we can revert our patch
    org_command_execute = RemoteWebDriver.execute

    def new_command_execute(self, command, params=None):
        if command == "newSession":
            # Mock the response
            return {'success': 0, 'value': None, 'sessionId': session_id}
        else:
            return org_command_execute(self, command, params)

    # Patch the function before creating the driver object
    RemoteWebDriver.execute = new_command_execute

    new_driver = webdriver.Remote(command_executor=executor_url, desired_capabilities=DesiredCapabilities.FIREFOX.copy())
    new_driver.session_id = session_id

    # Replace the patched function with original function
    RemoteWebDriver.execute = org_command_execute

    return new_driver


# @frappe.whitelist()
# def send_whatsapp_msg(doctype,name,attach_document_print,print_format,selected_attachments,mobile_number,description):
# 	selected_attachments = json.loads(selected_attachments)
# 	attach_document_print = json.loads(attach_document_print)

# 	if mobile_number.find(" ") != -1:
# 		mobile_number = mobile_number.replace(" ","")
# 	if mobile_number.find("+") != -1:
# 		mobile_number = mobile_number.replace("+","")
# 	if len(mobile_number) != 10:
# 		frappe.throw("Please Enter Only 10 Digit Contact Number.")
	
# 	check_whatsapp_login()
# 	enqueue(background_msg_whatsapp,queue= "long", timeout= 1800, job_name= 'Whatsapp Message', doctype= doctype, name= name, attach_document_print=attach_document_print,print_format= print_format,selected_attachments=selected_attachments,mobile_number=mobile_number,description=description)


# def check_whatsapp_login():
# 	profiledir = os.path.join(".", "firefox_cache")
# 	if not os.path.exists(profiledir):
# 		os.makedirs(profiledir)

# 	if profiledir:
# 		profile = webdriver.FirefoxProfile(profiledir)
# 	else:
# 		profile = webdriver.FirefoxProfile()

# 	options = Options()
# 	options.headless = True
# 	options.profile = profile

# 	driver = webdriver.Firefox(options=options,executable_path="/usr/local/bin/geckodriver")
# 	driver.get('https://web.whatsapp.com/')
# 	loggedin = False

# 	local_storage_file = os.path.join(profile.path, "{}.json".format(frappe.session.user))
# 	if os.path.exists(local_storage_file):
# 		with open(local_storage_file) as f:
# 			data = json.loads(f.read())
# 			driver.execute_script(
# 			"".join(
# 				[
# 					"window.localStorage.setItem('{}', '{}');".format(
# 						k, v.replace("\n", "\\n") if isinstance(v, str) else v
# 					)
# 					for k, v in data.items()
# 				]
# 			))
# 		driver.refresh()
# 	WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.two' + ',' + 'canvas')))
# 	try:
# 		driver.find_element_by_css_selector('.two')
# 		loggedin = True
# 	except NoSuchElementException:
# 		driver.find_element_by_css_selector('canvas')
# 	except:
# 		pass

# 	if not loggedin:
# 		return generate_qr_code(driver,profile.path)
# 	else:
# 		return True

# def generate_qr_code(driver,profile_path):
# 	path_private_files = frappe.get_site_path('private','files') + '/{}.png'.format(frappe.session.user)

# 	WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'canvas')))
# 	qr = driver.find_element_by_css_selector('canvas')
# 	fd = os.open(path_private_files, os.O_RDWR | os.O_CREAT)
# 	fn_png = os.path.abspath(path_private_files)
# 	qr.screenshot(fn_png)

# 	doc = frappe.new_doc("File")
# 	doc.file_name = "{}.png".format(frappe.session.user)
# 	doc.is_private=1
# 	doc.file_url = "/private/files/{}.png".format(frappe.session.user)
# 	doc.save(ignore_permissions=True)

# 	file_url = "/private/files/{}.png".format(frappe.session.user)
# 	msg = "<img src={} alt='No Image'>".format(file_url)
# 	# frappe.publish_realtime(event='display_qr_code_image', message=msg,user=frappe.session.user)
	
# 	frappe.msgprint(msg,title="Scan below QR Code in Whatsapp Web")
# 	enqueue(save_whatsapp_profile,queue= "long", timeout= 1800, job_name= 'Save Whatsapp Profile', driver = driver,profile_path=profile_path)
	
# def save_whatsapp_profile(driver,profile_path):
# 	loggedin = False
# 	WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.two')))
# 	try:
# 		driver.find_element_by_css_selector('.two')
# 		loggedin = True
# 	except:
# 		pass
	
# 	profiledir = os.path.join(".", "firefox_cache")
# 	if loggedin:
# 		for item in os.listdir(profile_path):
# 			if item in ["parent.lock", "lock", ".parentlock"]:
# 				continue
# 			s = os.path.join(profile_path, item)
# 			d = os.path.join(profiledir, item)
# 			if os.path.isdir(s):
# 				shutil.copytree(
# 					s,
# 					d,
# 					ignore=shutil.ignore_patterns(
# 						"parent.lock", "lock", ".parentlock"
# 					),
# 				)
# 			else:
# 				shutil.copy2(s, d)

# 		with open(os.path.join(profiledir,"{}.json".format(frappe.session.user)), "w") as f:
# 			f.write(json.dumps(driver.execute_script("return window.localStorage;")))

# 	else:
# 		frappe.throw("Please try again")

# 	driver.quit()

