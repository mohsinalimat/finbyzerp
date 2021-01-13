frappe.listview_settings['Batch'] = {
	add_fields: ['reference_name'],
	get_indicator: function(doc) {
        if(doc.reference_name){
            return ["Enabled","blue","reference_name"]
        }
        else{
            return ["Disabled","darkgrey",'']
        }
	}
};