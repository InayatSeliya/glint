# Copyright (c) 2024, Inayatali Seliya and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


# class ProfitDistribution(Document):
#     def validate(self):
#         """
#         This function validates the date field and triggers the calculation for profit distribution.
#         It is called automatically before saving the document.
#         """
#         if not self.date:
#             frappe.throw(_("Please set a valid date for profit distribution."))

#     def before_save(self):
#         """
#         This function calculates the total profit, total number of shares,
#         and profit per share before saving the Profit Distribution document.
#         """
#         # Get the total profit up to the selected date
#         total_profit = self.get_total_profit(self.date)

#         # Get the total number of shares issued and purchased up to the selected date
#         total_no_of_shares = self.get_total_shares(self.date)

#         # Calculate profit per share
#         if total_no_of_shares > 0:
#             profit_per_share = total_profit / total_no_of_shares
#         else:
#             profit_per_share = 0.0

#         # Set the calculated values on the Profit Distribution document
#         self.total_profit = abs(total_profit)
#         self.total_no_of_shares = total_no_of_shares
#         self.profit_per_share = profit_per_share

#     def get_total_profit(self, date):
#         """
#         This function fetches the total profit from the 'Profit Declared - GH' account
#         up to the given date.
#         """
#         # Fetch total balance from 'Profit Declared - GH' account up to the selected date
#         result = frappe.db.get_value(
#             "GL Entry",
#             {
#                 "account": "Profit Declared - GH",
#                 "posting_date": ["<=", date]
#             },
#             "sum(debit - credit) as balance"
#         )

#         # If result is None or no balance is found, return 0
#         # return abs(result) makes negative value to Positve
#         return abs(result) if result is not None else 0.0

#     def get_total_shares(self, date):
#         """
#         This function calculates the total number of shares issued and purchased
#         up to the given date using the Share Members Doctype and its Child table.
#         """
#         # Calculate total issued shares from Share Members Records
#         total_issued = frappe.db.get_value(
#             "Share Members Records",
#             {
#                 "parentfield": "share_member_record",  # Link to the child table in Share Members DocType
#                 "date": ["<=", date],
#                 "transfer_type": "Issue"
#             },
#             "sum(no_of_share)"
#         )

#         # Calculate total purchased shares from Share Members Records
#         total_purchased = frappe.db.get_value(
#             "Share Members Records",
#             {
#                 "parentfield": "share_member_record",  # Link to the child table in Share Members DocType
#                 "date": ["<=", date],
#                 "transfer_type": "Purchase"
#             },
#             "sum(no_of_share)"
#         )

#         # If no shares found, return 0
#         total_issued = total_issued if total_issued else 0.0
#         total_purchased = total_purchased if total_purchased else 0.0

#         # Calculate the total number of shares: issued - purchased
#         return total_issued - total_purchased



class ProfitDistribution(Document):
    def validate(self):
        """
        This function validates the date field and triggers the calculation for profit distribution.
        It is called automatically before saving the document.
        """
        if not self.date:
            frappe.throw(_("Please set a valid date for profit distribution."))

    def before_save(self):
        """
        This function calculates the total profit, total number of shares,
        and profit per share before saving the Profit Distribution document.
        """
        # Get the total profit up to the selected date
        total_profit = self.get_total_profit(self.date)

        # Get the total number of shares issued and purchased up to the selected date
        total_no_of_shares = self.get_total_shares(self.date)

        # Calculate profit per share
        if total_no_of_shares > 0:
            profit_per_share = total_profit / total_no_of_shares
        else:
            profit_per_share = 0.0

        # Set the calculated values on the Profit Distribution document
        self.total_profit = abs(total_profit)
        self.total_no_of_shares = total_no_of_shares
        self.profit_per_share = profit_per_share

    def on_submit(self):
        """
        Distribute profit to Share Members accounts on submission.
        """
        if self.profit.distributed:
            frappe.throw(_("Profit has already been distributed for this record."))

        if self.total_profit <= 0:
            frappe.throw(_("Total Profit must be greater then zero to distribute."))

        # Fetch Share Members and distribute profit
        share_members = frappe.get_all(
            "Share Members",
            fields=["name", "share_member_account", "total_shares"],
            filters={"total_shares": [">", 0]}
        )

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
    # return abs(result) makes negative value to Positve
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