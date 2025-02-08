// Copyright (c) 2025, Inayatali Seliya and contributors
// For license information, please see license.txt

frappe.query_reports["Share Member Profile"] = {
	"filters": [
		{
            fieldname: "member_code",
            label: __("Member Code"),
            fieldtype: "Link",
            options: "Share Members",
            reqd: 1, // Mandatory field
        },
        {
            fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date",
            default: frappe.datetime.add_months(frappe.datetime.nowdate(), -1), // Default: Last month
        },
        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
            default: frappe.datetime.nowdate(), // Default: Today
        },
	]
};
