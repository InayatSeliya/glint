// Copyright (c) 2024, Inayatali Seliya and contributors
// For license information, please see license.txt

frappe.ui.form.on("Share Members", {
	refresh(frm) {
        if (!frm.is_new()) {
            // Make multiple fields read-only
            ['member_type', 'main_code', 'sub_code', 'title'].forEach(field => {
                frm.set_df_property(field, 'read_only', 1);
            });
        }
	},
});
