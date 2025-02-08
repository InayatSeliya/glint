# Copyright (c) 2025, Inayatali Seliya and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import getdate

# def execute(filters=None):
#     columns = get_columns()
#     data = get_data(filters)
#     return columns, data

# def get_columns():
#     return [
#         # Columns for Member Details
#         {"label": "Section", "fieldname": "section", "fieldtype": "Data", "width": 150},
#         {"label": "Title", "fieldname": "title", "fieldtype": "Data", "width": 200},
#         {"label": "Member Type", "fieldname": "member_type", "fieldtype": "Data", "width": 150},
#         {"label": "Date of Birth", "fieldname": "date_of_birth", "fieldtype": "Date", "width": 120},
#         {"label": "Mobile", "fieldname": "mobile", "fieldtype": "Data", "width": 120},
#         {"label": "Nominee", "fieldname": "nominee", "fieldtype": "Data", "width": 150},
#         {"label": "Address", "fieldname": "address", "fieldtype": "Data", "width": 250},

#         # Columns for Shareholding Summary
#         {"label": "Total Shares Issued", "fieldname": "total_issued", "fieldtype": "Float", "width": 150},
#         {"label": "Total Amount Issued", "fieldname": "amount_issued", "fieldtype": "Currency", "width": 150},
#         {"label": "Total Shares Purchased", "fieldname": "total_purchased", "fieldtype": "Float", "width": 150},
#         {"label": "Total Amount Purchased", "fieldname": "amount_purchased", "fieldtype": "Currency", "width": 150},
#         {"label": "Total Shares Reinvested", "fieldname": "total_reinvested", "fieldtype": "Float", "width": 150},
#         {"label": "Total Amount Reinvested", "fieldname": "amount_reinvested", "fieldtype": "Currency", "width": 150},

#         # Columns for Transaction History
#         {"label": "Date", "fieldname": "date", "fieldtype": "Date", "width": 120},
#         {"label": "Transfer Type", "fieldname": "transfer_type", "fieldtype": "Data", "width": 150},
#         {"label": "No. of Shares", "fieldname": "no_of_share", "fieldtype": "Float", "width": 120},
#         {"label": "Rate per Share", "fieldname": "rate", "fieldtype": "Currency", "width": 120},
#         {"label": "Amount", "fieldname": "amount", "fieldtype": "Currency", "width": 150},
#     ]

# def get_data(filters):
#     if not filters or not filters.get("member_code"):
#         frappe.throw("Please select a Share Member to generate the report.")

#     member_code = filters.get("member_code")
#     from_date = filters.get("from_date")
#     to_date = filters.get("to_date")

#     # Fetch Member Details
#     member_details = frappe.db.get_value(
#         "Share Members",
#         {"name": filters.get("member_code")},  # Match using the full name from the filter
#         ["title", "member_type", "date_of_birth", "mobile", "nominee", "address"],
#         as_dict=True,
#     )

#     if not member_details:
#         frappe.throw(f"Share Member with code {filters.get('member_code')} does not exist.")

#     # Fetch Shareholding Summary (from Share Members Records)
#     share_summary = frappe.db.sql("""
#         SELECT
#             SUM(CASE WHEN transfer_type = 'Issue' THEN no_of_share ELSE 0 END) AS total_issued,
#             SUM(CASE WHEN transfer_type = 'Purchase' THEN no_of_share ELSE 0 END) AS total_purchased,
#             SUM(CASE WHEN transfer_type = 'Reinvest' THEN no_of_share ELSE 0 END) AS total_reinvested,
#             SUM(CASE WHEN transfer_type = 'Issue' THEN amount ELSE 0 END) AS amount_issued,
#             SUM(CASE WHEN transfer_type = 'Purchase' THEN amount ELSE 0 END) AS amount_purchased,
#             SUM(CASE WHEN transfer_type = 'Reinvest' THEN amount ELSE 0 END) AS amount_reinvested
#         FROM `tabShare Members Records`
#         WHERE parent = (SELECT name FROM `tabShare Members` WHERE name = %s)
#         AND (%s IS NULL OR date >= %s)
#         AND (%s IS NULL OR date <= %s)
#     """, (filters.get("member_code"), from_date, from_date, to_date, to_date), as_dict=True)[0]

#     # Fetch Transaction Details (if detailed transaction history is required)
#     transactions = frappe.db.sql("""
#         SELECT
#             date, transfer_type, no_of_share, rate, amount
#         FROM `tabShare Members Records`
#         WHERE parent = %s
#         AND (%s IS NULL OR date >= %s)
#         AND (%s IS NULL OR date <= %s)
#         ORDER BY date ASC
#     """, (member_code, from_date, from_date, to_date, to_date), as_dict=True)

#     # Prepare Data for Report
#     data = []
    
#     # Section 1: Member Details
#     data.append({
#         "section": "Member Details",
#         "title": member_details["title"],
#         "member_type": member_details["member_type"],
#         "date_of_birth": member_details["date_of_birth"],
#         "mobile": member_details["mobile"],
#         "nominee": member_details["nominee"],
#         "address": member_details["address"]
#     })

#     # Section 2: Shareholding Summary
#     data.append({
#         "section": "Shareholding Summary",
#         "total_issued": share_summary["total_issued"] or 0,
#         "amount_issued": share_summary["amount_issued"] or 0,
#         "total_purchased": share_summary["total_purchased"] or 0,
#         "amount_purchased": share_summary["amount_purchased"] or 0,
#         "total_reinvested": share_summary["total_reinvested"] or 0,
#         "amount_reinvested": share_summary["amount_reinvested"] or 0,
#     })

#     # Section 3: Transaction History
#     for txn in transactions:
#         data.append({
#             "section": "Transaction History",
#             "date": txn["date"],
#             "transfer_type": txn["transfer_type"],
#             "no_of_share": txn["no_of_share"],
#             "rate": txn["rate"],
#             "amount": txn["amount"]
#         })

#     return data

# New Report Format 2 START from here

# def execute(filters=None):
#     # Fetch Share Member Details
#     member_details = frappe.db.get_value(
#         "Share Members",
#         {"name": filters.get("member_code")},
#         ["name", "title", "date_of_birth", "mobile", "address", "nominee"],
#         as_dict=True
#     )

#     # Fetch Lifetime Shareholding Summary
#     share_summary = frappe.db.sql("""
#         SELECT
#             SUM(CASE WHEN transfer_type = 'Issue' THEN no_of_share ELSE 0 END) AS total_issued,
#             SUM(CASE WHEN transfer_type = 'Purchase' THEN no_of_share ELSE 0 END) AS total_purchased,
#             SUM(CASE WHEN transfer_type = 'Reinvest' THEN no_of_share ELSE 0 END) AS total_reinvested,
#             SUM(CASE WHEN transfer_type = 'Issue' THEN amount ELSE 0 END) AS amount_issued,
#             SUM(CASE WHEN transfer_type = 'Purchase' THEN amount ELSE 0 END) AS amount_purchased,
#             SUM(CASE WHEN transfer_type = 'Reinvest' THEN amount ELSE 0 END) AS amount_reinvested,
#             AVG(CASE WHEN transfer_type = 'Issue' THEN rate ELSE NULL END) AS avg_rate_issued,
#             AVG(CASE WHEN transfer_type = 'Purchase' THEN rate ELSE NULL END) AS avg_rate_purchased,
#             AVG(CASE WHEN transfer_type = 'Reinvest' THEN rate ELSE NULL END) AS avg_rate_reinvested
#         FROM `tabShare Members Records`
#         WHERE parent = %s
#     """, (filters.get("member_code")), as_dict=True)[0]

#     # Fetch Current Total Shares and Latest Share Price
#     total_shares = frappe.db.sql("""
#         SELECT
#             SUM(CASE WHEN transfer_type IN ('Issue', 'Reinvest') THEN no_of_share ELSE 0 END) -
#             SUM(CASE WHEN transfer_type = 'Purchase' THEN no_of_share ELSE 0 END) AS current_shares
#         FROM `tabShare Members Records`
#         WHERE parent = %s
#     """, (filters.get("member_code")), as_dict=True)[0].get('current_shares', 0)

#     latest_share_price = frappe.db.sql("""
#         SELECT share_price
#         FROM `tabShare Price`
#         ORDER BY update_on DESC LIMIT 1
#     """, as_dict=True)
#     latest_share_price = latest_share_price[0].get('share_price') if latest_share_price else 0

#     current_value = total_shares * latest_share_price

#     # Fetch Ledger Details
#     ledger_details = frappe.db.sql("""
#         SELECT
#             smr.date AS date,
#             st.name AS transaction_id,
#             smr.transfer_type,
#             smr.rate,
#             smr.no_of_share,
#             smr.amount
#         FROM `tabShare Members Records` smr
#         LEFT JOIN `tabShare Transaction` st ON smr.parent = st.name
#         WHERE smr.parent = %s
#         AND (%s IS NULL OR smr.date >= %s)
#         AND (%s IS NULL OR smr.date <= %s)
#         ORDER BY smr.date ASC
#     """, (filters.get("member_code"), filters.get("from_date"), filters.get("from_date"),
#           filters.get("to_date"), filters.get("to_date")), as_dict=True)

#     # Prepare Columns
#     columns = [
#         {"fieldname": "metric", "label": "Metric", "fieldtype": "Data", "width": 200},
#         {"fieldname": "total_no", "label": "Total No.", "fieldtype": "Float", "width": 150},
#         {"fieldname": "total_amount", "label": "Total Amount", "fieldtype": "Currency", "width": 150},
#         {"fieldname": "avg_rate", "label": "Avg Rate", "fieldtype": "Currency", "width": 150},
#     ]

#     # Prepare Data for Lifetime Summary
#     data = [
#         {
#             "metric": "Share Issue",
#             "total_no": share_summary.total_issued or 0,
#             "total_amount": share_summary.amount_issued or 0,
#             "avg_rate": share_summary.avg_rate_issued or 0,
#         },
#         {
#             "metric": "Share Purchase",
#             "total_no": share_summary.total_purchased or 0,
#             "total_amount": share_summary.amount_purchased or 0,
#             "avg_rate": share_summary.avg_rate_purchased or 0,
#         },
#         {
#             "metric": "Share Reinvest",
#             "total_no": share_summary.total_reinvested or 0,
#             "total_amount": share_summary.amount_reinvested or 0,
#             "avg_rate": share_summary.avg_rate_reinvested or 0,
#         },
#     ]

#     # Add Total Summary as Message
#     frappe.msgprint(f"""
#         Total No. of Shares: {total_shares}
#         Current Value of Shares: {current_value}
#         Latest Share Price: {latest_share_price}
#     """)

#     # Add Ledger Details to the Report
#     data += ledger_details

#     return columns, data

# New Report Format 3 START from here

def execute(filters=None):
    # Ensure filters are passed and contains member_code
    if not filters:
        return "Filters are missing."

    # Get the member code from filters (This could be from a custom filter field)
    member_code = filters.get('member_code')

    if not member_code:
        return "Member code is missing."
    
    # Fetch Share Member details
    try:
        # Fetch the Share Member document using the member_code
        share_member = frappe.get_doc("Share Members", member_code)

        # Prepare the member details dictionary
        member_details = {
            'name': share_member.title,
            'dob': share_member.date_of_birth,
            'mobile': share_member.mobile,
            'address': share_member.address,
            'nominee': share_member.nominee,
        }

        # Return the member details
        return member_details

    except frappe.DoesNotExistError:
        return f"Share Member with member code {member_code} does not exist."