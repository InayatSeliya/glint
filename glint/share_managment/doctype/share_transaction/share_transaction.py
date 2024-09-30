# Copyright (c) 2024, Inayatali Seliya and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ShareTransaction(Document):
	def validate(self):
		self.no_of_shares = self.amount / self.rate
		
	# pass
