# Modified for use on JPL machines
import bpy
import random
import argparse
import sys
import time
import pickle
import os
from random import randint
import numpy as np
from math import pi
from enum import Enum

lev100 = np.array( [
    0.01610000, 0.03840000, 0.07690000, 0.1370000, 0.2244000,
    0.3454000, 0.5064000, 0.7140000, 0.9753000, 1.297200,
    1.687200, 2.152600, 2.700900, 3.339800, 4.077000,
    4.920400, 5.877600, 6.956700, 8.165500, 9.511900,
    11.00380, 12.64920, 14.45590, 16.43180, 18.58470,
    20.92240, 23.45260, 26.18290, 29.12100, 32.27440,
    35.65050, 39.25660, 43.10010, 47.18820, 51.52780,
    56.12600, 60.98950, 66.12530, 71.53980, 77.23960,
    83.23100, 89.52040, 96.11380, 103.0172, 110.2366,
    117.7775, 125.6456, 133.8462, 142.3848, 151.2664,
    160.4959, 170.0784, 180.0183, 190.3203, 200.9887,
    212.0277, 223.4415, 235.2338, 247.4085, 259.9691,
    272.9191, 286.2617, 300.0000, 314.1369, 328.6753,
    343.6176, 358.9665, 374.7241, 390.8926, 407.4738,
    424.4698, 441.8819, 459.7118, 477.9607, 496.6298,
    515.7200, 535.2322, 555.1669, 575.5248, 596.3062,
    617.5112, 639.1398, 661.1920, 683.6673, 706.5654,
    729.8857, 753.6275, 777.7897, 802.3714, 827.3713,
    852.7880, 878.6201, 904.8659, 931.5236, 958.5911,
    986.0666, 1013.948, 1042.232, 1070.917, 1100.000 ] )

# 0-based indices
ix750 = 86
ix850 = 90
ix900 = 92
ix930 = 93

cmd_controls = True
layers_tfff = (True, False, False, False, False, False, False, False, False, False,
               False, False, False, False, False, False, False, False, False, False)
kmPerBlend = 10.

if cmd_controls == False:
    args.date = 20020906
    granule = 50
    args.version = 'v6'
    outTag = ''
    horizDecim = 1
    args.vertMag = 5.0
    globe = False
    args.stillCamera = True
    args.lowRenderSettings = False
    args.circularAnimation = False
    args.spiralAnimation = False
    args.topDownAnimation = False
    args.cloudColor = 'phase'
    thickbytype = False
    args.sizeByFrac = True
    args.reduceOverlap = True
    args.cloudSolid = True
    fname_pkl = 'cld.20020922G192.AIRS_v6.pkl'
    cymdg = str(args.date + granule)

renderLocation = None
earthTexturePath = None
earthBumpTexturePath = None
granLong = None
granLat = None

if cmd_controls == True:

    parser = argparse.ArgumentParser(
        description='Generate some real fancy 3D AIRS clouds')
    parser.add_argument('--date', action='store', dest='date',
                        default='20020906', help='date yyyymmdd')
    parser.add_argument('--gran', action='store', dest='granule', default='050', type=str,
                        help='granule number (50)')
    parser.add_argument('--ver', action='store', dest='version',
                        default='v6', help='retrieval version v5/v6')
    parser.add_argument('--outtag', action='store', dest='outTag',
                        default='', help='Tag to embed in output file name')
    parser.add_argument('--dec', action='store',
                        dest='horizDecim', default='1', help='1-10')
    parser.add_argument('--vmag', action='store', dest='vertMag', default=5.0, type=float,
                        help='vertical magnification: 1-10+')
    parser.add_argument('--animlen', action='store', dest='animLen', default=10.0, type=float,
                        help='animation length in seconds: 5-10+')

    parser.add_argument('--globe', dest='globe', action='store_true')
    parser.add_argument('--no-globe', dest='globe', action='store_false')
    parser.set_defaults(globe=False)

    parser.add_argument('--still', dest='stillCamera', action='store_true')
    parser.add_argument('--no-still', dest='stillCamera', action='store_false')
    parser.set_defaults(stillCamera=True)

    parser.add_argument(
        '--lowrender', dest='lowRenderSettings', action='store_true')
    parser.add_argument(
        '--no-lowrender', dest='lowRenderSettings', action='store_false')
    parser.set_defaults(lowRenderSettings=False)

    parser.add_argument('--circular',
                        dest='circularAnimation', action='store_true')
    parser.add_argument('--no-circular',
                        dest='circularAnimation', action='store_false')
    parser.set_defaults(circularAnimation=False)

    parser.add_argument('--spiral',
                        dest='spiralAnimation', action='store_true')
    parser.add_argument('--no-spiral',
                        dest='spiralAnimation', action='store_false')
    parser.set_defaults(spiralAnimation=False)

    parser.add_argument('--topdown',
                        dest='topDownAnimation', action='store_true')
    parser.add_argument('--no-topdown',
                        dest='topDownAnimation', action='store_false')
    parser.set_defaults(topDownAnimation=False)

    parser.add_argument('--ttype', dest='thickbytype', action='store_true')
    parser.add_argument('--no-ttype', dest='thickbytype', action='store_false')
    parser.set_defaults(thickbytype=True)

    parser.add_argument('--cloudcolor', action='store', default='type',
                    dest='cloudColor',
                    help='method to color clouds: {white|type|phase|ctt|tsurf|nsat|dtsurf|icectt|effdiam|optdepth|test|none}')

    parser.add_argument('--planecolor', action='store', default='blue',
                    dest='planeColor',
                    help='method to color a plane: {blue|green|white|tsurf|nsat|dtsurf|h2o750|h2o850|h2o900|h2o930}')

    parser.add_argument('--sfrac', dest='sizeByFrac', action='store_true')
    parser.add_argument('--no-sfrac', dest='sizeByFrac', action='store_false')
    parser.set_defaults(sizeByFrac=True)

    parser.add_argument('--redover', dest='reduceOverlap', action='store_true')
    parser.add_argument(
        '--no-redover', dest='reduceOverlap', action='store_false')
    parser.set_defaults(reduceOverlap=True)

    parser.add_argument('--cloudsolid', dest='cloudSolid', action='store_true')
    parser.add_argument('--no-cloudsolid',
                        dest='cloudSolid', action='store_false')
    parser.set_defaults(cloudSolid=True)

    parser.add_argument('--blendout', dest='blendOut', action='store_true')
    parser.add_argument('--no-blendout', dest='blendOut', action='store_false')
    parser.set_defaults(blendOut=False)

    # parser.add_argument('--globe', action='store', dest='globe', default=False, help='True/False', type=bool)
    # parser.add_argument('--still', action='store', dest='stillCamera', default=True, help='True/False', type=bool)
    # parser.add_argument('--lowrender', action='store', dest='lowRenderSettings', default=True, help='True/False', type=bool)
    # parser.add_argument('--circularanimation', action='store',  dest='circularAnimation', default=False, help='True/False', type=bool)
    # need to trim args because the original list includes the whole blender + python command
    # print(sys.argv[5:])
    args = parser.parse_args(sys.argv[5:])
    print(args)

    # pad out granule number string to 3 digits with leading zeros if needed
    if len(args.granule) == 2:
      args.granule = "0"+args.granule
    if len(args.granule) == 1:
      args.granule = "00"+args.granule

    planeH2o = False
    if args.planeColor.lower() == 'h2o750':
        planeH2o = True
        ixh2o = ix750
    elif args.planeColor.lower() == 'h2o850':
        planeH2o = True
        ixh2o = ix850
    elif args.planeColor.lower() == 'h2o900':
        planeH2o = True
        ixh2o = ix900
    elif args.planeColor.lower() == 'h2o930':
        planeH2o = True
        ixh2o = ix930

    planeMonochrome = False
    if args.planeColor.lower() == 'blue':
        planeMonochrome = True
    elif args.planeColor.lower() == 'green':
        planeMonochrome = True
    elif args.planeColor.lower() == 'white':
        planeMonochrome = True


    fname_pkl = "cld." + args.date + "G" + \
        args.granule + ".AIRS_" + args.version + ".pkl"
    cymdg = args.date + "G" + args.granule

    if args.outTag == '':
        outTag = '_'

        if args.cloudSolid != True:
            outTag = outTag + 'Vol'

        if args.cloudColor.lower() == 'ctt':
            outTag = outTag + 'Cctt'
        elif args.cloudColor.lower() == 'type':
            outTag = outTag + 'Ccty'
        elif args.cloudColor.lower() == 'phase':
            outTag = outTag + 'Ccph'
        elif args.cloudColor.lower() == 'effdiam':
            outTag = outTag + 'Cide'
        elif args.cloudColor.lower() == 'optdepth':
            outTag = outTag + 'Ciod'
        elif args.cloudColor.lower() == 'icectt':
            outTag = outTag + 'Cict'
        elif args.cloudColor.lower() == 'tsurf':
            outTag = outTag + 'Cts'
        elif args.cloudColor.lower() == 'nsat':
            outTag = outTag + 'Ctsa'
        elif args.cloudColor.lower() == 'dtsurf':
            outTag = outTag + 'Cdts'
        elif args.cloudColor.lower() == 'white':
            outTag = outTag + 'Cwht'
        elif args.cloudColor.lower() == 'test':
            outTag = outTag + 'Ctst'

        if args.planeColor.lower() == 'tsurf':
            outTag = outTag + 'Pts'
        elif args.planeColor.lower() == 'nsat':
            outTag = outTag + 'Ptsa'
        elif args.planeColor.lower() == 'dtsurf':
            outTag = outTag + 'Pdts'
        elif args.planeColor.lower() == 'h2o750':
            outTag = outTag + 'Pq75'
        elif args.planeColor.lower() == 'h2o850':
            outTag = outTag + 'Pq85'
        elif args.planeColor.lower() == 'h2o900':
            outTag = outTag + 'Pq90'
        elif args.planeColor.lower() == 'h2o930':
            outTag = outTag + 'Pq93'

        if args.sizeByFrac == False:
            outTag = outTag + 'Rc'

        outTag = outTag + 'V{}'.format(int(args.vertMag))

        if args.version != 'v6':
            outTag = outTag + '_' + args.version

    else:
        outTag = '_' + args.outTag

    framesPerSec = 24
    endFrame = framesPerSec * args.animLen
    horizDecim = int(args.horizDecim)
    globe = bool(args.globe)
    # stillCamera = bool(args.stillCamera)
    # lowRenderSettings = bool(args.lowRenderSettings)
    # circularAnimation = bool(args.circularAnimation)
    # spiralAnimation = bool(args.spiralAnimation)
    # topDownAnimation = bool(args.topDownAnimation)
    thickbytype = bool(args.thickbytype)
    # sizeByFrac = bool(args.sizeByFrac)
    # reduceOverlap = bool(args.reduceOverlap)
    # cloudSolid = bool(args.cloudSolid)
    # version = args.version
    # vertMag = args.vertMag
    # date = args.date
    granule = args.granule

    print(args.lowRenderSettings)


def createLight():
    # Lighting for solid view. Other light is too intense for this and will
    # cause over exposure if used
    if args.cloudColor.lower() == 'test' or args.cloudSolid == True:
        energy = 5
        distance = 5 * 75. / kmPerBlend
    else:
        energy = 6 # 8
        distance = 200 * 75. / kmPerBlend

        # Light source setup
        # print("Creating volumetric sun...")

        # bpy.ops.object.lamp_add(type='SUN', radius=1, view_align=False,
        # location=(0, 0, 1500 / kmPerBlend))
        # bpy.context.object.data.type = 'AREA'
        # bpy.context.object.data.energy = energy
        # bpy.context.object.data.distance = distance
        # bpy.context.object.data.use_specular = False
        # bpy.context.object.data.shadow_method = 'RAY_SHADOW'
        # bpy.context.object.data.shadow_ray_samples_x = 15

        # return

    # Light source setup
    # Four suns so no shadows are too deep
    print("Creating sun 1...")
    bpy.ops.object.lamp_add(type='SUN', radius=7500 / kmPerBlend, view_align=False,
                            location=(-1500 / kmPerBlend, 0, 1500 / kmPerBlend))
    bpy.context.object.data.type = 'AREA'
    bpy.context.object.data.energy = energy
    bpy.context.object.data.distance = distance
    bpy.context.object.data.use_specular = False
    bpy.context.object.data.shadow_method = 'RAY_SHADOW'
    bpy.context.object.data.shadow_ray_samples_x = 1

    print("Creating sun 2...")
    bpy.ops.object.lamp_add(type='SUN', radius=7500 / kmPerBlend, view_align=False,
                            location=(1500 / kmPerBlend, 0, 1500 / kmPerBlend))
    bpy.context.object.data.type = 'AREA'
    bpy.context.object.data.energy = energy
    bpy.context.object.data.distance = distance
    bpy.context.object.data.use_specular = False
    bpy.context.object.data.shadow_method = 'RAY_SHADOW'
    bpy.context.object.data.shadow_ray_samples_x = 1
    print("Creating sun 3...")
    bpy.ops.object.lamp_add(type='SUN', radius=7500 / kmPerBlend, view_align=False,
                            location=(0, -1500 / kmPerBlend, 1500 / kmPerBlend))
    bpy.context.object.data.type = 'AREA'
    bpy.context.object.data.energy = energy
    bpy.context.object.data.distance = distance
    bpy.context.object.data.use_specular = False
    bpy.context.object.data.shadow_method = 'RAY_SHADOW'
    bpy.context.object.data.shadow_ray_samples_x = 1
    print("Creating sun 4...")
    bpy.ops.object.lamp_add(type='SUN', radius=7500 / kmPerBlend, view_align=False,
                            location=(0, 1500 / kmPerBlend, 1500 / kmPerBlend))
    bpy.context.object.data.type = 'AREA'
    bpy.context.object.data.energy = energy
    bpy.context.object.data.distance = distance
    bpy.context.object.data.use_specular = False
    bpy.context.object.data.shadow_method = 'RAY_SHADOW'
    bpy.context.object.data.shadow_ray_samples_x = 1


def makeMaterial(name, diffuse, specular, alpha):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = diffuse
    mat.diffuse_shader = 'LAMBERT'
    mat.diffuse_intensity = 1.0
    mat.specular_color = specular
    mat.specular_shader = 'COOKTORR'
    mat.specular_intensity = 0.5
    mat.alpha = alpha
    mat.ambient = 1
    return mat


def makeMaterialCloud(name, color):
    if args.cloudSolid == True:
        return makeMaterialSolid(name, color)
    else:
        return makeMaterialVolume(name, color)


def makeMaterialSolid(name, color):
    # Creates material for surface visualization
    print("Creating solid material...")
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.diffuse_shader = 'LAMBERT'
    mat.diffuse_intensity = 1.0
    mat.specular_color = color
    mat.specular_shader = 'COOKTORR'
    mat.alpha = 1
    mat.ambient = 1
    return mat


def makeMaterialVolume(name, color):
    # Material for volumetric rendering
    mat = bpy.data.materials.new(name)
    mat.volume.transmission_color = color
    mat.volume.reflection_color = color
    # Adjust density scale [0:10] 0 is less "dense" than 10
    # 10 is almost like a solid
    # 0.5 is pretty transparent
    mat.volume.density_scale = 0.25
    mat.volume.light_method = 'SHADOWED'
    # higher step_size will look more natural but take longer
    mat.volume.step_size = 0.001
    mat.type = 'VOLUME'
    # how much does the color come back? [0:10]
    # 0 -- black
    # 10 -- bright that color but will look less volumetric
    mat.volume.emission = 0.25
    return mat


def setMaterial(obj, mat):
    # Applies the material to the object
    print("Applying material...")
    obj.data.materials.append(mat)
    return


def cloudPhaseColors():
    # Creates aerogel material
    volMatn9999 = makeMaterialCloud("n9999", (1, 1, 1))
    setMaterial(bpy.context.object, volMatn9999)

    volMatn9999 = makeMaterialCloud("n2", (0.672443, 0.116971, 0.0742136))
    setMaterial(bpy.context.object, volMatn9999)

    volMatn9999 = makeMaterialCloud("n1", (0.904661, 0.376262, 0.223228))
    setMaterial(bpy.context.object, volMatn9999)

    volMatn9999 = makeMaterialCloud("0", (1, 1, 1))
    setMaterial(bpy.context.object, volMatn9999)

    volMatn9999 = makeMaterialCloud("1", (0.637597, 0.783538, 0.871367))
    setMaterial(bpy.context.object, volMatn9999)

    volMatn9999 = makeMaterialCloud("2", (0.287441, 0.558341, 0.730461))
    setMaterial(bpy.context.object, volMatn9999)

    volMatn9999 = makeMaterialCloud("3", (0.0561285, 0.291771, 0.545725))
    setMaterial(bpy.context.object, volMatn9999)

    volMatn9999 = makeMaterialCloud("4", (0.0152085, 0.132868, 0.412543))
    setMaterial(bpy.context.object, volMatn9999)
    return


def cloudTypeColors():
    cloudType = makeMaterialCloud("Ac", (0, 0.8, 0.8))
    setMaterial(bpy.context.object, cloudType)

    cloudType = makeMaterialCloud("As", (0, 0, 1))
    setMaterial(bpy.context.object, cloudType)

    cloudType = makeMaterialCloud("Cu", (0.8, 0.2, 0))
    setMaterial(bpy.context.object, cloudType)

    cloudType = makeMaterialCloud("Deep", (0.76, 0, 0.8))
    setMaterial(bpy.context.object, cloudType)

    cloudType = makeMaterialCloud("High", (0.2, 0, 0.8))
    setMaterial(bpy.context.object, cloudType)

    cloudType = makeMaterialCloud("Ns", (1, 0, 0))
    setMaterial(bpy.context.object, cloudType)

    # cloudType = makeMaterialCloud("Sc", (0.8, 0.8, 0))
    # setMaterial(bpy.context.object, cloudType)

    cloudType = makeMaterialCloud("St", (0, 1, 0))
    setMaterial(bpy.context.object, cloudType)

    return


def nameColor(scaleVal):
    iColor = np.floor(21 * scaleVal)
    if iColor >= 21:
        iColor = 20
    if iColor <= 0:
        iColor = 0
    colorName = "col{}".format(int(iColor))
    return colorName

def nameGreenishColor(scaleVal):
    iColor = np.floor(21 * scaleVal)
    if iColor >= 21:
        iColor = 20
    if iColor <= 0:
        iColor = 0
    colorName = "colg{}".format(int(iColor))
    return colorName


def greenishColors(numColor):
    botR = 1.00 
    botG = 0.70 
    botB = 0.05
    midR = 0.50 
    midG = 1.00 
    midB = 0.50
    topR = 0.05 
    topG = 0.70 
    topB = 1.00
    for iColor in range(numColor):
        scaleFrac = iColor / (numColor-1.0)
        if scaleFrac < 0.5:
            # low half scales from blue to white
            subFrac = scaleFrac * 2.
            redFrac = botR + subFrac * (midR - botR)
            grnFrac = botG + subFrac * (midG - botG)
            bluFrac = botB + subFrac * (midB - botB)
        else:
            # high half scales from white to red
            subFrac = (scaleFrac - 0.5) * 2.
            redFrac = midR + subFrac * (topR - midR)
            grnFrac = midG + subFrac * (topG - midG)
            bluFrac = midB + subFrac * (topB - midB)
        colorName= "colg{}".format(iColor)
        print("Making color ", iColor, " ", colorName, " ", scaleFrac, " [ ", redFrac, ", ", grnFrac, ", ", bluFrac, " ]")
        mat = makeMaterialCloud(colorName, (redFrac, grnFrac, bluFrac))
        setMaterial(bpy.context.object, mat)


def bwrColors(numColor):
    botR = 0.10 
    botG = 0.10 
    botB = 1.00
    midR = 1.00 
    midG = 1.00 
    midB = 1.00
    topR = 1.00 
    topG = 0.10 
    topB = 0.10
    for iColor in range(numColor):
        scaleFrac = iColor / (numColor-1.0)
        if scaleFrac < 0.5:
            # low half scales from blue to white
            subFrac = scaleFrac * 2.
            redFrac = botR + subFrac * (midR - botR)
            grnFrac = botG + subFrac * (midG - botG)
            bluFrac = botB + subFrac * (midB - botB)
        else:
            # high half scales from white to red
            subFrac = (scaleFrac - 0.5) * 2.
            redFrac = midR + subFrac * (topR - midR)
            grnFrac = midG + subFrac * (topG - midG)
            bluFrac = midB + subFrac * (topB - midB)
        colorName= "col{}".format(iColor)
        print("Making color ", iColor, " ", colorName, " ", scaleFrac, " [ ", redFrac, ", ", grnFrac, ", ", bluFrac, " ]")
        mat = makeMaterialCloud(colorName, (redFrac, grnFrac, bluFrac))
        setMaterial(bpy.context.object, mat)


def defaultColors():
    cloudType = makeMaterialCloud("default", (1, 1, 1))
    setMaterial(bpy.context.object, cloudType)


def grayColor():
    cloudType = makeMaterialCloud("gray", (0.6, 0.6, 0.6))
    setMaterial(bpy.context.object, cloudType)


def sceneSetup(granLong, granLat):
    # This sets up the globe and background
    # TODO: Fix longRot and latRot to position granules properly
    if globe == True:
        # Sets up sphere
        print("Setting up globe...")
        bpy.ops.mesh.primitive_uv_sphere_add(ring_count=32, segments=64)
        bpy.context.object.location[0] = 0
        bpy.context.object.location[1] = 0
        bpy.context.object.location[2] = -501.979
        bpy.context.object.scale[0] = 300
        bpy.context.object.scale[1] = 300
        bpy.context.object.scale[2] = 300
        matProperties = makeMaterialSolid('Globe', (1, 1, 1), (1, 1, 1), (1))
        matProperties.specular_intensity = 0
        setMaterial(bpy.context.object, matProperties)
        bpy.context.object.active_material.use_cast_shadows = False
        bpy.context.object.active_material.diffuse_shader = 'MINNAERT'
        bpy.context.object.active_material.use_transparent_shadows = True
        bpy.context.object.active_material.darkness = 0.3
        bpy.context.object.active_material.use_cast_buffer_shadows = False
        bpy.context.scene.world.horizon_color = (0, 0, 0)
        bpy.context.object.active_material.diffuse_intensity = 0.05

        # Long and lat based on granule 219
        longRot = granLong + 136.0785
        latRot = granLat - 26.847252
        bpy.context.object.rotation_euler[0] = longRot
        bpy.context.object.rotation_euler[1] = latRot

        # Applies Earth texture to sphere
        print("Applying blue marble texture...")
        img = bpy.data.images.load(earthTexturePath)
        tex = bpy.data.textures.new('EarthTexture', type='IMAGE')
        tex.image = img
        atex = matProperties.texture_slots.add()
        atex.texture = tex
        atex.texture_coords = 'ORCO'
        atex.use_map_color_diffuse = True
        atex.mapping = 'SPHERE'
        bpy.context.object.active_material.use_transparent_shadows = True

        # Sets up heights of terrain
        img2 = bpy.data.images.load(earthBumpTexturePath)
        tex2 = bpy.data.textures.new('BumpTexture', type='IMAGE')
        tex2.image = img2
        atex2 = matProperties.texture_slots.add()
        atex2.texture = tex2
        atex2.mapping = 'SPHERE'
        atex2.texture_coords = 'ORCO'
        atex2.use_map_color_diffuse = False
        atex2.use_map_normal = True
        atex2.normal_factor = -0.2
        atex2.bump_method = 'BUMP_BEST_QUALITY'
        bpy.context.object.active_material.use_transparent_shadows = True
    elif args.planeColor.lower() == 'blue':
        # Start with a blue plane representing the Earth
        planeblue = makeMaterial('BlueSemi', (0.1, 0.1, 0.7), (0.5, 0.5, 0), 0.5)
        bpy.ops.mesh.primitive_plane_add(radius=2000. / kmPerBlend, view_align=False, enter_editmode=False,
                                         location=(0, 0, 0), layers=layers_tfff)
        setMaterial(bpy.context.object, planeblue)
        bpy.context.object.active_material.use_shadows = True
        bpy.context.object.active_material.use_transparent_shadows = True
        if args.cloudSolid == False:
            bpy.context.object.active_material.diffuse_intensity = 0.0005
        # bpy.context.object.active_material.use_cast_shadows = True
        # bpy.context.object.active_material.use_cast_buffer_shadows = True
    elif args.planeColor.lower() == 'green':
        # Start with a blue plane representing the Earth
        planegreen = makeMaterial('GreenSemi', (0.1, 0.7, 0.1), (0.5, 0, 0.5), 0.5)
        bpy.ops.mesh.primitive_plane_add(radius=2000. / kmPerBlend, view_align=False, enter_editmode=False,
                                         location=(0, 0, 0), layers=layers_tfff)
        setMaterial(bpy.context.object, planegreen)
        bpy.context.object.active_material.use_shadows = True
        bpy.context.object.active_material.use_transparent_shadows = True
        if args.cloudSolid == False:
            bpy.context.object.active_material.diffuse_intensity = 0.0005
        # bpy.context.object.active_material.use_cast_shadows = True
        # bpy.context.object.active_material.use_cast_buffer_shadows = True
    elif args.planeColor.lower() == 'white':
        # Start with a blue plane representing the Earth
        planewhite = makeMaterial('WhiteSemi', (0.7, 0.7, 0.7), (0.5, 0.5, 0.5), 0.5)
        bpy.ops.mesh.primitive_plane_add(radius=2000. / kmPerBlend, view_align=False, enter_editmode=False,
                                         location=(0, 0, 0), layers=layers_tfff)
        setMaterial(bpy.context.object, planewhite)
        bpy.context.object.active_material.use_shadows = True
        bpy.context.object.active_material.use_transparent_shadows = True
        if args.cloudSolid == False:
            bpy.context.object.active_material.diffuse_intensity = 0.0005
        # bpy.context.object.active_material.use_cast_shadows = True
        # bpy.context.object.active_material.use_cast_buffer_shadows = True

    # Sets up background
    print("Setting background..")
    bpy.context.scene.world.use_sky_blend = True
    bpy.context.scene.world.use_sky_real = True
    bpy.context.scene.world.horizon_color = (0.05, 0.05, 0.05)
    bpy.context.scene.world.ambient_color = (0, 0, 0)
    bpy.context.scene.world.zenith_color = (0.0216636, 0.0216636, 0.0216636)


def stillCameraSetup():
    # Sets up still camera situated at 15, 45, 90, -45, -15 nadir in regard to
    # granule
    if args.stillCamera == True:
        # Top camera
        print("Creating top camera...")
        bpy.ops.object.camera_add(
            view_align=True, enter_editmode=False, location=(0, 0, 45 * 75. / kmPerBlend))
        bpy.context.object.rotation_euler[2] = 1.5708  # pi/2
        bpy.context.object.data.sensor_width = 35
        # camera can be up to 10,000 km away from parts of the scene
        bpy.context.object.data.clip_end = 10000 / kmPerBlend
        bpy.context.object.name = "top.cam"

        # front camera
        print("Creating front camera...")
        bpy.ops.object.camera_add(
            view_align=True, enter_editmode=False, location=(0, -22 * 75. / kmPerBlend, 18 * 75. / kmPerBlend))
        bpy.context.object.data.sensor_width = 79.69
        # camera can be up to 10,000 km away from parts of the scene
        bpy.context.object.data.clip_end = 10000 / kmPerBlend
        bpy.context.object.rotation_euler[0] = 0.767945  # pi/4
        bpy.context.object.name = "front.cam"

        # front 2 camera
        print("Creating front 2 camera...")
        bpy.ops.object.camera_add(
            view_align=True, enter_editmode=False, location=(0, -11 * 75. / kmPerBlend, 18 * 75. / kmPerBlend))
        bpy.context.object.data.sensor_width = 79.69
        # camera can be up to 10,000 km away from parts of the scene
        bpy.context.object.data.clip_end = 10000 / kmPerBlend
        bpy.context.object.rotation_euler[0] = 0.405754
        bpy.context.object.name = "front2.cam"

        # left 2 camera
        print("Creating left 2 camera...")
        bpy.ops.object.camera_add(
            view_align=True, enter_editmode=False, location=(625 / kmPerBlend, 0, 18 * 75. / kmPerBlend))
        bpy.context.object.data.sensor_width = 79.69
        # camera can be up to 10,000 km away from parts of the scene
        bpy.context.object.data.clip_end = 10000 / kmPerBlend
        bpy.context.object.rotation_euler[0] = 0.359538
        bpy.context.object.rotation_euler[1] = 0
        bpy.context.object.rotation_euler[2] = 1.5708

        bpy.context.object.name = "left2.cam"

        # left camera
        print("Creating left camera...")
        bpy.ops.object.camera_add(
            view_align=True, enter_editmode=False, location=(1250 / kmPerBlend, 0, 18 * 75. / kmPerBlend))
        bpy.context.object.data.sensor_width = 79.69
        # camera can be up to 10,000 km away from parts of the scene
        bpy.context.object.data.clip_end = 10000 / kmPerBlend
        bpy.context.object.rotation_euler[0] = 0.767945
        bpy.context.object.rotation_euler[1] = 0
        bpy.context.object.rotation_euler[2] = 1.5708
        bpy.context.object.name = "left.cam"

        # right 2 camera
        print("Creating right 2 camera...")
        bpy.ops.object.camera_add(
            view_align=True, enter_editmode=False, location=(-625 / kmPerBlend, 0, 18 * 75. / kmPerBlend))
        bpy.context.object.data.sensor_width = 79.69
        # camera can be up to 10,000 km away from parts of the scene
        bpy.context.object.data.clip_end = 10000 / kmPerBlend
        bpy.context.object.rotation_euler[0] = 0.359538
        bpy.context.object.rotation_euler[1] = 0
        bpy.context.object.rotation_euler[2] = -1.5708
        bpy.context.object.name = "right2.cam"

        # right camera
        print("Creating right camera...")
        bpy.ops.object.camera_add(
            view_align=True, enter_editmode=False, location=(-1250 / kmPerBlend, 0, 18 * 75. / kmPerBlend))
        bpy.context.object.data.sensor_width = 79.69
        # camera can be up to 10,000 km away from parts of the scene
        bpy.context.object.data.clip_end = 10000 / kmPerBlend
        bpy.context.object.rotation_euler[0] = 0.767945
        bpy.context.object.rotation_euler[1] = 0
        bpy.context.object.rotation_euler[2] = 4.71239
        bpy.context.object.name = "right.cam"

        # back camera
        print("Creating back camera...")
        bpy.ops.object.camera_add(
            view_align=True, enter_editmode=False, location=(0, 22 * 75. / kmPerBlend, 18 * 75. / kmPerBlend))
        bpy.context.object.data.sensor_width = 79.69
        # camera can be up to 10,000 km away from parts of the scene
        bpy.context.object.data.clip_end = 10000 / kmPerBlend
        bpy.context.object.rotation_euler[0] = 10.2573
        bpy.context.object.rotation_euler[1] = -3.14159
        bpy.context.object.rotation_euler[2] = 0
        bpy.context.object.name = "back.cam"

        # back 2 camera
        print("Creating back 2 camera...")
        bpy.ops.object.camera_add(
            view_align=True, enter_editmode=False, location=(0, 11 * 75. / kmPerBlend, 18 * 75. / kmPerBlend))
        bpy.context.object.data.sensor_width = 79.69
        # camera can be up to 10,000 km away from parts of the scene
        bpy.context.object.data.clip_end = 10000 / kmPerBlend
        bpy.context.object.rotation_euler[0] = -2.73668
        bpy.context.object.rotation_euler[1] = 3.14159
        bpy.context.object.rotation_euler[2] = 0
        bpy.context.object.name = "back2.cam"


def clearScene():
    # Clears the current scene
    print("Clearing scene...")
    for obj in bpy.context.scene.objects:
        bpy.context.scene.objects.unlink(obj)
        bpy.data.objects.remove(obj)
    return


def makeClouds(fname_pkl):
    # This is where the magic happens
    global renderLocation
    global earthTexturePath
    global earthBumpTexturePath

    try:
        # Server locations
        pickleLocation = "./"
        # renderLocation = "/home/johnp/visualizer/renders"
        renderLocation = "./"
        earthTexturePath = os.path.expanduser(
            './Additionals/Textures/earth2.jpg')
        earthBumpTexturePath = os.path.expanduser(
            './Additionals/Textures/bump.jpg')
        os.chdir(pickleLocation)

    except:
        # John Pham's local location
        pickleLocation = "/Users/John/GitHub/JPL2016/granules"
        renderLocation = "/Users/John/GitHub/JPL2016/Renders"
        earthTexturePath = os.path.expanduser(
            '/Users/John/Github/JPL2016/Additionals/Textures/earth2.jpg')
        earthBumpTexturePath = os.path.expanduser(
            '/Users/John/Github/JPL2016/Additionals/Textures/bump.jpg')
        os.chdir(pickleLocation)

    os.chdir(pickleLocation)
    print(str(fname_pkl))
    pkl_file = open(str(fname_pkl), 'rb')
    Latitude = pickle.load(pkl_file, fix_imports=True, encoding='bytes')
    Longitude = pickle.load(pkl_file, fix_imports=True, encoding='bytes')
    satzen = pickle.load(pkl_file, fix_imports=True, encoding='bytes')
    satazi = pickle.load(pkl_file, fix_imports=True, encoding='bytes')
    solzen = pickle.load(pkl_file, fix_imports=True, encoding='bytes')
    solazi = pickle.load(pkl_file, fix_imports=True, encoding='bytes')
    TSurfStd = pickle.load(pkl_file, fix_imports=True, encoding='bytes')
    TSurfAir = pickle.load(pkl_file, fix_imports=True, encoding='bytes')
    latAIRS = pickle.load(pkl_file, fix_imports=True, encoding='bytes')
    lonAIRS = pickle.load(pkl_file, fix_imports=True, encoding='bytes')
    CldFrcStd = pickle.load(pkl_file, fix_imports=True, encoding='bytes')
    CldFrcStdErr = pickle.load(pkl_file, fix_imports=True, encoding='bytes')
    nCld = pickle.load(pkl_file, fix_imports=True, encoding='bytes')
    PCldTop = pickle.load(pkl_file, fix_imports=True, encoding='bytes')
    PCldTopErr = pickle.load(pkl_file, fix_imports=True, encoding='bytes')
    TCldTop = pickle.load(pkl_file, fix_imports=True, encoding='bytes')
    TCldTopErr = pickle.load(pkl_file, fix_imports=True, encoding='bytes')
    if args.version != 'v5':
        TSurfStd_QC = pickle.load(pkl_file, fix_imports=True, encoding='bytes')
        TSurfAir_QC = pickle.load(pkl_file, fix_imports=True, encoding='bytes')
        CldFrcStd_QC = pickle.load(
            pkl_file, fix_imports=True, encoding='bytes')
        PCldTop_QC = pickle.load(pkl_file, fix_imports=True, encoding='bytes')
        TCldTop_QC = pickle.load(pkl_file, fix_imports=True, encoding='bytes')
        cloud_phase_3x3 = pickle.load(
            pkl_file, fix_imports=True, encoding='bytes')
        cloud_phase_bits = pickle.load(
            pkl_file, fix_imports=True, encoding='bytes')
        ice_cld_opt_dpth = pickle.load(
            pkl_file, fix_imports=True, encoding='bytes')
        ice_cld_opt_dpth_QC = pickle.load(
            pkl_file, fix_imports=True, encoding='bytes')
        ice_cld_opt_dpth_ave_kern = pickle.load(
            pkl_file, fix_imports=True, encoding='bytes')
        ice_cld_eff_diam = pickle.load(
            pkl_file, fix_imports=True, encoding='bytes')
        ice_cld_eff_diam_QC = pickle.load(
            pkl_file, fix_imports=True, encoding='bytes')
        ice_cld_eff_diam_ave_kern = pickle.load(
            pkl_file, fix_imports=True, encoding='bytes')
        ice_cld_temp_eff = pickle.load(
            pkl_file, fix_imports=True, encoding='bytes')
        ice_cld_temp_eff_QC = pickle.load(
            pkl_file, fix_imports=True, encoding='bytes')
        ice_cld_temp_eff_ave_kern = pickle.load(
            pkl_file, fix_imports=True, encoding='bytes')
        ice_cld_fit_reduced_chisq = pickle.load(
            pkl_file, fix_imports=True, encoding='bytes')
        H2OMMRLevSup = pickle.load(
            pkl_file, fix_imports=True, encoding='bytes')
        H2OMMRLevSup_QC = pickle.load(
            pkl_file, fix_imports=True, encoding='bytes')
    pkl_file.close()

    global granLong
    global granLat
    granLong = lonAIRS[0][0]
    granLat = latAIRS[0][0]
    satHeight_km = 715
    # args.vertMag = 3.0
    nadirRadKm = 15.

    # white = makeMaterial('White', (1,1,1), (0.0,0.0,0.0), 0.25)

    # Creates first instance of cylinder to be copied later
    # bpy.ops.mesh.primitive_cylinder_add(radius=(0.02), depth=(1),
    bpy.ops.mesh.primitive_cylinder_add(radius=(0.5), depth=(1),
                                        view_align=False, enter_editmode=False, location=(0, 0, 0))

    # temporary type for plane test
    # cloudType = makeMaterialCloud("green", (0.1, 1.0, 0.1))
    # setMaterial(bpy.context.object, cloudType)

    # Color scheme is set here
    grayColor()

    # Everytime you want to add a new scheme, you need to create a function that creates
    # the materials, call it here, then assign it in the 3rd for loop
    # Only have to assign in for loop if more than 1 material
    if args.cloudColor.lower() == 'white':
        defaultColors()

    if args.cloudColor.lower() == 'type':
        cloudTypeColors()

    if args.cloudColor.lower() == 'phase':
        cloudPhaseColors()

    if args.cloudColor.lower() == 'ctt':
        bwrColors(21)

    if args.cloudColor.lower() == 'tsurf' or args.planeColor.lower() == 'tsurf':
        bwrColors(21)

    if args.cloudColor.lower() == 'nsat' or args.planeColor.lower() == 'nsat':
        bwrColors(21)

    if args.cloudColor.lower() == 'dtsurf' or args.planeColor.lower() == 'dtsurf':
        bwrColors(21)

    if args.planeColor.lower() == 'h2o750':
        greenishColors(21)

    if args.planeColor.lower() == 'h2o850':
        greenishColors(21)

    if args.planeColor.lower() == 'h2o900':
        greenishColors(21)

    if args.planeColor.lower() == 'h2o930':
        greenishColors(21)

    if args.cloudColor.lower() == 'effdiam':
        bwrColors(21)

    if args.cloudColor.lower() == 'icectt':
        bwrColors(21)

    if args.cloudColor.lower() == 'optdepth':
        bwrColors(21)

    if args.cloudColor.lower() == 'test':
        material = makeMaterialSolid('Red', (1, 0, 0))
        setMaterial(bpy.context.object, material)

    kmPerBlendZ = kmPerBlend / args.vertMag

    if planeMonochrome != True:
        thinBlend = 0.05 / kmPerBlend
        fracMult = 0.9

        if planeH2o == True:
            qplane = H2OMMRLevSup[:,:,ixh2o]
            qplane_qc = H2OMMRLevSup_QC[:,:,ixh2o]
            qmax = 0.0
            qmin = 1.e10
            for isc in range(45):
                for ifp in range(30):
                    if qplane[isc,ifp] > 0.0 and qplane_qc[isc,ifp] < 2:
                        if qplane[isc,ifp] > qmax:
                            qmax = qplane[isc,ifp]
                        if qplane[isc,ifp] < qmin:
                            qmin = qplane[isc,ifp]

        for isc in range(45):
            ysc_km = (isc - 45.0 / 2.0) * 45.0
            ysc = ysc_km / kmPerBlend
            for ifp in range(30):
                scanang_deg = (ifp - 14.5) * 3.3
                scanang_rad = np.radians(scanang_deg)
                xfp_km = satHeight_km * np.tan(scanang_rad)
                xfp = xfp_km / kmPerBlend

                # Copies mesh data for all objects after the first one
                if bpy.context.scene.objects.active.name != "Cylinder":
                    obj = bpy.context.scene.objects.active.copy()
                    obj.data = bpy.context.scene.objects.active.data.copy()
                    bpy.context.scene.objects.link(obj)

                hmag = 1.0 / np.cos(scanang_rad)
                xelong = 1.0 / np.cos(scanang_rad)

                # Removes any materials from the cylinder
                for material in range(len(bpy.context.active_object.data.materials)):
                    try:
                        bpy.context.active_object.data.materials.pop()
                    except RuntimeError:
                        pass

                if args.planeColor.lower() == 'tsurf':
                    # scale surface temperature from 200 to 300 K
                    fval = (TSurfStd[isc,ifp] - 200.) / (300. - 200.)
                    bpy.context.object.data.materials.append(
                                bpy.data.materials[nameColor(fval)])

                if args.planeColor.lower() == 'nsat':
                    # scale near surface air temperature from 200 to 300 K
                    fval = (TSurfAir[isc,ifp] - 200.) / (300. - 200.)
                    bpy.context.object.data.materials.append(
                                bpy.data.materials[nameColor(fval)])

                if args.planeColor.lower() == 'dtsurf':
                    # scale difference between nsat and tsurf from -20 to 20 K
                    dtsurf = (TSurfAir[isc,ifp] - TSurfStd[isc,ifp])
                    fval = (dtsurf - -20.) / (20. - -20.)
                    bpy.context.object.data.materials.append(
                                bpy.data.materials[nameColor(fval)])

                if args.planeColor.lower() == 'h2o750':
                    q = H2OMMRLevSup[isc,ifp,ix750]
                    if q <= 0.0:
                        bpy.context.object.data.materials.append(bpy.data.materials['gray'])
                    else:
                        fval = (q - qmin) / (qmax - qmin)
                        bpy.context.object.data.materials.append(
                                bpy.data.materials[nameGreenishColor(fval)])

                if args.planeColor.lower() == 'h2o850':
                    q = H2OMMRLevSup[isc,ifp,ix850]
                    if q <= 0.0:
                        bpy.context.object.data.materials.append(bpy.data.materials['gray'])
                    else:
                        fval = (q - qmin) / (qmax - qmin)
                        bpy.context.object.data.materials.append(
                                bpy.data.materials[nameGreenishColor(fval)])

                if args.planeColor.lower() == 'h2o900':
                    q = H2OMMRLevSup[isc,ifp,ix900]
                    if q <= 0.0:
                        bpy.context.object.data.materials.append(bpy.data.materials['gray'])
                    else:
                        fval = (q - qmin) / (qmax - qmin)
                        bpy.context.object.data.materials.append(
                                bpy.data.materials[nameGreenishColor(fval)])

                if args.planeColor.lower() == 'h2o930':
                    q = H2OMMRLevSup[isc,ifp,ix930]
                    if q <= 0.0:
                        bpy.context.object.data.materials.append(bpy.data.materials['gray'])
                    else:
                        fval = (q - qmin) / (qmax - qmin)
                        bpy.context.object.data.materials.append(
                                bpy.data.materials[nameGreenishColor(fval)])

                bpy.context.object.scale[0] = 3.0 * horizDecim * fracMult * hmag * xelong * nadirRadKm / kmPerBlend
                bpy.context.object.scale[1] = 3.0 * horizDecim * fracMult *                 nadirRadKm / kmPerBlend
                bpy.context.object.scale[2] = thinBlend

                bpy.context.scene.objects.active.location = ( xfp, ysc, 0.0)
                # print("location", bpy.context.scene.objects.active.location)

                # Copies mesh data for the first one
                if bpy.context.scene.objects.active.name == "Cylinder":
                    obj = bpy.context.scene.objects.active.copy()
                    obj.data = bpy.context.scene.objects.active.data.copy()
                    bpy.context.scene.objects.link(obj)


    if args.cloudColor.lower() != 'none':
        for isc in range(horizDecim // 2, 135, horizDecim):
            print(("Generating scan {} of {}G{}{}").format(
                (isc + 1), args.date, granule, outTag))
            ysc_km = (isc - 135.0 / 2.0) * 15.0
            ysc = ysc_km / kmPerBlend
    
            for ifp in range(horizDecim // 2, 90, horizDecim):
                scanang_deg = (ifp - 44.5) * 1.1
                scanang_rad = np.radians(scanang_deg)
                xfp_km = satHeight_km * np.tan(scanang_rad)
                xfp = xfp_km / kmPerBlend
                numCloud = int(nCld[isc, ifp])

                for icl in range(numCloud):
                    zcldtop_feet = (
                        1 - np.power(PCldTop[isc, ifp, icl] / 1013.25, 0.190284)) * 145366.45
                    zcldtop_km = zcldtop_feet * 0.3048 * 0.001
                    zcldtop = zcldtop_km / kmPerBlendZ
    
                    if icl == 0:
                        frac = CldFrcStd[isc, ifp, icl]
                    else:
                        frac = CldFrcStd[isc, ifp, icl] / \
                            (1.0 - CldFrcStd[isc, ifp, 0])

                    if args.sizeByFrac == True:
                        fracMult = np.sqrt(frac)
                    else:
                        fracMult = 1.0

                    if frac > 0.9999546:
                        opticalDepth = 10
                    else:
                        opticalDepth = np.log(1.0 / (1.0 - frac))

                    cloudThickKm = opticalDepth

                    # Copies mesh data for all objects after the first one
                    if bpy.context.scene.objects.active.name != "Cylinder":
                        obj = bpy.context.scene.objects.active.copy()
                        obj.data = bpy.context.scene.objects.active.data.copy()
                        bpy.context.scene.objects.link(obj)

                    xsmear = 1.25
                    hmag = 1.0 / np.cos(scanang_rad)
                    xelong = 1.0 / np.cos(scanang_rad)

                    # Removes any materials from the cylinder
                    for material in range(len(bpy.context.active_object.data.materials)):
                        try:
                            bpy.context.active_object.data.materials.pop()
                        except RuntimeError:
                            pass

                    # Assigns the material to the cylinder
                    if args.cloudColor.lower() == 'phase':
                        if cloud_phase_3x3[isc, ifp] == -9999:
                            bpy.context.object.data.materials.append(
                                bpy.data.materials["n9999"])
                        if cloud_phase_3x3[isc, ifp] == -2:
                            bpy.context.object.data.materials.append(
                                bpy.data.materials["n2"])
                        if cloud_phase_3x3[isc, ifp] == -1:
                            bpy.context.object.data.materials.append(
                                bpy.data.materials["n1"])
                        if cloud_phase_3x3[isc, ifp] == 0:
                            bpy.context.object.data.materials.append(
                                bpy.data.materials["0"])
                        if cloud_phase_3x3[isc, ifp] == 1:
                            bpy.context.object.data.materials.append(
                                bpy.data.materials["1"])
                        if cloud_phase_3x3[isc, ifp] == 2:
                            bpy.context.object.data.materials.append(
                                bpy.data.materials["2"])
                        if cloud_phase_3x3[isc, ifp] == 3:
                            bpy.context.object.data.materials.append(
                                bpy.data.materials["3"])
                        if cloud_phase_3x3[isc, ifp] == 4:
                            bpy.context.object.data.materials.append(
                                bpy.data.materials["4"])

                    class CloudType(Enum):
                        Ac = 0
                        As = 1
                        Cu = 2
                        Deep = 3
                        High = 4
                        Ns = 7
                        St = 8

                    if (PCldTop[isc, ifp, icl] < 440):
                        if (frac < 0.9):
                            cloudType = CloudType.High
                        else:
                            cloudType = CloudType.Deep

                    elif (PCldTop[isc, ifp, icl] < 680):
                        if (frac < 0.5):
                            cloudType = CloudType.Ac
                        elif (frac < 0.9):
                            cloudType = CloudType.As
                        else:
                            cloudType = CloudType.Ns

                    else:
                        if (frac < 0.9):
                            cloudType = CloudType.Cu
                        else:
                            cloudType = CloudType.St

                    if args.cloudColor.lower() == 'white':
                        bpy.context.object.data.materials.append(
                                    bpy.data.materials['default'])

                    if args.cloudColor.lower() == 'ctt':
                        # scale cloud top temperature from 200 to 300 K
                        fval = (TCldTop[isc, ifp, icl] - 200.) / (300. - 200.)
                        bpy.context.object.data.materials.append(
                                    bpy.data.materials[nameColor(fval)])

                    if args.cloudColor.lower() == 'tsurf':
                        # scale surface temperature from 200 to 300 K
                        fval = (TSurfStd[isc // 3, ifp // 3] - 200.) / (300. - 200.)
                        bpy.context.object.data.materials.append(
                                    bpy.data.materials[nameColor(fval)])

                    if args.cloudColor.lower() == 'nsat':
                        # scale near surface air temperature from 200 to 300 K
                        fval = (TSurfAir[isc // 3, ifp // 3] - 200.) / (300. - 200.)
                        bpy.context.object.data.materials.append(
                                    bpy.data.materials[nameColor(fval)])

                    if args.cloudColor.lower() == 'dtsurf':
                        # scale difference between nsat and tsurf from -20 to 20 K
                        dtsurf = (TSurfAir[isc // 3, ifp // 3] - TSurfStd[isc // 3, ifp // 3])
                        fval = (dtsurf - -20.) / (20. - -20.)
                        bpy.context.object.data.materials.append(
                                    bpy.data.materials[nameColor(fval)])

                    if args.cloudColor.lower() == 'effdiam':
                        # scale log(effective ice cloud particle diameter) from log(20) to log(500)
                        de = ice_cld_eff_diam[isc, ifp]
                        if de > 0.0:
                            fval = (np.log(de) - np.log(20.)) / (np.log(500.) - np.log(20.))
                            bpy.context.object.data.materials.append(
                                    bpy.data.materials[nameColor(fval)])
                        else:
                            bpy.context.object.data.materials.append(
                                    bpy.data.materials["gray"])

                    if args.cloudColor.lower() == 'optdepth':
                        # scale log(effective ice cloud optical depth) from log(0.1) to log(10)
                        tau = ice_cld_opt_dpth[isc, ifp]
                        if tau > 0.0:
                            fval = (np.log(tau) - np.log(0.1)) / (np.log(10.) - np.log(0.1))
                            bpy.context.object.data.materials.append(
                                    bpy.data.materials[nameColor(fval)])
                        else:
                            bpy.context.object.data.materials.append(
                                    bpy.data.materials["gray"])

                    if args.cloudColor.lower() == 'icectt':
                        # scale ice cloud top temperature from 200 to 300 K
                        te = ice_cld_temp_eff[isc, ifp]
                        if te > 0.0:
                            fval = (te - 200) / (300. - 200.)
                            bpy.context.object.data.materials.append(
                                    bpy.data.materials[nameColor(fval)])
                        else:
                            bpy.context.object.data.materials.append(
                                    bpy.data.materials["gray"])

                    if args.cloudColor.lower() == 'type':
                        if cloudType == CloudType.Ac:
                            bpy.context.object.data.materials.append(
                                bpy.data.materials["Ac"])
                        elif cloudType == CloudType.As:
                            bpy.context.object.data.materials.append(
                                bpy.data.materials["As"])
                        elif cloudType == CloudType.Cu:
                            bpy.context.object.data.materials.append(
                                bpy.data.materials["Cu"])
                        elif cloudType == CloudType.Deep:
                            bpy.context.object.data.materials.append(
                                bpy.data.materials["Deep"])
                        elif cloudType == CloudType.High:
                            bpy.context.object.data.materials.append(
                                bpy.data.materials["High"])
                        elif cloudType == CloudType.Ns:
                            bpy.context.object.data.materials.append(
                                bpy.data.materials["Ns"])
                        elif cloudType == CloudType.St:
                            bpy.context.object.data.materials.append(
                                bpy.data.materials["St"])
    
                    if (thickbytype == True):
                        if cloudType == CloudType.Ac:
                            cloudThickKm = 1.2
                        elif cloudType == CloudType.As:
                            cloudThickKm = 2.4
                        elif cloudType == CloudType.Cu:
                            cloudThickKm = 2.6
                        elif cloudType == CloudType.Deep:
                            # cloudThickKm = 10.8
                            cloudThickKm = zcldtop_km - 0.5
                        elif cloudType == CloudType.High:
                            cloudThickKm = 1.2
                        elif cloudType == CloudType.Ns:
                            # cloudThickKm = 3.4
                            cloudThickKm = zcldtop_km - 0.5
                        elif cloudType == CloudType.St:
                            cloudThickKm = 0.5

                    if args.reduceOverlap == True:
                        # to reduce overlap to minimize z fighting artifacts with volumetric clouds
                        # get rid of xsmear and hmag
                        bpy.context.object.scale[
                            0] = horizDecim * fracMult * xelong * nadirRadKm / kmPerBlend
                        bpy.context.object.scale[
                            1] = horizDecim * fracMult * nadirRadKm / kmPerBlend
                    else:
                        bpy.context.object.scale[
                            0] = horizDecim * fracMult * xsmear * hmag * xelong * nadirRadKm / kmPerBlend
                        bpy.context.object.scale[
                            1] = horizDecim * fracMult * hmag * nadirRadKm / kmPerBlend
    
                    if cloudThickKm > zcldtop_km - 0.2:
                        cloudThickKm = zcldtop_km - 0.2
    
                    cloudThickBlend = cloudThickKm / kmPerBlendZ
    
                    if icl == 0:
                        zcldtop0 = zcldtop
                        zcldbot0 = zcldtop - cloudThickBlend
                    else:
                        zcldtop1 = zcldtop
                        zcldbot1 = zcldtop - cloudThickBlend
                        # print(isc+1, ifp+1, "  top cloud ", zcldtop0 * kmPerBlendZ, zcldbot0 * kmPerBlendZ,
                        #                  "     bot cloud ", zcldtop1 * kmPerBlendZ, zcldbot1 * kmPerBlendZ)
                        if zcldtop1 > zcldbot0:
                            print("    {} {} top cloud {} {} bot cloud {} {}".format((isc + 1), (ifp + 1), (zcldtop0 *
                                  kmPerBlendZ), (zcldbot0 * kmPerBlendZ), (zcldtop1 * kmPerBlendZ), (zcldbot1 * kmPerBlendZ)))
                            print("    Overlap of {}".format( (zcldtop1 - zcldbot0) * kmPerBlendZ))
                            # adjust so lower cloud top is 0.2 km below
                            zcldtop = zcldbot0 - 0.2 / kmPerBlendZ
                            cloudThickBlend = zcldtop - zcldbot1
                            cloudThickKm = cloudThickBlend * kmPerBlendZ
                            if cloudThickKm <= 0.5:
                                print("    Adjusted bottom cloud would be too thin: {}".format( cloudThickKm))
                                continue
    
                    bpy.context.object.scale[2] = cloudThickBlend
                    # print("Scale", bpy.context.object.scale)
    
                    bpy.context.scene.objects.active.location = (
                        xfp,
                        ysc,
                        zcldtop - cloudThickBlend / 2.0)
                    # print("location", bpy.context.scene.objects.active.location)
    
                    # Copies mesh data for the first one
                    if bpy.context.scene.objects.active.name == "Cylinder":
                        obj = bpy.context.scene.objects.active.copy()
                        obj.data = bpy.context.scene.objects.active.data.copy()
                        bpy.context.scene.objects.link(obj)


def applyRenderSettings():
    # Lower render settings, decrease in quality for speed gain
    # Quality decrease is minimal with these settings
    print("Applying render settings... | Current runtime:",
          round((time.time() - startTime), 2), "s")
    bpy.context.scene.render.image_settings.file_format = 'JPEG'
    bpy.context.scene.render.resolution_percentage = 100
    bpy.context.scene.render.use_stamp = False
    bpy.context.scene.render.stamp_foreground = (1, 1, 1, 1)
    bpy.context.scene.render.use_stamp_frame = False
    bpy.context.scene.render.use_stamp_scene = False
    bpy.context.scene.render.use_stamp_camera = False
    bpy.context.scene.render.use_stamp_filename = False
    bpy.context.scene.render.use_stamp_time = False
    bpy.context.scene.render.use_stamp_note = True
    bpy.context.scene.render.use_stamp_render_time = False
    bpy.context.scene.render.use_stamp_date = False
    bpy.context.scene.render.resolution_percentage = 100
    bpy.context.scene.render.use_save_buffers = True
    bpy.context.scene.render.tile_x = 16
    bpy.context.scene.render.tile_y = 16
    bpy.context.scene.use_gravity = False
    if args.lowRenderSettings == True:
        bpy.context.scene.render.antialiasing_samples = '5'
        bpy.context.scene.render.resolution_x = 1080
        bpy.context.scene.render.resolution_y = 720
        bpy.context.scene.render.use_shadows = False
        bpy.context.scene.render.use_sss = False
        bpy.context.scene.render.layers["RenderLayer"].use_halo = False
        bpy.context.scene.render.layers["RenderLayer"].use_strand = False
        bpy.context.scene.render.layers["RenderLayer"].use_edge_enhance = False
        bpy.context.scene.render.layers["RenderLayer"].use_sky = False
    bpy.context.scene.render.threads_mode = 'AUTO'
    # bpy.context.scene.render.threads_mode = 'FIXED'
    # bpy.context.scene.render.threads = 512


def renderStills():
    if args.stillCamera == True:
        # print(bpy.context.scene.render.threads)
        print("Rendering cameras... | Current runtime:",
              round((time.time() - startTime), 2), "s")

        print("Rendering front camera...")
        bpy.context.scene.render.stamp_note_text = "front: " + cymdg
        bpy.context.scene.camera = bpy.data.objects['front.cam']
        bpy.context.scene.render.filepath = renderLocation + "/" + cymdg + "/" + \
            cymdg + outTag + "_front"
        bpy.ops.render.render(write_still=True, use_viewport=False)

        print("Rendering top camera...")
        bpy.context.scene.render.stamp_note_text = "Top: " + cymdg
        bpy.context.scene.camera = bpy.data.objects['top.cam']
        bpy.context.scene.render.filepath = renderLocation + "/" + cymdg + "/" + \
            cymdg + outTag + "_top"
        bpy.ops.render.render(write_still=True, use_viewport=False)

        print("Rendering front 2 camera...")
        bpy.context.scene.render.stamp_note_text = "front 2: " + cymdg
        bpy.context.scene.camera = bpy.data.objects['front2.cam']
        bpy.context.scene.render.filepath = renderLocation + "/" + cymdg + "/" + \
            cymdg + outTag + "_front2"
        bpy.ops.render.render(write_still=True, use_viewport=False)

        print("Rendering left camera...")
        bpy.context.scene.render.stamp_note_text = "left: " + cymdg
        bpy.context.scene.camera = bpy.data.objects['left.cam']
        bpy.context.scene.render.filepath = renderLocation + "/" + cymdg + "/" + \
            cymdg + outTag + "_left"
        bpy.ops.render.render(write_still=True, use_viewport=False)

        print("Rendering left 2 camera...")
        bpy.context.scene.render.stamp_note_text = "left 2: " + cymdg
        bpy.context.scene.camera = bpy.data.objects['left2.cam']
        bpy.context.scene.render.filepath = renderLocation + "/" + cymdg + "/" + \
            cymdg + outTag + "_left2"
        bpy.ops.render.render(write_still=True, use_viewport=False)

        print("Rendering right camera...")
        bpy.context.scene.render.stamp_note_text = "right: " + cymdg
        bpy.context.scene.camera = bpy.data.objects['right.cam']
        bpy.context.scene.render.filepath = renderLocation + "/" + cymdg + "/" + \
            cymdg + outTag + "_right"
        bpy.ops.render.render(write_still=True, use_viewport=False)

        print("Rendering right 2 camera...")
        bpy.context.scene.render.stamp_note_text = "right 2: " + cymdg
        bpy.context.scene.camera = bpy.data.objects['right2.cam']
        bpy.context.scene.render.filepath = renderLocation + "/" + cymdg + "/" + \
            cymdg + outTag + "_right2"
        bpy.ops.render.render(write_still=True, use_viewport=False)

        print("Rendering back camera...")
        bpy.context.scene.render.stamp_note_text = "back: " + cymdg
        bpy.context.scene.camera = bpy.data.objects['back.cam']
        bpy.context.scene.render.filepath = renderLocation + "/" + cymdg + "/" + \
            cymdg + outTag + "_back"
        bpy.ops.render.render(write_still=True, use_viewport=False)

        print("Rendering back 2 camera...")
        bpy.context.scene.render.stamp_note_text = "back 2: " + cymdg
        bpy.context.scene.camera = bpy.data.objects['back2.cam']
        bpy.context.scene.render.filepath = renderLocation + "/" + cymdg + "/" + \
            cymdg + outTag + "_back2"
        bpy.ops.render.render(write_still=True, use_viewport=False)


def cleanKeyframes(startFrame, endFrame):
    try:
        bpy.context.scene.frame_set(startFrame)
        bpy.context.object.keyframe_delete(data_path="location")
        bpy.context.scene.frame_set(endFrame)
        bpy.context.object.keyframe_delete(data_path="location")
    except RuntimeError:
        pass

def renderCircularAnimation():
    if args.circularAnimation == True:
        # Used to track center of granule
        trackPathScale = 25 * 75. / kmPerBlend
        circularAnimationheight = 20 * 75. / kmPerBlend
   # 5 seconds at 24 frames per second = 120
        bpy.context.scene.frame_end = endFrame
        bpy.ops.object.empty_add(type='PLAIN_AXES', radius=1, view_align=False, location=(
            0, 0, 0), layers=layers_tfff)
        bpy.context.object.name = "centerTrack"
        bpy.ops.curve.primitive_bezier_circle_add(view_align=False, enter_editmode=False, location=(
            0, 0, circularAnimationheight), layers=layers_tfff)
        bpy.context.object.name = "trackPath"
        bpy.context.object.scale[0] = trackPathScale
        bpy.context.object.scale[1] = trackPathScale
        print("Creating circular motion camera...")
        bpy.ops.object.camera_add(
            view_align=True, enter_editmode=False, location=(0, -22 * 75. / kmPerBlend, circularAnimationheight))
        bpy.context.object.data.sensor_width = 79.69
        # camera can be up to 10,000 km away from parts of the scene
        bpy.context.object.data.clip_end = 10000 / kmPerBlend
        # bpy.context.object.rotation_euler[0] = 0.767945
        bpy.context.object.name = "circularMotion.cam"
        bpy.ops.object.constraint_add(type='CLAMP_TO')
        bpy.context.object.constraints[
            "Clamp To"].target = bpy.data.objects["trackPath"]
        bpy.ops.object.constraint_add(type='TRACK_TO')
        bpy.context.object.constraints[
            "Track To"].target = bpy.data.objects["centerTrack"]
        bpy.context.object.constraints[
            "Track To"].track_axis = 'TRACK_NEGATIVE_Z'
        bpy.context.object.constraints["Track To"].up_axis = 'UP_Y'
        bpy.context.scene.frame_set(0)
        bpy.context.scene.camera = bpy.data.objects['circularMotion.cam']
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.data.objects['circularMotion.cam'].select = True
        bpy.context.object.location[0] = -1 * trackPathScale
        # bpy.ops.anim.keyframe_insert_menu(type='Location')
        bpy.context.object.keyframe_insert(data_path="location")
        # bpy.ops.anim.keyframe_insert_menu(type='Rotation')
        bpy.context.scene.frame_set(endFrame)
        bpy.context.object.location[0] = trackPathScale
        # bpy.ops.anim.keyframe_insert_menu(type='Location')
        bpy.context.object.keyframe_insert(data_path="location")
        # bpy.ops.anim.keyframe_insert_menu(type='Rotation')
        bpy.context.scene.render.filepath = renderLocation + \
            "/animation/" + cymdg + "/" + "circ_" + cymdg + outTag + "-"
        bpy.context.scene.render.image_settings.file_format = 'AVI_JPEG'
        bpy.ops.render.render(animation=True)

def renderSpiralAnimation():
    if args.spiralAnimation == True:
        # Used to track center of granule
        trackPathScale = 25 * 75. / kmPerBlend
        circularAnimationStartHeight = 20 * 75. / kmPerBlend
        circularAnimationEndHeight = 10 * 75. / kmPerBlend
        bpy.context.scene.frame_end = endFrame
        cleanKeyframes(0, endFrame)

        bpy.ops.curve.primitive_bezier_circle_add(view_align=False, enter_editmode=False, location=(
            0, 0, circularAnimationStartHeight), layers=layers_tfff)
        bpy.context.object.name = "trackPathMove"
        bpy.context.object.scale[0] = trackPathScale
        bpy.context.object.scale[1] = trackPathScale
        # Sets to frame 0
        bpy.context.scene.frame_set(0)
        # Selects camera to be animation camera
        bpy.ops.object.mode_set(mode='OBJECT')
        # Selects track
        bpy.data.objects['trackPathMove'].select = True
        # Sets initial location
        bpy.context.object.location[2] = circularAnimationStartHeight
        # Adds a keyframe
        bpy.context.object.keyframe_insert(data_path="location")
        # Sets current frame to 120 (5 seconds)
        bpy.context.scene.frame_set(endFrame)
        bpy.context.object.location[2] = circularAnimationEndHeight
        bpy.context.object.keyframe_insert(data_path="location")

        bpy.ops.object.empty_add(type='PLAIN_AXES', radius=1, view_align=False, location=(
            0, 0, 0), layers=layers_tfff)
        bpy.context.object.name = "centerTrack2"

        print("Creating spiral motion camera...")
        bpy.ops.object.camera_add(
            view_align=True, enter_editmode=False, location=(0, -22 * 75. / kmPerBlend, circularAnimationStartHeight))
        bpy.context.object.data.sensor_width = 79.69
        # camera can be up to 10,000 km away from parts of the scene
        bpy.context.object.data.clip_end = 10000 / kmPerBlend
        # bpy.context.object.rotation_euler[0] = 0.767945
        bpy.context.object.name = "spiralMotion.cam"
        bpy.context.scene.camera = bpy.data.objects['spiralMotion.cam']
        bpy.ops.object.constraint_add(type='CLAMP_TO')
        bpy.context.object.constraints[
            "Clamp To"].target = bpy.data.objects["trackPathMove"]
        bpy.ops.object.constraint_add(type='TRACK_TO')
        bpy.context.object.constraints[
            "Track To"].target = bpy.data.objects["centerTrack2"]
        bpy.context.object.constraints[
            "Track To"].track_axis = 'TRACK_NEGATIVE_Z'
        bpy.context.object.constraints["Track To"].up_axis = 'UP_Y'
        bpy.context.scene.frame_set(0)
        bpy.context.scene.camera = bpy.data.objects['spiralMotion.cam']
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.data.objects['spiralMotion.cam'].select = True
        bpy.context.object.location[0] = -1 * trackPathScale
        # bpy.ops.anim.keyframe_insert_menu(type='Location')
        bpy.context.object.keyframe_insert(data_path="location")
        # bpy.ops.anim.keyframe_insert_menu(type='Rotation')
        bpy.context.scene.frame_set(endFrame)
        bpy.context.object.location[0] = trackPathScale
        # bpy.ops.anim.keyframe_insert_menu(type='Location')
        bpy.context.object.keyframe_insert(data_path="location")
        # bpy.ops.anim.keyframe_insert_menu(type='Rotation')
        bpy.context.scene.render.filepath = renderLocation + \
            "/animation/" + cymdg + "/" + "spiral_" + cymdg + outTag + "-"
        bpy.context.scene.render.image_settings.file_format = 'AVI_JPEG'
        bpy.ops.render.render(animation=True)

def renderTopDownAnimation():
    if args.topDownAnimation == True:
        startLocation = -125.44
        endLocation = -250
        cleanKeyframes(0, endFrame)

        bpy.ops.object.empty_add(type='PLAIN_AXES', radius=1, view_align=False, location=(0, 0, 0), layers=layers_tfff)
        bpy.context.object.name = "topDownCenter"

        bpy.ops.curve.primitive_bezier_circle_add(radius=250, view_align=False, enter_editmode=False, location=(0, 0, 0), layers=layers_tfff)
        bpy.context.object.name = "topDownTrack"
        # Rotates the circle 90 degrees
        bpy.context.object.rotation_euler[1] = 1.5708

        bpy.ops.object.camera_add(view_align=True, enter_editmode=False, location=(0, 0, 0), rotation=(0.555694, 0.00889516, 0.709793), layers=layers_tfff)
        bpy.context.object.data.sensor_width = 72
        bpy.context.object.data.clip_end = 1000
        bpy.context.object.name = "topDown.cam"
        bpy.context.scene.camera = bpy.data.objects['topDown.cam']

        bpy.ops.object.constraint_add(type='CLAMP_TO')
        bpy.context.object.constraints["Clamp To"].target = bpy.data.objects["topDownTrack"]
        bpy.context.object.constraints["Clamp To"].main_axis = 'CLAMPTO_Y'

        bpy.ops.object.constraint_add(type='TRACK_TO')
        bpy.context.object.constraints["Track To"].target = bpy.data.objects["topDownCenter"]
        bpy.context.object.constraints["Track To"].track_axis = 'TRACK_NEGATIVE_Z'
        bpy.context.object.constraints["Track To"].up_axis = 'UP_Y'

        bpy.context.scene.frame_end = endFrame
        bpy.context.scene.frame_set(0)
        bpy.context.object.location[1] = startLocation
        bpy.context.object.keyframe_insert(data_path="location")
        bpy.context.scene.frame_set(endFrame)
        bpy.context.object.location[1] = endLocation
        bpy.context.object.keyframe_insert(data_path="location")
        bpy.context.scene.render.filepath = renderLocation + \
                "/animation/" + cymdg + "/" + "topdown_" + cymdg + outTag + "-"
        bpy.context.scene.render.image_settings.file_format = 'AVI_JPEG'
        bpy.ops.render.render(animation=True)


startTime = time.time()
clearScene()
applyRenderSettings()
makeClouds(fname_pkl)
sceneSetup(granLong, granLat)
createLight()
stillCameraSetup()

# Save as .blend to export to Unity:
if args.blendOut == True:
  filepath = renderLocation + "/" + cymdg + "/" + cymdg + outTag + ".blend"
  print("Saving .blend file for Unity: ", filepath)
  bpy.ops.wm.save_as_mainfile(filepath=filepath)

# # Export in a format Google Earth supports:
# filepath = renderLocation + "/" + cymdg + "/" + cymdg + outTag + ".dae"
# print("Saving .dae file for Google Earth: ", filepath)
# bpy.ops.wm.collada_export(filepath=filepath)

renderStills()
renderTopDownAnimation()
renderSpiralAnimation()
renderCircularAnimation()

print("\nTotal Time(s)", cymdg, round((time.time() - startTime), 2))

# EMM to do:
# new file names
# more args
# smaller FOVs to control z fighting
# add back in option to have smaller radius for lower ECF.  Also option to
# randomize subpixel location.
