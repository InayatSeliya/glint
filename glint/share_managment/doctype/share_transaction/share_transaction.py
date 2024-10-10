# Copyright (c) 2024, Inayatali Seliya and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate

@frappe.whitelist()
def cancel_documents(names):
        """
        Cancel multiple Share Transaction documents in bulk.
        """
        names = frappe.parse_json(names)  # Parse the JSON list of document names
        for name in names:
            doc = frappe.get_doc("Share Transaction", name)  # Get each document
            if doc.docstatus == 1:  # Only cancel if the document is in Submitted state
                doc.cancel()

@frappe.whitelist()
def submit_documents(names):
    """
    Submit multiple Share Transaction documents in bulk.
    """
    # Parse the JSON list of document names
    names = frappe.parse_json(names)
    
    # Iterate through each document name and submit it
    for name in names:
        doc = frappe.get_doc("Share Transaction", name)  # Get each document by name
        
        # Check if document is in Draft status before submitting
        if doc.docstatus == 0:  # 0 = Draft, 1 = Submitted, 2 = Cancelled
            doc.submit()

class ShareTransaction(Document):
    def validate(self):
        self.no_of_shares = self.amount / self.rate
        
    def on_submit(self):
    # Record entry as per transfer type
        if self.transfer_type == "Issue":
            self.add_shares(self.to_share_member)
        elif self.transfer_type == "Purchase":
            self.remove_shares(self.from_share_member)
        elif self.transfer_type == "Transfer":
            # Remove shares from the 'From Share Member'
            self.remove_shares(self.from_share_member)
            # Add shares to the 'To Share Member'
            self.add_shares(self.to_share_member)

    def add_shares(self, share_member):
        """Adds shares to a Share Member's record."""
        share_members_doc = frappe.get_doc("Share Members", share_member)
        # Add a new record to the share_member_record child table
        share_members_doc.append(
            "share_member_record",
            {
                "date": self.date,
                "transfer_type": self.transfer_type,
                "no_of_share": self.no_of_shares,
                "rate": self.rate,
                "amount": self.amount,
            },
        )
        # Save the Share Member document to apply changes
        share_members_doc.save()


    def on_cancel(self):
        # To delete entry from Share Member's record
        if self.transfer_type in ["Issue", "Purchase"]:
        # Determine the appropriate Share Member based on the transfer type
            target_share_member = self.to_share_member if self.transfer_type == "Issue" else self.from_share_member
        # Remove matching entries from Share Member's child table `share_member_record`
            self.remove_share_member_record(
                share_member = target_share_member,
                transfer_type = self.transfer_type,
                date = self.date,
                no_of_share = self.no_of_shares,
                rate = self.rate,
                amount = self.amount
            )

    def remove_share_member_record(self, share_member, transfer_type, no_of_share, rate, amount, date):
        # Fetch the Share Member document
        share_member_doc = frappe.get_doc("Share Members", share_member)
        # Identify matching records in the `share_member_record` child table
        matching_records = [
            record for record in share_member_doc.share_member_record
            if record.transfer_type == transfer_type
            and record.date == date
            and record.no_of_share == no_of_share
            and record.rate == rate
            and record.amount == amount
        ]
        # Remove all matching entries from the child table
        for record in matching_records:
            share_member_doc.share_member_record.remove(record)
        # Save the Share Member document to apply the changes
        share_member_doc.save()



    def remove_shares(self, share_member):
        # This function is created to remove share entry from Share Member's share_member_record if purchase or transfer is made in Share Transaction.
        """Removes shares from a Share Member's record."""
        share_members_doc = frappe.get_doc("Share Members", share_member)
        
        # Convert self.date to datetime format
        transaction_date = getdate(self.date)
        
        # Calculate total shares held by the member on or before current date
        total_share = 0
        for record in share_members_doc.share_member_record:
            # 
            record_date = getdate(record.date)
            if record_date <= transaction_date:
                if record.transfer_type in ["Issue", "Transfer"]:
                    total_share += record.no_of_share
                elif record.transfer_type == "Purchase":
                    total_share -= record.no_of_share

        # Check if shares to be removed exceed the total shares held
        if total_share < self.no_of_shares:
            # Convert No. of Shares in 2 decimal place only for error message.
            total_share_round = round(total_share, 2)

            # Convert date format from YYYY-MM-DD to DD-MM-YYYY for error message only.
            formatted_date = transaction_date.strftime("%d-%m-%Y")
            frappe.throw(f"Insufficient shares. Share Member has only {total_share_round} shares up to {formatted_date}.")

        # Append a record indicating the share removal (Purchase)
        share_members_doc.append(
            "share_member_record",
            {
                "date": self.date,
                "transfer_type": self.transfer_type,
                "no_of_share": self.no_of_shares,
                "rate": self.rate,
                "amount": self.amount,
            },
        )
        share_members_doc.save()

