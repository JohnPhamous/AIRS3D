import bpy, random, argparse, sys, time, os, json
from random import randint
from enum import Enum

layers_tfff = (
    True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False
    )
kmPerBlend = 10.
renderLocation = None
