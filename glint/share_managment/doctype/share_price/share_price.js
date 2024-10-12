// Copyright (c) 2024, Inayatali Seliya and contributors
// For license information, please see license.txt

frappe.ui.form.on("Share Price", {
    refresh: function(frm) {
        if (!frm.is_new()) {
            frm.set_df_property('share_price', 'read_only', 1);  // This makes Share Price read only
            frm.set_df_property('update_on', 'read_only', 1); // This makes Date read only
        }
    },

    after_save: function(frm) {
        // Rrefresh the from imediately after document is saved
        frm.reload_doc();
    }
    
});
