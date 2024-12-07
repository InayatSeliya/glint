# Copyright (c) 2024, Inayatali Seliya and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data

def get_columns():
	return[
		{
			"fieldname": "member_code",
			"fieldtype": "Data",
			"label": "Member Code",
			"width": "120"
		}, {
			"fieldname": "member_name",
			"fieldtype": "Data",
			"label": "Member Name",
			"width": "150"
		}, {
			"fieldname": "total_no_of_shares",
			"fieldtype": "Float",
			"label": "Total No of Shares",
			"width": "130"
		}, {
			"fieldname": "dividend_per_share",
			"fieldtype": "Currency",
			"label": "Dividend Per Share",
			"width": "130"
		}, {
			"fieldname": "dividend_amount",
			"fieldtype": "Currency",
			"label": "Dividend Amount",
			"width": "130"
		}
	]

def get_data(filters):

	dividend_account_balance = frappe.db.get_value(
		"Account",
		{"name": "Profit Declared"},
		"balance"
	)

	if not dividend_account_balance:
		frappe.throw("No balance found for the 'Profit Declare Account'. Please verify the account.")
	
	
	query = """
		SELECT
		sm.member_code AS member_code,
		sm.name AS member_name,
		SUM(CASE
				WHEN smr.transfer_type = 'Issue' THEN smr.no_of_share
				WHEN smr.transfer_type = 'Purchase' THEN -smr.no_of_share
				ELSE 0
			END) AS total_no_of_shares,
		dd.dividend_p
"""