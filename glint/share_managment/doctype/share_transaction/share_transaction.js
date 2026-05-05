// Copyright (c) 2024, Inayatali Seliya and contributors
// For license information, please see license.txt

frappe.ui.form.on("Share Transaction", {
	// Auto-fetch when To Share Member is selected
	to_share_member: function(frm) {
		if (frm.doc.to_share_member) {
			// Fetch Share Member document to get the Share Member Account
			frappe.call({
				method: 'frappe.client.get',
				args: {
					doctype: 'Share Members',
					name: frm.doc.to_share_member
				},
				callback: function(response) {
					if (response.message) {
						const share_member = response.message;
						// Set Equity/Liability Account from Share Member's account
						frm.set_value('equityliability_account', share_member.share_member_account);
						// Set Asset Account to 'Cash - GH'
						frm.set_value('asset_account', 'Cash - GH');
					}
				}
			});
		}
	},

	// Auto-fetch when From Share Member is selected
	from_share_member: function(frm) {
		if (frm.doc.from_share_member) {
			// Fetch Share Member document to get the Share Member Account
			frappe.call({
				method: 'frappe.client.get',
				args: {
					doctype: 'Share Members',
					name: frm.doc.from_share_member
				},
				callback: function(response) {
					if (response.message) {
						const share_member = response.message;
						// Set Equity/Liability Account to 'Cash - GH'
						frm.set_value('equityliability_account', 'Cash - GH');
						// Set Asset Account from Share Member's account
						frm.set_value('asset_account', share_member.share_member_account);
					}
				}
			});
		}
	}
});
