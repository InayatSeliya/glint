# Copyright (c) 2024, Inayatali Seliya and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime

class ProfitDistributionManagement(Document):
    def validate(self):
        """
        This function validates the date field and triggers the calculation for profit distribution.
        It is called automatically before saving the document.
        """
        if not self.date:
            frappe.throw(("Please set a valid date for profit distribution."))

    def autoname(self):
        """
        This function auto-generates the name of the document based on the 'date' field.
        The format will be 'Profit Distribution - d-m-y'.
        """
        if self.date:
            # Ensure the date is a datetime object (if it's a string)
            if isinstance(self.date, str):
                self.date = datetime.strptime(self.date, '%Y-%m-%d')  # Assuming date is stored in 'yyyy-mm-dd' format

            # Format the date as d-m-y
            self.name = "Profit - {}".format(self.date.strftime('%d-%m-%Y'))

    def before_save(self):
        """
        This function calculates the total profit, total number of shares,
        profit per share, and populates the child table with Share Member details
        before saving the Profit Distribution document.
        """
        # Get the total profit up to the selected date
        total_profit = self.get_total_profit(self.date)

        # Get the total number of shares issued and purchased up to the selected date
        total_no_of_shares = self.get_total_shares(self.date)

        # Calculate profit per share
        profit_per_share = total_profit / total_no_of_shares if total_no_of_shares > 0 else 0.0

        # Set the calculated values on the Profit Distribution document
        self.total_profit = total_profit
        self.total_no_of_shares = total_no_of_shares
        self.profit_per_share = profit_per_share

        # Clear existing child table entries
        self.profit_distribution_details = []

        # Fetch all Share Members
        share_members = frappe.get_all("Share Members", fields=["name", "share_member_account"], order_by="name ASC")

        for member in share_members:
            # Calculate total issued shares for the member
            total_issued = frappe.db.get_value(
                "Share Members Records",
                {
                    "parent": member.name,
                    "parentfield": "share_member_record",
                    "transfer_type": "Issue",
                    "date": ["<=", self.date]
                },
                "sum(no_of_share)"
            ) or 0.0

            # Calculate total purchased shares for the member
            total_purchased = frappe.db.get_value(
                "Share Members Records",
                {
                    "parent": member.name,
                    "parentfield": "share_member_record",
                    "transfer_type": "Purchase",
                    "date": ["<=", self.date]
                },
                "sum(no_of_share)"
            ) or 0.0

            # Calculate net shares for the member (issued - purchased)
            total_member_shares = total_issued - total_purchased

            # Skip if the member has no net shares
            if total_member_shares <= 0:
                continue

            # # Skip if no shares are found for the member
            # if not total_member_shares or total_member_shares <= 0:
            #     continue

            # Calculate profit amount for the member
            profit_amount = total_member_shares * profit_per_share

            # Append the data to the child table
            self.append("profit_distribution_details", {
                "share_member": member.name,
                "total_shares": total_member_shares,
                "profit_amount": profit_amount,
                "share_members_account": member.share_member_account  # Fetch account field from Share Members
            })

    def before_submit(self):
        """
        Create a Journal Entry in draft mode to distribute profit.
        Debit: Profit Declared - GH
        Credit: Share Members' accounts based on their profit amounts.
        """
        # Ensure total profit and profit distribution details are set
        if not self.total_profit or not self.profit_distribution_details:
            frappe.throw(_("Cannot create Journal Entry. Total Profit or Profit Distribution Details are missing."))

        # Round the total profit to 2 decimal places
        total_profit = round(self.total_profit, 2)

        # Create Journal Entry
        journal_entry = frappe.new_doc("Journal Entry")
        journal_entry.voucher_type = "Journal Entry"
        journal_entry.posting_date = self.date

        # Add Debit Entry for 'Profit Declared - GH'
        journal_entry.append("accounts", {
            "account": "Profit Declared - GH",  # Replace with your actual account name
            "debit_in_account_currency": total_profit,
            "credit_in_account_currency": 0.0
        })

        total_credit = 0.0  # Track total credit for Share Members

        # Add Credit Entries for Share Members
        for detail in self.profit_distribution_details:
            if not detail.share_members_account:
                frappe.throw(_("Share Member account is missing for {}").format(detail.share_member))

            # Round profit amount for each member
            profit_amount = round(detail.profit_amount, 2)

            journal_entry.append("accounts", {
                "account": detail.share_members_account,
                "debit_in_account_currency": 0.0,
                "credit_in_account_currency": profit_amount
            })

            # Accumulate total credit
            total_credit += profit_amount

        # Round total credit to 2 decimal places
        total_credit = round(total_credit, 2)

        # Calculate rounding difference
        rounding_difference = round(total_profit - total_credit, 2)

        if rounding_difference != 0:
            # Adjust the rounding difference in the last credit entry
            last_entry = journal_entry.accounts[-1]
            last_entry.credit_in_account_currency += rounding_difference

        # Save Journal Entry in draft mode
        journal_entry.save()

        # Link the Journal Entry to the current document
        self.journal_entry = journal_entry.name

        # Notify the user
        frappe.msgprint(("Journal Entry created in draft mode: {}").format(journal_entry.name))

    def get_total_profit(self, date):
        """
        This function fetches the total profit from the 'Profit Declared - GH' account
        up to the given date.
        """
        # Fetch total balance from 'Profit Declared - GH' account up to the selected date
        result = frappe.db.get_value(
            "GL Entry",
            {
                "account": "Profit Declared - GH",
                "posting_date": ["<=", date]
            },
            "sum(debit - credit) as balance"
        )

        # If result is None or no balance is found, return 0
        return abs(result) if result is not None else 0.0

    def get_total_shares(self, date):
        """
        This function calculates the total number of shares issued and purchased
        up to the given date using the Share Members Doctype and its Child table.
        """
        # Calculate total issued shares from Share Members Records
        total_issued = frappe.db.get_value(
            "Share Members Records",
            {
                "parentfield": "share_member_record",  # Link to the child table in Share Members DocType
                "date": ["<=", date],
                "transfer_type": "Issue"
            },
            "sum(no_of_share)"
        )

        # Calculate total purchased shares from Share Members Records
        total_purchased = frappe.db.get_value(
            "Share Members Records",
            {
                "parentfield": "share_member_record",  # Link to the child table in Share Members DocType
                "date": ["<=", date],
                "transfer_type": "Purchase"
            },
            "sum(no_of_share)"
        )

        # If no shares found, return 0
        total_issued = total_issued if total_issued else 0.0
        total_purchased = total_purchased if total_purchased else 0.0

        # Calculate the total number of shares: issued - purchased
        return total_issued - total_purchased