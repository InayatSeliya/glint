# Copyright (c) 2024, Inayatali Seliya and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ShareMembers(Document):
	def before_save(self):
		# This will save Create Member Code data from Main Code and Sub Code
		if self.main_code and self.sub_code:
			self.member_code = f"{self.main_code}-{self.sub_code}"


	# 	if self.get('member_type') == 'Main Member':
	# 		# it create Main member's group in COA
	# 		group_name = f"{self.get('main_code')} - {self.get('title')}"
	# 		account_group = frappe.get_doc({
	# 			'doctype': 'Account',
	# 			'account_name': group_name,
	# 			'parent_account': 'Shareholders Funds - GH',
	# 			'is_group': 1,
	# 			'company': self.company
	# 		})
	# 		account_group.insert()

	# 		# It create Main Member's self account in COA
	# 		main_member_child_account = frappe.get_doc({
	# 			'doctype': 'Account',
	# 			'account_name': f"{self.get('main_code')} - Self",
	# 			'parent_account': account_group.name,
	# 			'is_group': 0,
	# 			'company': self.company
	# 		})
	# 		main_member_child_account.insert()

	# 	elif self.get('member_type') == 'Sub Member':
	# 		# create Sub Member's account in COA under Parent Member Group account
	# 		main_member_account_group = frappe.get_value('Account', {'account_name': self.get('main_member')}, 'name')
	# 		if main_member_account_group:
	# 			child_account = frappe.get_doc({
	# 				'doctype': 'Account',
	# 				'account_name': f"{self.get('main_code')} - {self.get('title')}",
	# 				'parent_account': main_member_account_group,
	# 				'is_group': 0,
	# 				'company': self.company
	# 			})
	# 			child_account.insert()



	# To delete account from COA
	# def on_trash(self):
	# 	account_name = frappe.get_value('Account', {'account_name': self.get('title')}, 'name')

	# 	if account_name:
	# 		try:
	# 			frappe.delete_doc('Account', account_name)
	# 			frappe.db.commit()
	# 			frappe.msgprint(f"Deleted COA account: {account_name}")
	# 		except frappe.DoesNotExistError:
	# 			frappe.msgprint(f"Account {account_name} does not exist.")
	# 		except Exception as e:
	# 			frappe.throw(f"Failed to delete COA account: {str(e)}")
			

		

	
