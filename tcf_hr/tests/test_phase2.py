import unittest
from unittest.mock import MagicMock, patch

import frappe

from tcf_hr.api.checkin import clean_coordinates, next_action
from tcf_hr.api.notifications import parse_message
from tcf_hr.api.profile import compact
from tcf_hr.geocoding import cache_key, format_address


class TestParseMessage(unittest.TestCase):
	def test_bold_and_plain_parts(self):
		parts = parse_message("<strong>Your</strong> Leave Application HR-1 has been <b>Approved</b> by Ann")
		self.assertEqual(
			parts,
			[
				{"text": "Your", "bold": True},
				{"text": " Leave Application HR-1 has been ", "bold": False},
				{"text": "Approved", "bold": True},
				{"text": " by Ann", "bold": False},
			],
		)

	def test_other_tags_are_dropped_and_entities_decoded(self):
		parts = parse_message('<script>alert(1)</script><a href="x">Tom &amp; Jerry</a>')
		self.assertEqual(parts, [{"text": "alert(1)Tom & Jerry", "bold": False}])
		# Escaped markup in the stored message becomes literal text, which Vue renders as text, not HTML
		self.assertEqual(parse_message("&lt;b&gt;x&lt;/b&gt;"), [{"text": "<b>x</b>", "bold": False}])

	def test_empty(self):
		self.assertEqual(parse_message(None), [])
		self.assertEqual(parse_message(""), [])


class TestCheckinHelpers(unittest.TestCase):
	def test_next_action(self):
		self.assertEqual(next_action(None), "IN")
		self.assertEqual(next_action("OUT"), "IN")
		self.assertEqual(next_action("IN"), "OUT")

	def test_clean_coordinates(self):
		self.assertEqual(clean_coordinates("45.4642035", "9.189982"), (45.464204, 9.189982))
		for bad in [(None, None), ("x", "1"), (91, 0), (0, 181), (0, 0), ("nan", "1")]:
			with self.subTest(bad=bad):
				self.assertIsNone(clean_coordinates(*bad))


class TestGeocodingHelpers(unittest.TestCase):
	def test_format_address_prefers_structured_parts(self):
		payload = {
			"display_name": "12, Via Roma, Centro, Milano, Lombardia, 20121, Italia",
			"address": {
				"road": "Via Roma",
				"house_number": "12",
				"postcode": "20121",
				"city": "Milano",
				"country": "Italia",
				"state": "Lombardia",
			},
		}
		self.assertEqual(format_address(payload), "Via Roma 12, 20121 Milano, Italia")

	def test_format_address_without_street_or_number(self):
		self.assertEqual(
			format_address({"address": {"village": "Bellagio", "country": "Italia"}}), "Bellagio, Italia"
		)

	def test_format_address_falls_back_to_display_name_or_none(self):
		self.assertEqual(format_address({"display_name": "Somewhere"}), "Somewhere")
		for bad in (None, {}, [], {"address": {}}, {"display_name": ""}):
			with self.subTest(bad=bad):
				self.assertIsNone(format_address(bad))

	def test_cache_key_rounds_to_about_ten_metres(self):
		self.assertEqual(cache_key(45.4642035, 9.189982, "en"), cache_key(45.46420, 9.18998, "en"))
		self.assertNotEqual(cache_key(45.4642, 9.19, "en"), cache_key(45.4642, 9.19, "it"))


class TestProfileHelpers(unittest.TestCase):
	def test_compact_drops_empty_values(self):
		self.assertEqual(
			compact({"a": "x", "b": None, "c": "", "d": 0, "e": "0"}),
			{"a": "x", "e": "0"},
		)
