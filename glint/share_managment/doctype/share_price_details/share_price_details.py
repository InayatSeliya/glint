# Copyright (c) 2025, Inayatali Seliya and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from frappe.utils import getdate, flt

class SharePriceDetails(Document):
    def validate(self):
        if not self.start_date or not self.end_date:
            frappe.throw("Start Date and End Date are required.")

    def before_save(self):
        start_date = getdate(self.start_date)
        end_date = getdate(self.end_date)

        # Fetch Goodwill Amount from COA
        self.goodwill_amount = self.get_goodwill_amount_from_coa(start_date, end_date)

        # Calculate goodwill period months
        goodwill_period_months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month) + 1
        self.goodwill_period_months = goodwill_period_months

        monthly_goodwill = flt(self.goodwill_amount) / goodwill_period_months

        # Fetch existing records
        existing_records = {getdate(record.month): record for record in self.get("share_price_records")}
        frappe.logger().info(f"Existing Records Before Save: {existing_records}")

        # Preserve last recorded share details
        last_period_details = self.get_last_period_details(start_date)
        last_share_price = last_period_details['total_price'] if last_period_details else None

        for i in range(goodwill_period_months):
            month_date = (start_date + relativedelta(months=i)).replace(day=1)

            if month_date in existing_records:
                record = existing_records[month_date]
                # Only update missing fields, do not reset existing ones
                record.monthly_goodwill = record.monthly_goodwill or monthly_goodwill
                record.share_price = record.share_price or last_share_price
                record.amount_received = record.amount_received or self.get_amount_received(month_date)
            else:
                # Create new record only if it does not exist
                record = self.append("share_price_records", {
                    "month": month_date,
                    "monthly_goodwill": monthly_goodwill,
                    "share_price": last_share_price if last_share_price else None,
                    "amount_received": self.get_amount_received(month_date)
                })

            # Keep last share price updated
            last_share_price = record.share_price if record.share_price else last_share_price

        # Ensure records remain sorted
        self.share_price_records = sorted(self.share_price_records, key=lambda x: x.month)

        frappe.logger().info(f"Records After Before Save: {self.share_price_records}")

    def get_last_period_details(self, start_date):
        """Fetch the last period's share price, goodwill price and cumulative shares."""
        last_period = frappe.db.sql("""
            SELECT share_price, goodwill_price, cumulative_shares
            FROM `tabShare Price Records`
            WHERE month < %s 
            ORDER BY month DESC 
            LIMIT 1
        """, (start_date,), as_dict=True)

        if last_period:
            return {
                'total_price': last_period[0]["share_price"] + last_period[0]["goodwill_price"],
                'cumulative_shares': last_period[0]["cumulative_shares"] or 0
            }
        return None

    # def get_amount_received(self, month_date):
    #     month_date = getdate(month_date)
    #     total_amount = frappe.db.sql("""
    #         SELECT SUM(amount) FROM `tabShare Transaction`
    #         WHERE MONTH(date) = %s AND YEAR(date) = %s
    #     """, (month_date.month, month_date.year))

    #     return total_amount[0][0] if total_amount and total_amount[0][0] else 0

    def get_amount_received(self, month_date):
        month_date = getdate(month_date)

        # Get total amount from Issue and Reinvest transactions
        issue_result = frappe.db.sql("""
            SELECT COALESCE(SUM(amount), 0) as total
            FROM `tabShare Transaction`
            WHERE MONTH(date) = %s
            AND YEAR(date) = %s
            AND transfer_type IN ('Issue', 'Reinvest')
        """, (month_date.month, month_date.year), as_dict=1)
        issue_amount = issue_result[0].total if issue_result else 0

        # Get total amount from Purchase transactions
        purchase_result = frappe.db.sql("""
            SELECT COALESCE(SUM(amount), 0) as total
            FROM `tabShare Transaction`
            WHERE MONTH(date) = %s 
            AND YEAR(date) = %s
            AND transfer_type = 'Purchase'
        """, (month_date.month, month_date.year), as_dict=1)
        purchase_amount = purchase_result[0].total if purchase_result else 0

        # Calculate net amount (Issue + Reinvest - Purchase)
        return issue_amount - purchase_amount


    def get_goodwill_amount_from_coa(self, start_date, end_date):
        """ Fetches the total Goodwill Amount from all child accounts under 'Goodwill - GH' """
        goodwill_group = "Goodwill - GH"  # Parent Group Account

        # Fetch all child accounts under "Goodwill - GH"
        child_accounts = frappe.db.sql("""
            SELECT name FROM `tabAccount` 
            WHERE parent_account = %s AND is_group = 0
        """, (goodwill_group,), as_dict=True)

        if not child_accounts:
            frappe.throw(f"No child accounts found under {goodwill_group}.")

        child_account_names = [acc["name"] for acc in child_accounts]

        # Sum Goodwill Amount from all child accounts in GL Entry table
        goodwill_amount = frappe.db.sql("""
            SELECT SUM(debit - credit) FROM `tabGL Entry`
            WHERE account IN (%s)
            AND posting_date BETWEEN %s AND %s
        """ % (", ".join(["%s"] * len(child_account_names)), "%s", "%s"),
            tuple(child_account_names + [start_date, end_date])
        )

        return goodwill_amount[0][0] if goodwill_amount and goodwill_amount[0][0] else 0

    def on_submit(self):
        """Calculate No of Shares, Cumulative Shares, Goodwill Price, and update Share Price."""
        records = sorted(self.share_price_records, key=lambda x: x.month)
        
        # Get last period's details
        last_period_details = self.get_last_period_details(records[0].month)
        
        # Determine if this is the first ever document
        is_first_document = not last_period_details
        
        # Set initial values
        if is_first_document:
            if not self.initial_share_price:
                frappe.throw("Initial Share Price is required for first document")
            share_price_to_use = self.initial_share_price
            cumulative_shares = 0
        else:
            self.db_set('initial_share_price', last_period_details['total_price'])
            share_price_to_use = last_period_details['total_price']
            cumulative_shares = last_period_details['cumulative_shares']

        current_share_price = share_price_to_use
        previous_goodwill_price = 0

        for i, record in enumerate(records):
            amount_received = self.get_amount_received(record.month)
            record.db_set('amount_received', amount_received)

            # Calculate total price for share calculation
            total_price = current_share_price + previous_goodwill_price

            # Calculate no_of_shares if amount received
            if amount_received:
                no_of_shares = amount_received / total_price
                record.db_set('no_of_shares', no_of_shares)
                cumulative_shares += no_of_shares
                record.db_set('cumulative_shares', cumulative_shares)

            # Calculate goodwill price
            if cumulative_shares > 0:
                current_goodwill_price = record.monthly_goodwill / cumulative_shares
            else:
                current_goodwill_price = 0
            record.db_set('goodwill_price', current_goodwill_price)

            # Set share price 
            new_share_price = current_share_price + previous_goodwill_price
            record.db_set('share_price', new_share_price)

            # Update for next iteration
            current_share_price = new_share_price
            previous_goodwill_price = current_goodwill_price

            frappe.db.commit()
