// Copyright (c) 2024, Inayatali Seliya and contributors
// For license information, please see license.txt

frappe.ui.form.on('Share Transaction', {
    on_submit: function(frm) {
        // Prepare account entries based on transfer type
        let accounts = [];

        // Determine debit and credit accounts based on transfer type
        if (frm.doc.transfer_type === 'Issue' || frm.doc.transfer_type === 'Purchase') {
            accounts.push({
                account: frm.doc.asset_account, // Debit account
                debit_in_account_currency: frm.doc.amount,
                credit_in_account_currency: 0
            });

            accounts.push({
                account: frm.doc.equityliability_account, // Credit account
                debit_in_account_currency: 0,
                credit_in_account_currency: frm.doc.amount
            });
        } else if (frm.doc.transfer_type === 'Transfer') {
            // Implement transfer logic if needed, e.g., debit and credit can be the same account
            accounts.push({
                account: frm.doc.asset_account, // Debit account
                debit_in_account_currency: frm.doc.amount,
                credit_in_account_currency: 0
            });

            accounts.push({
                account: frm.doc.equityliability_account, // Credit account
                debit_in_account_currency: 0,
                credit_in_account_currency: frm.doc.amount
            });
        }

        // Create a new Journal Entry
        frappe.call({
            method: 'frappe.client.insert',
            args: {
                doc: {
                    doctype: 'Journal Entry',
                    voucher_type: 'Journal Entry',
                    posting_date: frm.doc.date,
                    company: frm.doc.company, // Ensure the company is set correctly
                    accounts: accounts
                }
            },
            callback: function(response) {
                if (response.message) {
                    frappe.msgprint(__('Journal Entry created successfully in darft mode: {0}', [response.message.name]));
                }
            }
        });
    }
});


// frappe.ui.form.on("Share Transaction", {
// 	refresh(frm) {

// 	},
// });
