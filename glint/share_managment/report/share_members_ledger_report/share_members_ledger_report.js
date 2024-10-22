// Copyright (c) 2024, Inayatali Seliya and contributors
// For license information, please see license.txt

frappe.query_reports["Share Members Ledger Report"] = {
	"filters": [
		{
            "fieldname": "member_code",
            "label": "Member Code",
            "fieldtype": "Link",
            "options": "Share Members",
            "reqd": 1
        },
        {
            "fieldname": "start_date",
            "label": "Start Date",
            "fieldtype": "Date",
            "reqd": 1
        },
        {
            "fieldname": "end_date",
            "label": "End Date",
            "fieldtype": "Date",
            "reqd": 1
        }
	]
};
