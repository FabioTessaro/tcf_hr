import unittest

import frappe

from tcf_hr.api.files import MAX_BYTES, check_upload, safe_filename


class TestFiles(unittest.TestCase):
	def test_safe_filename(self):
		self.assertEqual(safe_filename("../../etc/passwd.PDF"), "passwd.pdf")
		self.assertEqual(safe_filename("C:\\docs\\receipt 1.JPG"), "receipt 1.jpg")
		self.assertEqual(safe_filename(None), "file")
		self.assertLessEqual(len(safe_filename("a" * 500 + ".pdf")), 140)

	def test_accepts_valid_files(self):
		self.assertIsNone(check_upload("r.pdf", 1000, b"%PDF-1.7"))
		self.assertIsNone(check_upload("r.png", 1000, b"\x89PNG\r\n"))
		self.assertIsNone(check_upload("r.JPG", 1000, b"\xff\xd8\xff"))
		self.assertIsNone(check_upload("r.docx", 1000, b"PK\x03\x04"))
		self.assertIsNone(check_upload("r.pdf", MAX_BYTES, b"%PDF"))

	def test_rejects_bad_files(self):
		for name, size, head in [
			("r.exe", 10, b"MZ"),
			("r.svg", 10, b"<svg"),
			("r", 10, b"x"),
			("r.pdf", 0, b""),
			("r.pdf", MAX_BYTES + 1, b"%PDF"),
			("r.pdf", 10, b"MZ\x90"),  # claims to be a pdf
			("r.png", 10, b"%PDF"),
		]:
			with self.subTest(name=name, size=size):
				self.assertIsNotNone(check_upload(name, size, head))
