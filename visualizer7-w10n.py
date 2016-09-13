import bpy, random, argparse, sys, time, os, json
from random import randint
from enum import Enum

layers_tfff = (
    True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False
    )
kmPerBlend = 10.
renderLocation = None
year, day = None, None  # day is in 365 format

pomegrante =
"http://airsl2.gesdisc.eosdis.nasa.gov/pomegranate/Aqua_AIRS_Level2/AIRX2RET.006/{}/{}/AIRS.{}.{}.{}.L2.RetStd.v6.0.0.0.".format(year, day, year, month, granule)
