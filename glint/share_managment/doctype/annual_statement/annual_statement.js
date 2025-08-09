// Copyright (c) 2025, Inayatali Seliya and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Annual Statement", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on('Annual Statement', {
    refresh(frm) {
        if (frm.doc.from_date && frm.doc.to_date) {
            const from = frappe.datetime.str_to_obj(frm.doc.from_date);
            const to = frappe.datetime.str_to_obj(frm.doc.to_date);

            const from_date = `${("0" + from.getDate()).slice(-2)}-${("0" + (from.getMonth() + 1)).slice(-2)}-${from.getFullYear()}`;
            const to_date = `${("0" + to.getDate()).slice(-2)}-${("0" + (to.getMonth() + 1)).slice(-2)}-${to.getFullYear()}`;

            frm.set_value("fy_profit_note", 
                `Profit from ${from_date} to ${to_date} will be added in next FY Year.`);
        }
    },

    from_date(frm) {
        frm.trigger("refresh");
    },

    to_date(frm) {
        frm.trigger("refresh");
    }
});