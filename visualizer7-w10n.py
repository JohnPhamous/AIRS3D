try:
    # Use when running within Blender
    import bpy, requests, json, datetime
    blender = True
except ImportError:
    # Use when outside of Blender
    import requests, json, datetime
    blender = False

debug = False    # Used to test functions without having to manually input

def convert_days(year, month, day):
    # Converts the user's date into the day of the year (1-365/366)
    user_date = datetime.datetime(year, month, day)
    day_of_year = (user_date - datetime.datetime(user_date.year, 1, 1)).days + 1
    return day_of_year

def search_path(url):
    # Finds preliminary URL path
    print("Finding file...")
    raw_data = requests.get(url)
    data_json = json.loads(raw_data.text)
    data_useful = data_json["leaves"][0]
    data_useful = data_useful["name"]
    return data_useful

def download_data(name, url):
    # Downloads json from Pomegranate server then returns a list of values
    print("Downloading {}...".format(name))
    raw_data = requests.get(url)
    data_json = json.loads(raw_data.text)
    data_useful = data_json["data"]
    data_flat = [item for sublist in data_useful for item in sublist]
    return data_flat

# Dictionary with AIRS data fields
granule_properties = {"Longitude", "Latitude","TSurfStd", "TSurfAir",
                      "CldFrcStd", "nCld", "PCldTop", "TCldTop",
                      "cloud_phase_3x3", "ice_cld_opt_dpth", "ice_cld_eff_diam",
                      "ice_cld_temp_eff", "H2OMMRLevSup"}

# Populates keys with None value
granule_properties = {key: None for key in granule_properties}

if debug == True:
    month = 10
    day = 25
    year = 2010
    granule = 42
else:
    print("Enter granule info below")
    month = input("Month(1-12): ")
    month = "{0}".format(str(month).zfill(2))
    day = input("Day(1-31): ")
    day = "{0}".format(str(day).zfill(2))
    year = str(input("Year(XXXX): "))
    granule = input("Granule: ")
    granule = "{0}".format(str(granule).zfill(3))

print("Searching for granule {} on {}-{}-{}".format(granule, month, day, year))
day_of_year = convert_days(int(year), int(month), int(day))

# Finds URL for supporting data of granule
url_prefix = ("http://airsl2.gesdisc.eosdis.nasa.gov/pomegranate/Aqua_AIRS_Level2/AIRX2SUP.006/{}/{}/".format(year,
                                                                                                 day_of_year))
search_pattern = "AIRS.{}.{}.{}.001.L2.RetSup.v6.0.7.0.**.hdf/?output=json".format(year,
                                                                     month,
                                                                     day)
filename = search_path((url_prefix + search_pattern))
# HTML view
# print((url_prefix + filename + "/?output=HTML"))

if blender == True:
    # Goes through dictionary and downloads corresponding data
    for key in granule_properties:
        granule_properties[key] = download_data(key, (url_prefix + filename + "/" + key + "[]?output=json"))
        print(len(granule_properties[key]))

    # Parameters
    outTag = ""
    horizDecim = 1
    vertMag = 1
    animLen = 10.0
    globe = False
    stillCamera = False
    lowRenderSettings = False
    circularAnimation = False
    spiralAnimation = False
    topDownAnimation = False
    thickbytype = False
    cloudColor = 'type'
    planeColor = 'blue'
    sizeByFrac = None
    reduceOverlap = True
    cloudSolid = False
    blendOut = False

    kmPerBlend = 10.0
    satHeight_km = 715.0
    nadirRadKm = 15.0
    kmPerBlendZ = kmPerBlend /  vertMag
    fracMult = 0.9
    thinBlend = 0.05 / kmPerBlend

    # Creates first instance of cylinder to be copied later
    bpy.ops.mesh.primitive_cylinder_add(radius=(0.5), depth=(1),
                                    view_align=False, enter_editmode=False, location=(0, 0, 0))
    # isc = latitude
    for granule_properties["Latitude"][i] in range(45):
        ysc_km = (granule_properties["Latitude"][i] - 45.0 / 2.0) * 45.0
        ysc = ysc_km / kmPerBlend
        # ifp = longitude
        for granule_properties["Longitude"][i] in range(30):
            scanang_deg = (granule_properties["Longitude"][i] - 14.5) * 3.3
            scanang_rad = np.radians(scanang_deg)
            xfp_km = satHeight_km * np.tan(scanang_rad)
            xfp = xfp_km / kmPerBlend

            # Copies mesh data of cylinder
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
            bpy.context.object.scale[0] = (3.0 * horizDecim * fracMult * hmag * xelong * nadirRadKm / kmPerBlend)
            bpy.context.object.scale[1] = 3.0 * horizDecim * fracMult * nadirRadKm / kmPerBlend
            bpy.context.object.scale[2] = thinBlend

            bpy.context.scene.objects.active.location = (granule_properties["Longitude"][i], granule_properties["Latitude"][i], 0.0)

            if bpy.context.scene.objects.active.name == "Cylinder":
                obj = bpy.context.scene.objects.active.copy()
                obj.data = bpy.context.scene.objects.active.data.copy()
                bpy.context.scene.objects.link(obj)
