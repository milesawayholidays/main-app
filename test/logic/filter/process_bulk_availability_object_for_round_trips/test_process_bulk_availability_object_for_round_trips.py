import unittest
import json
import sys
import os
import pprint

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../../'))

from src.global_state import state
from src.config import config

from src.data_types.enums import SOURCE

from src.currencies.cash import handler as cash_handler
from src.currencies.mileage import handler as mileage_handler

from src.logic.filter import flight_Filter as ff

from .testresults import expected_results

class TestProcessBulkAvailabilityObjectForRoundTrips(unittest.TestCase):

  @classmethod
  def setUpClass(cls):
    try:
      testcases = open("test/logic/filter/process_bulk_availability_object_for_round_trips/testcases.json")
      cls.test_cases = json.load(testcases)
      testcases.close()

      cls.expected_results = expected_results

      state.load()
      config.load()
      cash_handler.load("USD", "test")
      mileage_handler.load("test", "test")
    except Exception as e:
      print(f"Cannot load test data: {e}")
      cls.skipTest(cls, f"Cannot load test data: {e}")

  def test_on_working_case(self):
    input = self.test_cases["On_Working_Case"]
    expected = self.expected_results["On_Working_Case"]

    result = ff.process_bulk_availability_object_for_round_trips(input, SOURCE.AZUL)

    result_str = pprint.pformat(result, indent=2, width=120)

    with open("test/logic/filter/process_bulk_availability_object_for_round_trips/output_on_working_case.txt", "w") as f:
      f.write(result_str)

    self.assertEqual(result, expected)


  def test_on_empty(self):
    input = self.test_cases["On_Empty_Case"]
    expected = self.expected_results["On_Empty_Case"]

    result = ff.process_bulk_availability_object_for_round_trips(input, SOURCE.AZUL)

    result_str = pprint.pformat(result, indent=2, width=120)
    with open("test/logic/filter/process_bulk_availability_object_for_round_trips/output_on_empty_case.txt", "w") as f:
      f.write(result_str)

    self.assertEqual(result, expected)

  def test_on_cannot_find_trips(self):
    input = self.test_cases["On_Cannot_Find_Trips_Case"]
    expected = self.expected_results["On_Cannot_Find_Trips_Case"]

    result = ff.process_bulk_availability_object_for_round_trips(input, SOURCE.AZUL)

    result_str = pprint.pformat(result, indent=2, width=120)
    with open("test/logic/filter/process_bulk_availability_object_for_round_trips/output_on_cannot_find_trips.txt", "w") as f:
      f.write(result_str)

    self.assertEqual(ff.process_bulk_availability_object_for_round_trips(input, SOURCE.AZUL), expected)
