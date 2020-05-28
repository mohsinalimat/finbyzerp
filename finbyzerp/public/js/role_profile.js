frappe.ui.form.on('Role Profile', {
    setup: function (frm) {
        if (has_common(frappe.user_roles, ["Administrator", "System Manager", "Local Admin"])) {
            if (!frm.roles_editor) {
                var role_area = $('<div style="min-height: 300px">')
                    .appendTo(frm.fields_dict.roles_html.wrapper);
                frm.roles_editor = new frappe.RoleEditor(role_area, frm);
                frm.roles_editor.show();
            } else {
                frm.roles_editor.show();
            }
        }
    }
});