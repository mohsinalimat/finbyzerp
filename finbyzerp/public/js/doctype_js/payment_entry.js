frappe.ui.form.on('Payment Entry', {
	refresh: (frm) => {
		if (frm.doc.__islocal){
		frm.set_df_property("company", "read_only", (!frm.doc.__islocal || frm.doc.amended_from) ? 1 : 0);
		}
	},
	onload: (frm) => {
		if (frm.doc.__islocal){
		frm.trigger('naming_series');
		}
		cur_frm.set_query("address", function (doc) {
			return {
				query: "frappe.contacts.doctype.address.address.address_query",
				filters: { link_doctype: "Customer", link_name: doc.party }
			};
		})
		frm.trigger('set_address');
	},
	before_save: function(frm){
		frm.trigger('set_address');
	},
	party: function(frm){
		if(frm.doc.party_type=="Customer" && frm.doc.party){
		frappe.call({
			method:"erpnext.accounts.party.get_party_details",
			args:{
				party: frm.doc.party,
				party_type: frm.doc.party_type
			},
			callback: function(r){
				if(r.message){
					if(frm.doc.address != r.message.customer_address){
						frm.set_value('address', r.message.customer_address)
					}
				}
				frm.refresh();
			}
		})
	}
	},
	naming_series: function (frm) {
		if (frappe.meta.get_docfield("Payment Entry", "series_value", frm.doc.name)){
			if (frm.doc.__islocal && frm.doc.company && !frm.doc.amended_from) {
				frappe.call({
					method: "finbyzerp.api.check_counter_series",
					args: {
						'name': frm.doc.naming_series,
						'date': frm.doc.transaction_date,
						'company_series': frm.doc.company_series || null,
					},
					callback: function (e) {
						frm.set_value('series_value', e.message);
						// frm.doc.series_value = e.message;
					}
				});
				// frm.refresh_field('series_value')
			}
		}
	},
	company: function (frm) {
		frm.trigger('naming_series');
	},
	posting_date: function (frm) {
		frm.trigger('naming_series');
	},
	
});

