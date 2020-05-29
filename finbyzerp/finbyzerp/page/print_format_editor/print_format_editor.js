frappe.pages['print-format-editor'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Print Format Editor',
		single_column: true
	});
}