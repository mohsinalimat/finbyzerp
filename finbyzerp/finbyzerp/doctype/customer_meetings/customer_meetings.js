var calculate_total_expense = function(frm) {
    var total_expense = flt(frm.doc.local_travel_expense) + flt(frm.doc.train_tickets) + flt(frm.doc.flight_ticket) + flt(frm.doc.food_expense)+flt(frm.doc.lodging_cost);
    frm.set_value("total_expense", total_expense);
};
frappe.ui.form.on("Customer Meetings", "local_travel_expense", function(frm) {
    calculate_total_expense(frm);
});
frappe.ui.form.on("Customer Meetings", "train_tickets", function(frm) {
    calculate_total_expense(frm);
});
frappe.ui.form.on("Customer Meetings", "flight_ticket", function(frm) {
    calculate_total_expense(frm);
});
frappe.ui.form.on("Customer Meetings", "food_expense", function(frm) {
    calculate_total_expense(frm);
});
frappe.ui.form.on("Customer Meetings", "lodging_cost", function(frm) {
    calculate_total_expense(frm);
});

frappe.ui.form.on("Customer Meetings",{
	refresh: function(frm){
		frm.fields_dict.contact_person.get_query = function(doc) {
			return {
				query: 'frappe.contacts.doctype.contact.contact.contact_query',
				filters: {
					link_doctype: "Customer",
					link_name: frm.doc.customer
				}
			}
		};
		frm.fields_dict.meeting_party_representative.grid.get_field("contact").get_query = function(doc,cdt,cdn) {
			return {
				query: 'frappe.contacts.doctype.contact.contact.contact_query',
				filters: {
					link_doctype: "Customer",
					link_name: frm.doc.customer
				}
			}
		}
		frm.fields_dict.address.get_query = function(doc) {
			return {
				query: 'frappe.contacts.doctype.address.address.address_query',
				filters: {
					link_doctype: "Customer",
					link_name: frm.doc.customer
				}
			}
		};
	},
	customer: function(frm){
		frappe.call({
			method:"erpnext.accounts.party.get_party_details",
			args:{
				party: frm.doc.customer,
				party_type: "Customer"
			},
			callback: function(r){
				if(r.message){
					frm.set_value('contact_person', r.message.contact_person)
					frm.set_value('email_id', r.message.contact_email)
					frm.set_value('mobile_no', r.message.contact_mobile)
					frm.set_value('contact', r.message.contact_dispaly)
					frm.set_value('address', r.message.customer_address)
					frm.set_value('address_display', r.message.address_display)
				}
			}
		})
	}
})
// Get Customer Contact & Details
// frappe.ui.form.on('Customer Meetings', 'customer', function(frm){
// 	// frappe.call({
// 	// 	'method': 'frappe.client.get_value',
// 	// 	'args': {
// 	// 		'doctype': 'Contact',
// 	// 		'fieldname': 'name',
// 	// 		  'filters': {
// 	// 			'customer': frm.doc.customer,
// 	// 			'is_primary_contact': 1
// 	// 		  }
// 	// 		},
// 	// 	   callback: function(r){
// 	// 			frm.set_value('contact', r.message.name);
// 	// 	   }
// 	// });
// 	frappe.db.get_value("Contact",{'customer':frm.doc.customer,'is_primary_contact':1},'name', function(r){
// 		if (r.name){
// 			frm.set_value("contact",r.name)
// 		}
// 	})
// });

// frappe.ui.form.on("Customer Meetings", "contact", function(frm) {
//   frappe.model.with_doc("Contact", frm.doc.contact, function() { 
//      var contact = frappe.model.get_doc("Contact", frm.doc.contact);
//      frm.set_value("email_id", contact.email_id);
// 	 frm.set_value("mobile_no", contact.mobile_no);
//   });
// });

// Get Customer Address and Display
// frappe.ui.form.on('Customer Meetings', 'customer', function(frm){
// 	frappe.call({
// 		'method': 'frappe.client.get_value',
// 		'args': {
// 			'doctype': 'Address',
// 			'fieldname': 'name',
// 			  'filters': {
// 				'customer': frm.doc.customer,
// 				'is_primary_address': 1
// 			  }
// 			},
// 		   callback: function(r){
// 				frm.set_value('address', r.message.name);
// 		   }
// 	});
// });


// frappe.ui.form.on("Customer Meetings", "address", function(frm, cdt, cdn) {
// 	if (frm.doc.address) {
// 	return frappe.call({
// 		method: "erpnext.utilities.doctype.address.address.get_address_display",
// 		args: {
// 			"address_dict": frm.doc.address
// 		},
// 		callback: function(r) {
// 			if(r.message)
// 				frm.set_value("address_display", r.message);
// 		}
// 	});
// 	}
// });

