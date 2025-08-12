import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../../'))

from src.data_types.enums import CABIN
from src.data_types.summary_objs import summary_trip

expected_results = {
  "On_Working_Case": {
    CABIN.Y: [
      summary_trip(ID='1', city='Cape Town', totalCost=1317402, distance=7643.583092294503),
      summary_trip(ID='2', city='Dubai', totalCost=1279000, distance=7643.583092294503),
      summary_trip(ID='3', city='São Paulo', totalCost=1960000, distance=9404.594683625408),
      summary_trip(ID='4', city='Paris (Roissy-en-France, Val-d\'Oise)', totalCost=1907200, distance=9404.594683625408),
      summary_trip(ID='5', city='Los Angeles', totalCost=168150, distance=8753.827447474696),
      summary_trip(ID='6', city='Narita', totalCost=165345, distance=8753.827447474696),
      summary_trip(ID='7', city='London', totalCost=129600, distance=5539.7039463111205),
      summary_trip(ID='8', city='New York', totalCost=123380, distance=5539.7039463111205),
      summary_trip(ID='9', city='Sydney (Mascot)', totalCost=141000, distance=6293.451484746663)
    ],
    CABIN.W: [
      summary_trip(ID='3', city='São Paulo', totalCost=2600000, distance=9404.594683625408),
      summary_trip(ID='4', city='Paris (Roissy-en-France, Val-d\'Oise)', totalCost=2543000, distance=9404.594683625408),
      summary_trip(ID='7', city='London', totalCost=258000, distance=5539.7039463111205),
      summary_trip(ID='8', city='New York', totalCost=245280, distance=5539.7039463111205)
    ],
    CABIN.J: [
      summary_trip(ID='1', city='Cape Town', totalCost=1605123, distance=7643.583092294503),
      summary_trip(ID='2', city='Dubai', totalCost=1566000, distance=7643.583092294503),
      summary_trip(ID='5', city='Los Angeles', totalCost=392250, distance=8753.827447474696),
      summary_trip(ID='6', city='Narita', totalCost=385245, distance=8753.827447474696),
      summary_trip(ID='9', city='Sydney (Mascot)', totalCost=322000, distance=6293.451484746663)
    ],
    CABIN.F: [
      summary_trip(ID='5', city='Los Angeles', totalCost=630350, distance=8753.827447474696),
      summary_trip(ID='6', city='Narita', totalCost=616345, distance=8753.827447474696)
    ]
  },
  "On_Empty_Case": None,
}