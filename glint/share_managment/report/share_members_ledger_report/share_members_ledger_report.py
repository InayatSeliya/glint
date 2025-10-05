# Copyright (c) 2024, Inayatali Seliya and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)

    # Initialize Totals
    total_investment_reinvest = 0
    total_withdrawal = 0

    # Calculate separate totals
    for row in data:
        if row['transfer_type'] == 'Investment' or row['transfer_type'] == 'Reinvest':
            total_investment_reinvest += row['amount']
        elif row['transfer_type'] == 'Withdrawal':
            total_withdrawal += row['amount']

    # Add blank row for spacing
    data.append({
        "date": "",
        "share_transaction_id": "",
        "transfer_type": "",
        "amount": ""
    })

    # Add total rows at the bottom of report
    data.append({
        "date": "",
        "share_transaction_id": "",
        "transfer_type": "<b>Total Investment and Reinvest</b>",
        "amount": total_investment_reinvest
    })

    data.append({
        "date": "",
        "share_transaction_id": "",
        "transfer_type": "<b>Total Withdrawal</b>",
        "amount": total_withdrawal
    })

    data.append({
        "date": "",
        "share_transaction_id": "",
        "transfer_type": "<b>Net Balance</b>",
        "amount": total_investment_reinvest - total_withdrawal
    })

    return columns, data


def get_columns():
	return [
		{
			"fieldname": "date",
			"fieldtype": "Date",
			"label": "Date",
			"width": 110
		}, {
			"fieldname": "share_transaction_id",
			"fieldtype": "Link",
			"label": "Share Transaction ID",
			"options": "Share Transaction",
			"width": 175
		}, {
			"fieldname": "transfer_type", 
			"label": "Transfer Type", 
			"fieldtype": "Data", 
			"width": 120
		}, {
			"fieldname": "amount", 
			"label": "Amount", 
			"fieldtype": "Currency", 
			"width": 100
		}
	]

def get_data(filters):
    query = """
        SELECT DISTINCT
            smr.date,
            CASE 
                WHEN smr.transfer_type = 'Issue' THEN st_issue.name
                WHEN smr.transfer_type = 'Reinvest' THEN st_reinvest.name
                WHEN smr.transfer_type = 'Purchase' THEN st_purchase.name
            END AS share_transaction_id,
            smr.transfer_type,
            smr.amount
        FROM
            `tabShare Members Records` smr
        LEFT JOIN
            `tabShare Members` sm ON sm.name = smr.parent
        LEFT JOIN
            `tabShare Transaction` st_issue 
            ON st_issue.to_share_member = sm.name 
            AND smr.transfer_type = 'Issue'
            AND smr.date = st_issue.date
            AND smr.amount = st_issue.amount
            AND st_issue.docstatus = 1
        LEFT JOIN
            `tabShare Transaction` st_reinvest
            ON st_reinvest.to_share_member = sm.name 
            AND smr.transfer_type = 'Reinvest'
            AND smr.date = st_reinvest.date
            AND smr.amount = st_reinvest.amount
            AND st_reinvest.docstatus = 1
        LEFT JOIN
            `tabShare Transaction` st_purchase
            ON st_purchase.from_share_member = sm.name 
            AND smr.transfer_type = 'Purchase'
            AND smr.date = st_purchase.date
            AND smr.amount = st_purchase.amount
            AND st_purchase.docstatus = 1
        WHERE
            sm.name = %(member_code)s
            AND smr.date BETWEEN %(start_date)s AND %(end_date)s
        ORDER BY
            smr.date ASC
    """
    data = frappe.db.sql(query, filters, as_dict=True)

    # Transform transfer_type names
    for row in data:
        if row['transfer_type'] == 'Issue':
            row['transfer_type'] = 'Investment'
        elif row['transfer_type'] == 'Reinvest':
            row['transfer_type'] = 'Reinvest'
        elif row['transfer_type'] == 'Purchase':
            row['transfer_type'] = 'Withdrawal'
    
    return data
