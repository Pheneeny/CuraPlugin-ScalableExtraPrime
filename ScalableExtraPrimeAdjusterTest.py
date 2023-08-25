# Copyright (c) 2018 Pheneeny
# The ScalableExtraPrime plugin is released under the terms of the AGPLv3 or higher.

import unittest
import ScalableExtraPrimeAdjuster as lepa

gcode1 = "G1 X82.559 Y142.583 E510.05313"
gcode2 = "G1 F1500 E503.55313"
gcode3 = "G0 F7200 X83.64 Y142.561"
gcode4 = "G0 F7200 X83.64 Y142.561 ;comment"
g1split = lepa.split_gcode(gcode1)
g2split = lepa.split_gcode(gcode2)
g3split = lepa.split_gcode(gcode3)
g4split = lepa.split_gcode(gcode4)


class TestScalablePrimeAdjusterTest(unittest.TestCase):

    def test_split_gcode(self):

        self.assertEqual([("G", "1"), ("X", "82.559"), ("Y", "142.583"), ("E", "510.05313")], lepa.split_gcode(gcode1))
        self.assertEqual([("G", "1"), ("F", "1500"), ("E", "503.55313")], lepa.split_gcode(gcode2))
        self.assertEqual([("G", "0"), ("F", "7200"), ("X", "83.64"), ("Y", "142.561")], lepa.split_gcode(gcode3))
        self.assertEqual([("G", "0"), ("F", "7200"), ("X", "83.64"), ("Y", "142.561"), (";", "comment")], lepa.split_gcode(gcode4))

    def test_combine_gcode(self):
        self.assertEqual(gcode1, lepa.combine_gcode(lepa.split_gcode(gcode1)))
        self.assertEqual(gcode2, lepa.combine_gcode(lepa.split_gcode(gcode2)))
        self.assertEqual(gcode3, lepa.combine_gcode(lepa.split_gcode(gcode3)))
        self.assertEqual(gcode2+" ;comment", lepa.combine_gcode(lepa.split_gcode(gcode2), "comment"))

    def test_get_point_from_split(self):
        self.assertEqual(lepa.Point(82.559, 142.583), lepa.get_point_from_split(g1split))
        self.assertEqual(None, lepa.get_point_from_split(g2split))
        self.assertEqual(lepa.Point(83.64, 142.561), lepa.get_point_from_split(g3split))

    def test_get_e_from_split(self):
        self.assertEqual(510.05313, lepa.get_e_from_split(g1split))
        self.assertEqual(503.55313, lepa.get_e_from_split(g2split))
        self.assertEqual(None, lepa.get_e_from_split(g3split))
        self.assertEqual(None, lepa.get_e_from_split(g4split))

    def test_get_distance(self):
        origin = lepa.Point(0, 0)
        p2 = lepa.Point(0, 5)
        p3 = lepa.Point(5, 0)
        self.assertEqual(5, lepa.get_distance(origin, p2))
        self.assertEqual(5, lepa.get_distance(origin, p3))
        self.assertEqual(7.0710678118654755, lepa.get_distance(p3, p2))

    def test_get_extra_e(self):
        min_travel = 0
        max_travel = 200
        min_prime = 0
        max_prime = 2

        self.assertEqual(0, lepa.get_extra_e(min_travel, max_travel, min_prime, max_prime, 0))
        self.assertEqual(0.5, lepa.get_extra_e(min_travel, max_travel, min_prime, max_prime, 50))
        self.assertEqual(1, lepa.get_extra_e(min_travel, max_travel, min_prime, max_prime, 100))
        self.assertEqual(1.5, lepa.get_extra_e(min_travel, max_travel, min_prime, max_prime, 150))
        self.assertEqual(2, lepa.get_extra_e(min_travel, max_travel, min_prime, max_prime, 200))

        self.assertEqual(0, lepa.get_extra_e(0, 0, min_prime, max_prime, 0))
        self.assertEqual(2, lepa.get_extra_e(0, 0, min_prime, max_prime, 500))
        self.assertEqual(0, lepa.get_extra_e(min_travel, max_travel, 0, 0, 0))
        self.assertEqual(0, lepa.get_extra_e(min_travel, max_travel, 0, 0, 200))

    def test_set_e_in_split(self):
        adjusted1 = lepa.set_e_in_split(g1split, 500)
        self.assertEqual(500, lepa.get_e_from_split(adjusted1))
        adjusted2 = lepa.set_e_in_split(g2split, 500)
        self.assertEqual(500, lepa.get_e_from_split(adjusted2))
        adjusted3 = lepa.set_e_in_split(g3split, 500)
        self.assertEqual(None, lepa.get_e_from_split(adjusted3))
        adjusted4 = lepa.set_e_in_split(g4split, 500)
        self.assertEqual(None, lepa.get_e_from_split(adjusted4))

    def test_should_add_extra_filament(self):
        self.assertTrue(lepa.should_add_extra_filament(5, 5, True, True))
        self.assertTrue(lepa.should_add_extra_filament(5, 5, True, False))
        self.assertTrue(lepa.should_add_extra_filament(5, 0, True, True))
        self.assertTrue(lepa.should_add_extra_filament(5, 0, False, True))
        self.assertFalse(lepa.should_add_extra_filament(5, 5, False, True))
        self.assertFalse(lepa.should_add_extra_filament(5, 0, True, False))

    def test_parse_gcode_with_retraction(self):
        gcode = '''G1 X10.00 Y0.00 E2.00
G1 X10.000 Y10.00 E4.00
G1 F1500 E3.5
G0 F7200 X0.00 Y10.00
G0 F7200 X0.00 Y0.00
G1 E4.00
G1 X10.00 Y0.00 E6.00
G1 X10.000 Y10.00 E8.00
G1 F1500 E7.5
G0 F7200 X0.00 Y10.00
G0 F7200 X0.00 Y0.00
G1 E8.00
G1 X10.00 Y0.00 E10.00
'''
        expected_output='''G1 X10.00 Y0.00 E2.0
G1 X10.000 Y10.00 E4.0
G1 F1500 E3.5
G0 F7200 X0.00 Y10.00
G0 F7200 X0.00 Y0.00
G1 E4.2 ;Adjusted e by 0.2mm
G1 X10.00 Y0.00 E6.2
G1 X10.000 Y10.00 E8.2
G1 F1500 E7.7
G0 F7200 X0.00 Y10.00
G0 F7200 X0.00 Y0.00
G1 E8.4 ;Adjusted e by 0.2mm
G1 X10.00 Y0.00 E10.4
'''
        output = lepa.parse_and_adjust_gcode(["","",gcode, ""], 0,200,0,2)
        output = output[2]
        self.assertEqual(expected_output, output)

    def test_parse_gcode_without_retraction(self):
        gcode = '''G1 X10.00 Y0.00 E2.00
G1 X10.000 Y10.00 E4.00
G0 F7200 X0.00 Y10.00
G0 F7200 X0.00 Y0.00
G1 X10.00 Y0.00 E6.00
G1 X10.000 Y10.00 E8.00
G0 F7200 X0.00 Y10.00
G0 F7200 X0.00 Y0.00
G1 X10.00 Y0.00 E10.00
'''
        expected_output = '''G1 X10.00 Y0.00 E2.0
G1 X10.000 Y10.00 E4.0
G0 F7200 X0.00 Y10.00
G0 F7200 X0.00 Y0.00
G1 E4.2 ;Adjusted e by 0.2mm
G1 X10.00 Y0.00 E6.2
G1 X10.000 Y10.00 E8.2
G0 F7200 X0.00 Y10.00
G0 F7200 X0.00 Y0.00
G1 E8.4 ;Adjusted e by 0.2mm
G1 X10.00 Y0.00 E10.4
'''
        output = lepa.parse_and_adjust_gcode(["","",gcode, ""], 0, 200, 0, 2, True)
        output = output[2]
        self.assertEqual(expected_output, output)

    def test_parse_gcode_no_prime_without_retraction_no_retraction(self):
        self.maxDiff = None
        gcode = '''G1 X10.00 Y0.00 E2.00
G1 X10.000 Y10.00 E4.00
G0 F7200 X0.00 Y10.00
G0 F7200 X0.00 Y0.00
G1 X10.00 Y0.00 E6.00
G1 X10.000 Y10.00 E8.00
G0 F7200 X0.00 Y10.00
G0 F7200 X0.00 Y0.00
G1 X10.00 Y0.00 E10.00
'''
        expected_output = '''G1 X10.00 Y0.00 E2.0
G1 X10.000 Y10.00 E4.0
G0 F7200 X0.00 Y10.00
G0 F7200 X0.00 Y0.00
G1 X10.00 Y0.00 E6.0
G1 X10.000 Y10.00 E8.0
G0 F7200 X0.00 Y10.00
G0 F7200 X0.00 Y0.00
G1 X10.00 Y0.00 E10.0
'''
        output = lepa.parse_and_adjust_gcode(["","",gcode, ""], 0, 200, 0, 2, True, False)
        output = output[2]
        self.assertEqual(expected_output, output)

    def test_parse_gcode_no_prime_without_retraction_mixed(self):
        self.maxDiff = None
        gcode = '''G1 X10.00 Y0.00 E2.0
G1 X10.000 Y10.00 E4.0
G1 F1500 E3.5
G0 F7200 X0.00 Y10.0
G0 F7200 X0.00 Y0.0
G1 E4.00
G1 X10.00 Y0.00 E6.0
G1 X10.000 Y10.00 E8.0
G0 F7200 X0.00 Y10.0
G0 F7200 X0.00 Y0.0
G1 X10.00 Y0.00 E10.0
'''
        expected_output = '''G1 X10.00 Y0.00 E2.0
G1 X10.000 Y10.00 E4.0
G1 F1500 E3.5
G0 F7200 X0.00 Y10.0
G0 F7200 X0.00 Y0.0
G1 E4.2 ;Adjusted e by 0.2mm
G1 X10.00 Y0.00 E6.2
G1 X10.000 Y10.00 E8.2
G0 F7200 X0.00 Y10.0
G0 F7200 X0.00 Y0.0
G1 X10.00 Y0.00 E10.2
'''
        output = lepa.parse_and_adjust_gcode(["","",gcode, ""], 0, 200, 0, 2, True, False)
        output = output[2]
        self.assertEqual(expected_output, output)

    def test_parse_gcode_with_G92(self):
        gcode = '''G1 X10.00 Y0.00 E2.00
G1 X10.000 Y10.00 E4.00
G1 F1500 E3.5
G0 F7200 X0.00 Y10.00
G0 F7200 X0.00 Y0.00
G1 E4.00
G92 E0
G1 X10.00 Y0.00 E2.00
G1 X10.000 Y10.00 E4.00
G1 F1500 E3.5
G0 F7200 X0.00 Y10.00
G0 F7200 X0.00 Y0.00
G1 E4.00
G1 X10.00 Y0.00 E6.00
'''
        expected_output='''G1 X10.00 Y0.00 E2.0
G1 X10.000 Y10.00 E4.0
G1 F1500 E3.5
G0 F7200 X0.00 Y10.00
G0 F7200 X0.00 Y0.00
G1 E4.2 ;Adjusted e by 0.2mm
G92 E0
G1 X10.00 Y0.00 E2.0
G1 X10.000 Y10.00 E4.0
G1 F1500 E3.5
G0 F7200 X0.00 Y10.00
G0 F7200 X0.00 Y0.00
G1 E4.2 ;Adjusted e by 0.2mm
G1 X10.00 Y0.00 E6.2
'''
        output = lepa.parse_and_adjust_gcode(["","",gcode, ""], 0,200,0,2)
        output = output[2]
        self.assertEqual(expected_output, output)


    def test_args_in_comment(self):
        gcode = "G1 X1 Y280 ;move along X-Y"
        split = lepa.split_gcode(gcode)
        point = lepa.get_point_from_split(split)
        self.assertEqual(point, lepa.Point(1, 280))

    def test_parse_gcode_with_G91_last_layer(self):
        self.maxDiff = None
        gcode = '''G1 X10.00 Y0.00 E2.00
G1 X10.000 Y10.00 E4.00
G1 F1500 E3.5
G0 F7200 X0.00 Y10.00
G0 F7200 X0.00 Y0.00
G1 E4.00
G92 E0
G1 X10.00 Y0.00 E2.00
G1 X10.000 Y10.00 E4.00
G1 F1500 E3.5
G0 F7200 X0.00 Y10.00
G0 F7200 X0.00 Y0.00
G1 E4.00
G1 X10.00 Y0.00 E6.00
'''
        expected_output = '''G1 X10.00 Y0.00 E2.0
G1 X10.000 Y10.00 E4.0
G1 F1500 E3.5
G0 F7200 X0.00 Y10.00
G0 F7200 X0.00 Y0.00
G1 E4.2 ;Adjusted e by 0.2mm
G92 E0
G1 X10.00 Y0.00 E2.0
G1 X10.000 Y10.00 E4.0
G1 F1500 E3.5
G0 F7200 X0.00 Y10.00
G0 F7200 X0.00 Y0.00
G1 E4.2 ;Adjusted e by 0.2mm
G1 X10.00 Y0.00 E6.2
'''
        last_layer = '''G91
G1 E-2 F300
'''
        output = lepa.parse_and_adjust_gcode(["", "", gcode, last_layer], 0, 200, 0, 2)
        self.assertEqual(expected_output, output[2])
        self.assertEqual(last_layer, output[3])

    def test_and_throw_M83(self):
        gcode = '''G1 X10.00 Y0.00 E2.00
G1 X10.000 Y10.00 E4.00
G1 F1500 E3.5
M83
G0 F7200 X0.00 Y10.00
G0 F7200 X0.00 Y0.00
G1 E4.00
G92 E0
G1 X10.00 Y0.00 E2.00
G1 X10.000 Y10.00 E4.00
G1 F1500 E3.5
G0 F7200 X0.00 Y10.00
G0 F7200 X0.00 Y0.00
G1 E4.00
G1 X10.00 Y0.00 E6.00
'''
        try:
            output = lepa.parse_and_adjust_gcode(["", "", gcode, ""], 0, 200, 0, 2)
        except:
            return
        self.fail("Failed to throw exception for M83")


if __name__ == "__main__":
    unittest.main()