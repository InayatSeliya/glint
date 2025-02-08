# Copyright (c) 2025, Inayatali Seliya and contributors
# For license information, please see license.txt

from frappe.model.document import Document
from frappe.utils import flt, getdate, format_date, fmt_money
import frappe

class ShareMemberProfileReport(Document):

    def before_save(self):
        if not self.share_price:
            frappe.throw(("Please select a Share Price Date before saving the report."))
        self.populate_sub_member_share_details()

    def populate_sub_member_share_details(self):
        from_date = self.from_date
        to_date = self.to_date

        # Fetch sub-members linked to the selected main member
        sub_members = frappe.get_all(
            "Share Members",
            filters={"main_member": self.share_member},
            fields=["name", "title", "member_code"]
        )

        # Include the Main Member itself
        all_members = [{"name": self.share_member, "title": self.name1, "member_code": self.member_code}]
        all_members.extend(sub_members)

        # Sort the all_members list by member_code in ascending order
        all_members = sorted(all_members, key=lambda x: x['member_code'])

        # Clear existing table data
        self.sub_member_share_details = []

        total_issued_shares = 0
        total_share_issued_amount = 0
        total_reinvested_shares = 0
        total_share_reinvested_amount = 0
        total_purchased_shares = 0
        total_share_purchase_amount = 0

        # Fetch and append share details for each member
        for member in all_members:
            share_details = self.get_share_details_for_member(member["name"], from_date, to_date)
            self.append("sub_member_share_details", {
                "member_name": member["title"],
                "member_code": member["member_code"],
                "no_of_shares": share_details.get('current_value_no_of_shares', 0),
                "current_value": share_details.get('current_value_no_of_shares', 0) * self.share_price
            })
            # Accumulate totals for issued, reinvested, and purchased shares
            total_issued_shares += share_details.get('issued_no_of_shares', 0)
            total_share_issued_amount += share_details.get('issued_amount', 0)
            total_reinvested_shares += share_details.get('reinvested_no_of_shares', 0)
            total_share_reinvested_amount += share_details.get('reinvested_amount', 0)
            total_purchased_shares += share_details.get('purchased_no_of_shares', 0)
            total_share_purchase_amount += share_details.get('purchased_amount', 0)

        # Calculate total number of shares and current value
        self.total_no_of_shares = total_issued_shares + total_reinvested_shares - total_purchased_shares
        self.total_current_value = self.total_no_of_shares * self.share_price
        
        # Set the total numbers and amounts for each type
        self.total_no_of_share_issued = total_issued_shares
        self.total_share_issued_amount = total_share_issued_amount
        self.total_no_of_share_reinvested = total_reinvested_shares
        self.total_share_reinvested_amount = total_share_reinvested_amount
        self.total_no_of_share_purchase = total_purchased_shares
        self.total_share_purchase_amount = total_share_purchase_amount

        # Calculate and set the average rates for each type
        self.share_issued_average_rate = (
            total_share_issued_amount / total_issued_shares
            if total_issued_shares > 0 else 0
        )
        self.share_reinvested_average_rate = (
            total_share_reinvested_amount / total_reinvested_shares
            if total_reinvested_shares > 0 else 0
        )
        self.share_purchase_average_rate = (
            total_share_purchase_amount / total_purchased_shares
            if total_purchased_shares > 0 else 0
        )

    def get_share_details_for_member(self, share_member, from_date, to_date):
        query = """
            SELECT 
                transfer_type,
                SUM(no_of_share) AS total_no_of_share,
                SUM(amount) AS total_amount,
                AVG(rate) AS avg_rate
            FROM `tabShare Members Records`
            WHERE parent = %s AND date BETWEEN %s AND %s
            GROUP BY transfer_type
        """
        share_data = frappe.db.sql(query, (share_member, from_date, to_date), as_dict=True)

        # Initialize the result structure
        result = {
            "current_value_no_of_shares": 0,
            "issued_no_of_shares": 0,
            "issued_amount": 0,
            "reinvested_no_of_shares": 0,
            "reinvested_amount": 0,
            "purchased_no_of_shares": 0,
            "purchased_amount": 0,
            "total_amount": 0
        }

        for data in share_data:
            if data["transfer_type"] == "Issue":
                result["issued_no_of_shares"] += flt(data["total_no_of_share"])
                result["issued_amount"] += flt(data["total_amount"])
            elif data["transfer_type"] == "Reinvest":
                result["reinvested_no_of_shares"] += flt(data["total_no_of_share"])
                result["reinvested_amount"] += flt(data["total_amount"])
            elif data["transfer_type"] == "Purchase":
                result["purchased_no_of_shares"] += flt(data["total_no_of_share"])
                result["purchased_amount"] += flt(data["total_amount"])

            # Include only Issue and Reinvest for current value calculation
            if data["transfer_type"] in ["Issue", "Reinvest"]:
                result["current_value_no_of_shares"] += flt(data["total_no_of_share"])
                result["total_amount"] += flt(data["total_amount"])
            elif data["transfer_type"] == "Purchase":
                result["current_value_no_of_shares"] -= flt(data["total_no_of_share"])
                result["total_amount"] -= flt(data["total_amount"])

        return result

    def get_context(doc, context):
        # Pre-format the data you want to pass to the print format
        doc.formatted_from_date = format_date(doc.from_date)
        doc.formatted_to_date = format_date(doc.to_date)
        
        # Pre-format the monetary fields
        doc.formatted_share_price = fmt_money(doc.share_price)
        doc.formatted_total_current_value = fmt_money(doc.total_current_value)
        doc.formatted_share_issued_average_rate = fmt_money(doc.share_issued_average_rate)
        doc.formatted_share_reinvested_average_rate = fmt_money(doc.share_reinvested_average_rate)
        doc.formatted_share_purchase_average_rate = fmt_money(doc.share_purchase_average_rate)
        
        # Make sure you pass these formatted values into the print format
        return context