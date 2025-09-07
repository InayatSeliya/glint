# Copyright (c) 2025, Inayatali Seliya and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import get_first_day, get_last_day
from frappe import _
from dateutil.relativedelta import relativedelta


class ProfitDistributionDetails(Document):
    def validate(self):
        self.validate_dates()
        self.validate_profit_account()
        self.set_total_profit()
        self.set_no_of_months()
        self.calculate_monthly_profit()

    def validate_dates(self):
        if not self.start_date or not self.end_date:
            frappe.throw(_("Start Date and End Date are mandatory."))
        if self.start_date >= self.end_date:
            frappe.throw(_("Start Date must be before End Date."))
        if not self.profit_declaration_date:
            frappe.throw(_("Profit Declaration Date is mandatory."))
        if self.profit_declaration_date < self.end_date:
            frappe.throw(_("Profit Declaration Date must be after End Date."))

    def validate_profit_account(self):
        if not self.profit_account:
            frappe.throw(_("Profit Account must be selected."))


    def set_total_profit(self):
        gl_entry = frappe.db.sql("""
            SELECT 
                SUM(credit) AS total_credit,
                SUM(debit) AS total_debit
            FROM `tabGL Entry`
            WHERE posting_date <= %s
            AND account = %s
            AND is_cancelled = 0
        """, (self.profit_declaration_date, self.profit_account), as_dict=True)

        total_credit = gl_entry[0].total_credit if gl_entry and gl_entry[0].total_credit else 0
        total_debit = gl_entry[0].total_debit if gl_entry and gl_entry[0].total_debit else 0
        
        net_profit = total_credit - total_debit
        
        if net_profit <= 0:
            frappe.throw(_("No net profit found in the selected account up to the declaration date."))
        
        self.total_profit = net_profit

    def set_no_of_months(self):
        if self.start_date and self.end_date:
            self.no_of_months = self.calculate_month_difference(self.start_date, self.end_date)
            if self.no_of_months <= 0:
                frappe.throw(_("No. of months must be greater than zero."))

    def calculate_monthly_profit(self):
        if self.total_profit and self.no_of_months:
            self.monthly_profit = self.total_profit / self.no_of_months

    @staticmethod
    def calculate_month_difference(start_date, end_date):
        start = frappe.utils.getdate(start_date)
        end = frappe.utils.getdate(end_date)
        return (end.year - start.year) * 12 + (end.month - start.month) + 1

    def get_previous_units(self, member):
        """Get member's units from the last profit distribution record"""
        last_distribution = frappe.get_all(
            "Profit Distribution Details",
            filters={
                "docstatus": 1,  # Get only submitted documents
                "end_date": ("<", self.start_date)  # Get records before current period
            },
            order_by="end_date DESC",
            limit=1
        )

        if not last_distribution:
            return 0

        last_units = frappe.get_all(
            "Profit Distribution Monthly Units",
            filters={
                "parent": last_distribution[0].name,
                "share_member": member
            },
            fields=["units"],
            order_by="month DESC",
            limit=1
        )

        return last_units[0].units if last_units else 0

    def before_save(self):
        if not self.start_date or not self.end_date or not self.monthly_profit or not self.no_of_months:
            return

        # Preserve existing reinvest flags for members (if any)
        existing_reinvest = {}
        for row in self.profit_distribution_summary:
            existing_reinvest[row.share_member] = row.reinvest

        # Clear monthly_units before recalculating to avoid duplicates
        self.set("profit_distribution_monthly_units", [])

        members = frappe.get_all("Share Members", fields=["name"], order_by="name ASC")

        end_month = get_first_day(self.end_date)
        current_month = get_first_day(self.start_date)

        # member_units = {m.name: 0 for m in members}
        member_units = {m.name: self.get_previous_units(m.name) for m in members}

        while current_month <= end_month:
            share_price = frappe.db.get_value("Share Price Records", {"month": current_month}, "share_price")
            if not share_price or share_price == 0:
                frappe.throw(_("Share Price not found for the selected period."))
                # current_month += relativedelta(months=1)
                # continue

            total_units = 0
            member_month_units = {}

            for member in members:
                month_end = get_last_day(current_month)

                issue_amount_result = frappe.db.sql("""
                    SELECT SUM(amount)
                    FROM `tabShare Transaction`
                    WHERE transfer_type IN ('Issue', 'Reinvest')
                    AND to_share_member = %s
                    AND date BETWEEN %s AND %s
                """, (member.name, current_month, month_end))
                issue_amount = issue_amount_result[0][0] if issue_amount_result and issue_amount_result[0][0] else 0

                purchase_amount_result = frappe.db.sql("""
                    SELECT SUM(amount)
                    FROM `tabShare Transaction`
                    WHERE transfer_type = 'Purchase'
                    AND from_share_member = %s
                    AND date BETWEEN %s AND %s
                """, (member.name, current_month, month_end))
                purchase_amount = purchase_amount_result[0][0] if purchase_amount_result and purchase_amount_result[0][0] else 0

                net_units = (issue_amount - purchase_amount) / share_price
                member_units[member.name] += net_units
                member_month_units[member.name] = member_units[member.name]

                total_units += member_units[member.name]

            for member in members:
                units = round(member_month_units[member.name], 4)
                holding_percent = (units / total_units * 100) if total_units else 0
                profit_amount = (holding_percent / 100) * self.monthly_profit

                self.append("profit_distribution_monthly_units", {
                    "share_member": member.name,
                    "month": current_month,
                    "units": units,
                    "holding_percent": round(holding_percent, 4),
                    # "profit_amount": round(profit_amount, 0)
                    "profit_amount": profit_amount # no rounding here, keep decimals
                })

            current_month += relativedelta(months=1)

        # Clear and refill summary table
        self.set("profit_distribution_summary", [])

        member_totals = {}
        for row in self.profit_distribution_monthly_units:
            if not row.share_member:
                continue
            member_totals.setdefault(row.share_member, 0)
            member_totals[row.share_member] += row.profit_amount or 0

        for member in sorted(member_totals.keys()):
            self.append("profit_distribution_summary", {
                "share_member": member,
                "total_profit": round(member_totals[member], 2), # round only final total to 2 decimals
                "reinvest": existing_reinvest.get(member, 0)  # Preserve checkbox state
            })

    def on_submit(self):
        total_reinvest_amount = 0
        total_withdraw_amount = 0
        withdraw_details = []

        for row in self.profit_distribution_summary:
            member = row.share_member
            profit_amount = row.total_profit or 0
            reinvest = row.reinvest

            if reinvest:
                total_reinvest_amount += profit_amount

                share_member_account = frappe.db.get_value("Share Members", member, "share_member_account")

                transaction = frappe.get_doc({
                    "doctype": "Share Transaction",
                    "transfer_type": "Reinvest",
                    "date": self.profit_declaration_date,
                    "journal_entry": 1,
                    "to_share_member": member,
                    "equityliability_account": share_member_account,
                    "asset_account": "Profit Declared - GH",
                    "amount": profit_amount,
                    "remarks": f"Profit Reinvested from distribution {self.name}"
                })
                transaction.insert(ignore_permissions=True)
            else:
                total_withdraw_amount += profit_amount
                withdraw_details.append(f"{member}: ₹{profit_amount}")

        # Update parent doc fields without creating Journal Entry (skipped for now)
        # self.reinvest_amount = total_reinvest_amount
        # self.withdraw_amount = total_withdraw_amount
        
        # Round final totals before saving
        total_reinvest_amount = round(total_reinvest_amount, 2)
        total_withdraw_amount = round(total_withdraw_amount, 2)

        self.db_set('reinvest_amount', total_reinvest_amount)
        self.db_set('withdraw_amount', total_withdraw_amount)

        # Journal Entry creation is skipped as per your instruction.
        # You can add it later when you want.

        frappe.msgprint("Share Transaction for Reinvest created successfully.")
