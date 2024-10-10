# Copyright (c) 2024, Inayatali Seliya and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
	columns = [{
		"fieldname": "share_member",
		"label": "Share Member",
		"fieldtype": "Data",
		"width": "250"
	}, {
		"fieldname": "member_code",
		"label": "Member Code",
		"fieldtype": "Data",
		"width": "125"
	}, {
		"fieldname": "member_type",
		"label": "Member Type",
		"fieldtype": "Data",
		"width": "125"
	}, {
		"fieldname": "total_no_of_shares",
		"label": "Total No. of Shares",
		"fieldtype": "Float",
		"width": "150"
	}, {
		"fieldname": "average_rate",
		"label": "Average Rate",
		"fieldtype": "Float",
		"width": "125"
	}, {
		"fieldname": "total_amount",
		"label": "Total Amount",
		"fieldtype": "Currency",
		"options": "INR",
		"width": "125"
	}]


	data = get_share_member_data()

	return columns, data

def get_share_member_data():

	share_member_data = frappe.db.sql("""
		SELECT
			sm.title AS share_member,
			sm.member_code AS member_code,
			sm.member_type,
			-- Calculate total number of shares: (Sum of Issued Shares - Sum of Purchase Shares)
			SUM(CASE WHEN smr.transfer_type = 'Issue' THEN smr.no_of_share ELSE 0 END) -
			SUM(CASE WHEN smr.transfer_type = 'Purchase' THEN smr.no_of_share ELSE 0 END) AS total_no_of_shares,

			-- Calculate total amount: (Sum of Issued Amount - Sum of Purchase Amount)
			SUM(CASE WHEN smr.transfer_type = 'Issue' THEN smr.amount ELSE 0 END) - 
			SUM(CASE WHEN smr.transfer_type = 'Purchase' THEN smr.amount ELSE 0 END) AS total_amount,

			-- Calculate average rate
			CASE
				WHEN (SUM(CASE WHEN smr.transfer_type = 'Issue' THEN smr.no_of_share ELSE 0 END) - 
						SUM(CASE WHEN smr.transfer_type = 'Purchase' THEN smr.no_of_share ELSE 0 END)) = 0
				THEN 0
				ELSE (SUM(CASE WHEN smr.transfer_type = 'Issue' THEN smr.amount ELSE 0 END) - 
						SUM(CASE WHEN smr.transfer_type = 'Purchase' THEN smr.amount ELSE 0 END)) / 
						(SUM(CASE WHEN smr.transfer_type = 'Issue' THEN smr.no_of_share ELSE 0 END) - 
						SUM(CASE WHEN smr.transfer_type = 'Purchase' THEN smr.no_of_share ELSE 0 END))
			END AS average_rate
								   				   
		FROM `tabShare Members` sm
		LEFT JOIN `tabShare Members Records` smr ON sm.name = smr.parent
		GROUP BY sm.name
	""", as_dict=True)					   
	
	return share_member_data

	

	
