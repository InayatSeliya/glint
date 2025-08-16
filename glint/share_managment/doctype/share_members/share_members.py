# Copyright (c) 2024, Inayatali Seliya and contributors
# For license information, please see license.txt
				
import frappe
from frappe.model.document import Document


class ShareMembers(Document):
    def validate(self):
        # This will save Create Member Code data from Main Code and Sub Code
        if self.main_code and self.sub_code:
            self.member_code = f"{self.main_code}-{self.sub_code}"
    
    def before_save(self):
        if self.get('member_type') == 'Main Member':
            group_name = f"{self.get('main_code')}-{self.get('sub_code')} - {self.get('title')}"
            if not frappe.db.exists('Account', {'account_name': group_name, 'company': self.company}):
                account_group = frappe.get_doc({
                    'doctype': 'Account',
                    'account_name': group_name,
                    'parent_account': 'Shareholders Funds - GH',
                    'is_group': 1,
                    'company': self.company
                })
                account_group.insert()

            main_member_child_account_name = f"{self.get('main_code')}-{self.get('sub_code')} - Self"
            if not frappe.db.exists('Account', {'account_name': main_member_child_account_name, 'company': self.company}):
                main_member_child_account = frappe.get_doc({
                    'doctype': 'Account',
                    'account_name': main_member_child_account_name,
                    'parent_account': account_group.name,
                    'is_group': 0,
                    'company': self.company
                })
                main_member_child_account.insert()

        elif self.get('member_type') == 'Sub Member':
            main_member_account_group = frappe.get_value('Account', {'account_name': self.get('main_member'), 'company': self.company}, 'name')
            if main_member_account_group:
                child_account_name = f"{self.get('main_code')}-{self.get('sub_code')} - {self.get('title')}"
                if not frappe.db.exists('Account', {'account_name': child_account_name, 'company': self.company}):
                    child_account = frappe.get_doc({
                        'doctype': 'Account',
                        'account_name': child_account_name,
                        'parent_account': main_member_account_group,
                        'is_group': 0,
                        'company': self.company
                    })
                    child_account.insert()

    def on_update(self):
        if self.get('member_type') == 'Main Member':
            self.share_member_account = frappe.get_value(
                'Account',
                {'account_name': f"{self.get('main_code')}-{self.get('sub_code')} - Self", 'company': self.company},
                'name'
            )
        elif self.get('member_type') == 'Sub Member':
            self.share_member_account = frappe.get_value(
                'Account',
                {'account_name': f"{self.get('main_code')}-{self.get('sub_code')} - {self.get('title')}", 'company': self.company},
                'name'
            )
        frappe.db.set_value(self.doctype, self.name, 'share_member_account', self.share_member_account)

@frappe.whitelist()
def get_share_member_data(doc):
    # Fetch summary details
    share_summary = frappe.db.sql("""
        SELECT
            SUM(CASE WHEN transfer_type = 'Issue' THEN no_of_share ELSE 0 END) AS total_issued,
            SUM(CASE WHEN transfer_type = 'Issue' THEN amount ELSE 0 END) AS amount_issued,
            SUM(CASE WHEN transfer_type = 'Purchase' THEN no_of_share ELSE 0 END) AS total_purchased,
            SUM(CASE WHEN transfer_type = 'Purchase' THEN amount ELSE 0 END) AS amount_purchased,
            SUM(CASE WHEN transfer_type = 'Reinvest' THEN no_of_share ELSE 0 END) AS total_reinvested,
            SUM(CASE WHEN transfer_type = 'Reinvest' THEN amount ELSE 0 END) AS amount_reinvested
        FROM `tabShare Members Records`
        WHERE parent = %(member_code)s
    """, {"member_code": doc.name}, as_dict=True)[0]
    
    # Fetch transaction ledger
    transactions = frappe.db.sql("""
        SELECT date, name AS share_transaction_id, transfer_type, rate, no_of_shares, amount
        FROM `tabShare Transaction`
        WHERE from_share_member = %(member_code)s
        OR to_share_member = %(member_code)s
        ORDER BY date
    """, {"member_code": doc.name}, as_dict=True)
    
    # Attach these fields to doc
    doc.total_issued = share_summary.get("total_issued", 0)
    doc.amount_issued = share_summary.get("amount_issued", 0)
    doc.total_purchased = share_summary.get("total_purchased", 0)
    doc.amount_purchased = share_summary.get("amount_purchased", 0)
    doc.total_reinvested = share_summary.get("total_reinvested", 0)
    doc.amount_reinvested = share_summary.get("amount_reinvested", 0)
    doc.transactions = transactions
    return doc
