# Copyright (c) 2024, Inayatali Seliya and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
	columns = [{
		"fieldname": "share_member",
		"label": "Share Member",
		"fieldtype": "Data"
	}, {
		"fieldname": "total_no_of_shares",
		"label": "Total No. of Shares",
		"fieldtype": "Float"
	}, {
		"fieldname": "total_amount",
		"label": "Total Amount",
		"fieldtype": "Currency",
		"options": "INR"
	}]


	data = get_share_member_data()

	return columns, data

def get_share_member_data():

	share_member_data = frappe.db.sql("""
		SELECT
			sm.name AS share_member,
			SUM(smr.no_of_share) As total_no_of_shares,
			SUM(smr.amount) AS total_amount
		FROM `tabShare Members` sm
		LEFT JOIN `tabShare Members Records` smr ON sm.name = smr.parent
		GROUP BY sm.name
	""", as_dict=True)					   
	
	return share_member_data

	

	# data = frappe.get_all(
	# 	"Share Transaction", 
	# 	fields=["SUM(amount) AS total_amount", "SUM(no_of_shares) AS total_share", "to_share_member"], 
	# 	filters={"docstatus": 1}, 
	# 	group_by="to_share_member",
	# )

	# frappe.get_all(
	# 	"Share Members", 
	# 	fields=["SUM(amount) AS total_amount", "SUM(no_of_share) AS total_share", "name"], 
	# 	filters={"docstatus": 1}, 
	# 	group_by="name",
	# )

	# return columns, data
