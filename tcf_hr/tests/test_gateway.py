import unittest

import frappe

from tcf_hr.api.gateway import allowed_ops, clamp_fields, clean_payload

CONFIG = {"doctypes": {"Salary Slip": {"ops": ["read"]}, "Leave Application": {"ops": ["read", "create"]}}}


class TestGatewayHelpers(unittest.TestCase):
	def test_allowed_ops(self):
		self.assertEqual(allowed_ops(CONFIG, "Salary Slip"), {"read"})
		self.assertEqual(allowed_ops(CONFIG, "Leave Application"), {"read", "create"})
		self.assertEqual(allowed_ops(CONFIG, "User"), set())

	def test_clamp_fields_default_and_permitted(self):
		self.assertEqual(clamp_fields(None, ["name", "status"]), ["name"])
		self.assertEqual(clamp_fields(["name", "status"], ["name", "status"]), ["name", "status"])

	def test_clamp_fields_rejects_unpermitted_and_expressions(self):
		for bad in (["salary"], ["count(name) as c"], ["name; drop table x"], ["`name`"], [1]):
			with self.assertRaises(frappe.PermissionError):
				clamp_fields(bad, ["name", "status"])

	def test_clean_payload_drops_protected_and_unwritable(self):
		data = {
			"doctype": "Expense Claim",
			"owner": "attacker@example.com",
			"docstatus": 1,
			"employee": "EMP-1",
			"approval_status": "Approved",
			"expenses": [{"amount": 5, "parent": "X", "docstatus": 1, "doctype": "Expense Claim Detail"}],
		}
		cleaned = clean_payload(data, writable=["employee"], table_fields=["expenses"])
		self.assertEqual(cleaned, {"employee": "EMP-1", "expenses": [{"amount": 5}]})

	def test_clean_payload_table_rows_must_be_dicts(self):
		cleaned = clean_payload({"expenses": ["x", {"amount": 1}]}, writable=[], table_fields=["expenses"])
		self.assertEqual(cleaned, {"expenses": [{"amount": 1}]})
		self.assertEqual(clean_payload({"expenses": "x"}, [], ["expenses"]), {"expenses": []})

	def test_clean_payload_cannot_choose_name_or_modified(self):
		cleaned = clean_payload(
			{"name": "HACK-1", "modified": "2000-01-01", "employee": "EMP-1"},
			writable=["name", "modified", "employee"],
			table_fields=[],
		)
		self.assertEqual(cleaned, {"employee": "EMP-1"})
