# Copyright (c) 2024, Inayatali Seliya and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class ShareTransaction(Document):
    def validate(self):
        self.no_of_shares = self.amount / self.rate
        
    def on_submit(self):
        if self.transfer_type == "Issue":
            self.add_shares(self.to_share_member)
        elif self.transfer_type == "Purchase":
            self.remove_shares(self.from_share_member)
        elif self.transfer_type == "Transfer":
            self.remove_shares(self.from_share_member)
            self.add_shares(self.to_share_member)

    def add_shares(self, share_member):
        """Adds shares to a Share Member's record."""
        share_members_doc = frappe.get_doc("Share Members", share_member)
        share_members_doc.append(
            "share_member_record",
            {
                "transfer_type": self.transfer_type,
                "no_of_share": self.no_of_shares,
                "rate": self.rate,
                "amount": self.amount,
            },
        )
        share_members_doc.save()

    def remove_shares(self, share_member):
        """Removes shares from a Share Member's record."""
        share_members_doc = frappe.get_doc("Share Members", share_member)

        # Calculate total shares held by the member
        total_share = 0
        for record in share_members_doc.share_member_record:
            if record.transfer_type in ["Issue", "Transfer"]:
                total_share += record.no_of_share
            elif record.transfer_type == "Purchase":
                total_share -= record.no_of_share

        # Check if shares to be removed exceed the total shares held
        if total_share < self.no_of_shares:
            frappe.throw(f"Insufficient shares. Member has only {total_share} shares.")

        # Append a record indicating the share removal (Purchase)
        share_members_doc.append(
            "share_member_record",
            {
                "transfer_type": self.transfer_type,
                "no_of_share": -self.no_of_shares,  # Negative to show removal
                "rate": self.rate,
                "amount": -self.amount,
            },
        )
        share_members_doc.save()

