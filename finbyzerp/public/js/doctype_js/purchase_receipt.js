frappe.ui.form.on('Purchase Receipt', {
	refresh: (frm) => {
		frm.set_df_property("company", "read_only", (!frm.doc.__islocal || frm.doc.amended_from) ? 1 : 0);
	},
	onload: (frm) => {
		frm.trigger('naming_series');
	},
	naming_series: function (frm) {
		if (frappe.meta.get_docfield("Sales Order", "series_value", frm.doc.name)){
			if (frm.doc.__islocal && frm.doc.company && !frm.doc.amended_from) {
				console.log('test')
				frappe.call({
					method: "finbyzerp.api.check_counter_series",
					args: {
						'name': frm.doc.naming_series,
						'date': frm.doc.transaction_date,
						'company_series': frm.doc.company_series || null,
					},
					callback: function (e) {
						frm.doc.series_value = e.message;
					}
				});
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
