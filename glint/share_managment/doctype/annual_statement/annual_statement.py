# Copyright (c) 2025, Inayatali Seliya and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import get_first_day, getdate, flt

class AnnualStatement(Document):
	def autoname(self):
		date_str = getdate(self.posting_date).strftime("%d-%m-%Y")
		self.name = f"{self.share_member} - {date_str}"
	

	def validate(self):
		# 0. Mandatory field checks
		if not self.from_date or not self.to_date:
			frappe.throw(_("From Date and To Date are mandatory."))
		
		if not self.posting_date:
			frappe.throw(_("Posting Date is mandatory."))

		# 1. Date range logic
		if self.from_date >= self.to_date:
			frappe.throw(_("From Date must be before To Date."))

		# 2. Posting date must be after to_date
		if self.posting_date <= self.to_date:
			frappe.throw(_("Posting Date must be after To Date."))

		# 3. Safety check for Main Member
		member_type = frappe.db.get_value("Share Members", self.share_member, "member_type")
		if member_type != "Main Member":
			frappe.throw(_("Only 'Main Member' can be selected."))

	def before_save(self):
		if not self.share_member or not self.to_date:
			return

		# Get share price for the start of the month of `to_date`
		month_start = get_first_day(getdate(self.to_date))

		share_price_row = frappe.get_value(
			"Share Price Records",
			{"month": month_start},
			["share_price", "goodwill_price"],
			as_dict=True
		)

		if not share_price_row:
			frappe.throw(f"No Share Price found for month: {month_start}")

		total_share_price = (share_price_row.get("share_price") or 0) + (share_price_row.get("goodwill_price") or 0)

		# Convert to_date → 1st of month (format in Monthly Units)
		unit_month = get_first_day(getdate(self.to_date))

		# Clear old rows
		self.set("share_member_summary", [])

		# Collect all members (Main + Subs)
		members = [{"name": self.share_member}]
		sub_members = frappe.get_all(
			"Share Members",
			filters={"main_member": self.share_member},
			fields=["name"],
			order_by="name ASC"
		)
		members.extend(sub_members)

		for member in members:
			share_member = member["name"]

			# Get last month's unit
			unit_row = frappe.get_value(
				"Profit Distribution Monthly Units",
				{"share_member": share_member, "month": unit_month},
				"units"
			)
			units = unit_row if unit_row else 0

			# Share value = units × total_share_price
			share_value = units * total_share_price

			# Get total profit for this member from the Profit Distribution Details for this period
			profit_row = frappe.db.sql("""
				SELECT pds.total_profit
				FROM `tabProfit Distribution Summary` pds
				JOIN `tabProfit Distribution Details` pdd ON pds.parent = pdd.name
				WHERE pds.share_member = %s
					AND pdd.start_date >= %s
					AND pdd.end_date <= %s
				LIMIT 1
			""", (share_member, self.from_date, self.to_date), as_dict=True)
			
			profit = profit_row[0].total_profit if profit_row else 0

			# Get account for this member
			member_account = frappe.db.get_value("Share Members", share_member, "share_member_account")
			if not member_account:
				frappe.throw(_(f"No account linked to member {share_member}"))

			# Get GL entries for this account
			gl_entries = frappe.db.sql("""
				SELECT 
					COALESCE(SUM(credit), 0) as total_credit,
					COALESCE(SUM(debit), 0) as total_debit
				FROM `tabGL Entry`
				WHERE 
					account = %s
					AND posting_date <= %s
					AND is_cancelled = 0
			""", (member_account, self.to_date), as_dict=1)

			# Calculate total investment (Credit - Debit)
			total_investment = flt(gl_entries[0].total_credit) - flt(gl_entries[0].total_debit)
			
			# Calculate total investment
			# total_investment = 0

			# issue_reinvest = frappe.get_all(
			# 	"Share Transaction",
			# 	filters={
			# 		"docstatus": 1,
			# 		"date": ["<=", self.to_date],
			# 		"to_share_member": share_member,
			# 		"transfer_type": ["in", ["Issue", "Reinvest"]]
			# 	},
			# 	fields=["amount"]
			# )

			# for tx in issue_reinvest:
			# 	total_investment += tx.amount or 0

			# purchases = frappe.get_all(
			# 	"Share Transaction",
			# 	filters={
			# 		"docstatus": 1,
			# 		"date": ["<=", self.to_date],
			# 		"from_share_member": share_member,
			# 		"transfer_type": "Purchase"
			# 	},
			# 	fields=["amount"]
			# )

			# for tx in purchases:
			# 	total_investment -= tx.amount or 0



			# Append row
			self.append("share_member_summary", {
				"share_member": share_member,
				"total_investment": total_investment,
				"date": self.to_date,
				"share_price": total_share_price,
				"share_unit": units,
				"share_value": share_value,
				"profit": profit
			})

		# Populate Annual Statement Transaction Details
		self.set("annual_statement_transaction_details", [])

		# Get list of all related members: main + sub
		members = frappe.get_all("Share Members",
			filters={"main_member": self.share_member},
			pluck="name"
		)
		members.append(self.share_member)

		# Fetch all transactions in date range
		transactions = frappe.get_all("Share Transaction",
			filters={
				"date": ["between", [self.from_date, self.to_date]]
			},
			fields=["date", "transfer_type", "to_share_member", "from_share_member", "amount"],
			order_by="date asc, to_share_member asc, from_share_member asc"
		)

		# Filter transactions manually based on relevant members
		for tx in transactions:
			member = None
			if tx.transfer_type in ["Issue", "Reinvest"] and tx.to_share_member in members:
				member = tx.to_share_member
				label = "Investment" if tx.transfer_type == "Issue" else "Reinvestment"
			elif tx.transfer_type == "Purchase" and tx.from_share_member in members:
				member = tx.from_share_member
				label = "Withdrawal"
			else:
				continue

			self.append("annual_statement_transaction_details", {
				"date": tx.date,
				"share_member": member,
				"transaction_type": label,
				"amount": tx.amount
			})