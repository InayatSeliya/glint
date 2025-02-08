# Copyright (c) 2024, Inayatali Seliya and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)

	# Initialize Totals
	total_no_of_shares = 0
	total_amount = 0

	# Calculate total from Issue and Reinvest then deduct from Purchase
	for row in data:
		if row['transfer_type'] == 'Issue':
			total_no_of_shares += row['no_of_share']
			total_amount += row['amount']
		elif row['transfer_type'] == 'Reinvest':
			total_no_of_shares += row['no_of_share']
			total_amount += row['amount']
		elif row['transfer_type'] == 'Purchase':
			total_no_of_shares -= row['no_of_share']
			total_amount -= row['amount']

	# Add totals at the bottom of report
	data.append({
		"date": "",
		"share_transaction_id": "",
		"transfer_type": "<b>Total</b>",
		"rate": "",
		"no_of_share": total_no_of_shares,
		"amount": total_amount
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
			"fieldname": "rate", 
			"label": "Rate", 
			"fieldtype": "Currency", 
			"width": 100
		}, {
			"fieldname": "no_of_share", 
			"label": "No. of Shares", 
			"fieldtype": "Float", 
			"width": 130
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
			st.name AS share_transaction_id,
            smr.transfer_type,
            smr.rate,
			smr.no_of_share,
            smr.amount
        FROM
            `tabShare Members Records` smr
        LEFT JOIN
            `tabShare Members` sm ON sm.name = smr.parent
		LEFT JOIN
			`tabShare Transaction` st 
			ON ((st.to_share_member = sm.name AND smr.transfer_type = 'Issue')
			OR (st.to_share_member = sm.name AND smr.transfer_type = 'Reinvest')
			OR (st.from_share_member = sm.name AND smr.transfer_type = 'Purchase'))
			AND smr.date = st.date
			AND smr.no_of_share = st.no_of_shares
        WHERE
            sm.name = %(member_code)s
            AND smr.date BETWEEN %(start_date)s AND %(end_date)s
        ORDER BY
            smr.date ASC
	"""
	return frappe.db.sql(query,filters, as_dict=True)