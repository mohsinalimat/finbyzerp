# -*- coding: utf-8 -*-
# Copyright (c) 2017, FinByz Tech Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import msgprint, db, _
import json
from frappe.utils import cint, getdate, get_fullname, get_url_to_form,now_datetime

class CustomerMeetings(Document):
	def on_submit(self):
		url = get_url_to_form("Customer Meetings", self.name)
		# url = "http://erp.finbyz.in/desk#Form/Customer%20Meetings/" + self.name
		if self.actionables:
			discussed = "<strong><a href="+url+">"+self.name+"</a>: </strong>"+ "Met "+ self.contact_person + " On "+ self.meeting_from +"<br>" + self.discussion.replace('\n', "<br>")+ "<br><strong>Actionable:</strong>" +self.actionables
		else:
			discussed = "<strong><a href="+url+">"+self.name+"</a>: </strong>"+ "Met "+ self.contact_person + " On "+ self.meeting_from +"<br>" + self.discussion.replace('\n', "<br>")
		cm = frappe.new_doc("Communication")
		cm.subject = self.name
		cm.communication_type = "Comment"
		cm.comment_type = "Comment"
		cm.content = self.discussed
		cm.reference_doctype = "Customer"
		cm.reference_name = self.customer
		cm.save(ignore_permissions=True)


@frappe.whitelist()
def get_events(start, end, filters=None):
	"""Returns events for Gantt / Calendar view rendering.
	:param start: Start date-time.
	:param end: End date-time.
	:param filters: Filters (JSON).
	"""
	filters = json.loads(filters)
	from frappe.desk.calendar import get_event_conditions
	conditions = get_event_conditions("Customer Meetings", filters)

	return frappe.db.sql("""
			select 
				name, meeting_from, meeting_to, organization
			from 
				`tabCustomer Meetings`
			where
				(meeting_from <= %(end)s and meeting_to >= %(start)s) {conditions}
			""".format(conditions=conditions),
				{
					"start": start,
					"end": end
				}, as_dict=True, update={"allDay": 0})