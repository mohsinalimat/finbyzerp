frappe.views.calendar["Meeting"] = {
	field_map: {
		"start": "meeting_from",
		"end": "meeting_to",
		"id": "name",
		"title": "party",
		"allDay": "allDay"
	},
	get_events_method: "finbyzerp.finbyzerp.doctype.meeting.meeting.get_events"
};