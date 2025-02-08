# Copyright (c) 2024, Inayatali Seliya and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
    if not filters:
        filters = {}

    columns = get_columns()
    data = []

    # Validate and fetch required filter inputs
    member_code = filters.get("member_code")
    if not member_code:
        frappe.throw("Please select a Member Code.")

    # Fetch Share Member details
    member_details = frappe.get_doc("Share Members", member_code)

    # Fetch Lifetime Shareholding Summary
    share_summary_query = """
        SELECT
            SUM(CASE WHEN transfer_type = 'Issue' THEN no_of_share ELSE 0 END) AS total_issued,
            SUM(CASE WHEN transfer_type = 'Purchase' THEN no_of_share ELSE 0 END) AS total_purchased,
            SUM(CASE WHEN transfer_type = 'Reinvest' THEN no_of_share ELSE 0 END) AS total_reinvested,
            SUM(CASE WHEN transfer_type = 'Issue' THEN amount ELSE 0 END) AS amount_issued,
            SUM(CASE WHEN transfer_type = 'Purchase' THEN amount ELSE 0 END) AS amount_purchased,
            SUM(CASE WHEN transfer_type = 'Reinvest' THEN amount ELSE 0 END) AS amount_reinvested
        FROM `tabShare Members Records`
        WHERE parent = %(member_code)s
    """
    share_summary = frappe.db.sql(share_summary_query, {"member_code": member_code}, as_dict=True)[0]

    # Calculate Current Shares
    total_issued = share_summary.get("total_issued", 0)
    total_purchased = share_summary.get("total_purchased", 0)
    total_reinvested = share_summary.get("total_reinvested", 0)

    current_no_of_shares = total_issued - total_purchased + total_reinvested

    # Fetch the latest share price
    latest_share_price = frappe.db.sql(
        """
        SELECT share_price
        FROM `tabShare Price`
        ORDER BY update_on DESC
        LIMIT 1
        """
    )
    current_share_price = latest_share_price[0][0] if latest_share_price else 0

    current_value = current_no_of_shares * current_share_price

    # Fetch Transaction Ledger
    transaction_query = """
        SELECT
            date,
            parent AS share_transaction_id,
            transfer_type,
            rate,
            no_of_share,
            amount
        FROM `tabShare Members Records`
        WHERE parent = %(member_code)s
        ORDER BY date ASC
    """
    transactions = frappe.db.sql(transaction_query, {"member_code": member_code}, as_dict=True)

    # Format data for report
    data.append({
        "name": member_details.title,
        "member_code": member_details.member_code,
        "date_of_birth": member_details.date_of_birth,
        "mobile": member_details.mobile,
        "address": member_details.address,
        "nominee": member_details.nominee,
        "total_issued": total_issued,
        "amount_issued": share_summary.get("amount_issued", 0),
        "total_purchased": total_purchased,
        "amount_purchased": share_summary.get("amount_purchased", 0),
        "total_reinvested": total_reinvested,
        "amount_reinvested": share_summary.get("amount_reinvested", 0),
        "current_no_of_shares": current_no_of_shares,
        "current_value": current_value,
    })

    # Add transactions to the report
    for transaction in transactions:
        data.append({
            "date": transaction.date,
            "share_transaction_id": transaction.share_transaction_id,
            "transfer_type": transaction.transfer_type,
            "rate": transaction.rate,
            "no_of_share": transaction.no_of_share,
            "amount": transaction.amount,
        })

    return columns, data


def get_columns():
    return [
        {"fieldname": "name", "label": "Name", "fieldtype": "Data", "width": 150},
        {"fieldname": "member_code", "label": "Member Code", "fieldtype": "Data", "width": 120},
        {"fieldname": "date_of_birth", "label": "Date of Birth", "fieldtype": "Date", "width": 120},
        {"fieldname": "mobile", "label": "Mobile", "fieldtype": "Data", "width": 120},
        {"fieldname": "address", "label": "Address", "fieldtype": "Data", "width": 250},
        {"fieldname": "nominee", "label": "Nominee", "fieldtype": "Data", "width": 150},
        {"fieldname": "total_issued", "label": "Total Shares Issued", "fieldtype": "Int", "width": 150},
        {"fieldname": "amount_issued", "label": "Amount Issued", "fieldtype": "Currency", "width": 150},
        {"fieldname": "total_purchased", "label": "Total Shares Purchased", "fieldtype": "Int", "width": 150},
        {"fieldname": "amount_purchased", "label": "Amount Purchased", "fieldtype": "Currency", "width": 150},
        {"fieldname": "total_reinvested", "label": "Total Shares Reinvested", "fieldtype": "Int", "width": 150},
        {"fieldname": "amount_reinvested", "label": "Amount Reinvested", "fieldtype": "Currency", "width": 150},
        {"fieldname": "current_no_of_shares", "label": "Current No. of Shares", "fieldtype": "Int", "width": 150},
        {"fieldname": "current_value", "label": "Current Value", "fieldtype": "Currency", "width": 150},
        {"fieldname": "date", "label": "Date", "fieldtype": "Date", "width": 100},
        {"fieldname": "share_transaction_id", "label": "Share Transaction ID", "fieldtype": "Data", "width": 150},
        {"fieldname": "transfer_type", "label": "Transfer Type", "fieldtype": "Data", "width": 150},
        {"fieldname": "rate", "label": "Rate", "fieldtype": "Currency", "width": 100},
        {"fieldname": "no_of_share", "label": "No. of Shares", "fieldtype": "Int", "width": 100},
        {"fieldname": "amount", "label": "Amount", "fieldtype": "Currency", "width": 150},
    ]

# def execute(filters=None):
# 	columns = get_columns()
# 	data = get_data(filters)
# 	return columns, data

# def get_columns():
# 	return[
# 		{
# 			"fieldname": "member_code",
# 			"fieldtype": "Data",
# 			"label": "Member Code",
# 			"width": "120"
# 		}, {
# 			"fieldname": "member_name",
# 			"fieldtype": "Data",
# 			"label": "Member Name",
# 			"width": "150"
# 		}, {
# 			"fieldname": "total_no_of_shares",
# 			"fieldtype": "Float",
# 			"label": "Total No of Shares",
# 			"width": "130"
# 		}, {
# 			"fieldname": "dividend_per_share",
# 			"fieldtype": "Currency",
# 			"label": "Dividend Per Share",
# 			"width": "130"
# 		}, {
# 			"fieldname": "dividend_amount",
# 			"fieldtype": "Currency",
# 			"label": "Dividend Amount",
# 			"width": "130"
# 		}
# 	]

# def get_data(filters):

# 	dividend_account_balance = frappe.db.get_value(
# 		"Account",
# 		{"name": "Profit Declared"},
# 		"balance"
# 	)

# 	if not dividend_account_balance:
# 		frappe.throw("No balance found for the 'Profit Declare Account'. Please verify the account.")
	
	
# 	query = """
# 		SELECT
# 		sm.member_code AS member_code,
# 		sm.name AS member_name,
# 		SUM(CASE
# 				WHEN smr.transfer_type = 'Issue' THEN smr.no_of_share
# 				WHEN smr.transfer_type = 'Purchase' THEN -smr.no_of_share
# 				ELSE 0
# 			END) AS total_no_of_shares,
# 		dd.dividend_p
# """