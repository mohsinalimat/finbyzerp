frappe.ui.form.on('Purchase Order', {
	refresh: (frm) => {
		frm.set_df_property("company", "read_only", (!frm.doc.__islocal || frm.doc.amended_from) ? 1 : 0);
	},
	onload: (frm) => {
		frm.trigger('naming_series');
	},
	naming_series: function (frm) {
		if (frm.doc.__islocal && frm.doc.company && !frm.doc.amended_from) {
			frappe.call({
				method: "finbyzerp.api.check_counter_series",
				args: {
					'name': frm.doc.naming_series,
					'date': frm.doc.posting_date,
					'company_series': frm.doc.company_series || null,
				},
				callback: function (e) {
					frm.doc.series_value = e.message;
					frm.refresh_field('series_value')
				}
			});
		}
	},
	company: function (frm) {
		frm.trigger('naming_series');
	},
	posting_date: function (frm) {
		frm.trigger('naming_series');
	},
});