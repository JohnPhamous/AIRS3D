try:
    # Use when running within Blender
    import bpy, requests, json, datetime
except ImportError:
    # Use when outside of Blender
    import requests, json, datetime

longitude_url = (
    'http://airsl2.gesdisc.eosdis.nasa.gov/pomegranate/Aqua_AIRS_Level2/AIRX2RET.006/2016/008/AIRS.2016.01.08.001.L2.RetStd.v6.0.31.0.G16008144115.hdf/Longitude[]?output=json')

# Dictionary with AIRS data fields
granule_properties = {"longitude", "latitude", "satzen", "satazi", "TSurfStd",
                    "TSurfAir", "latAIRS", "lonAIRS", "CldFrcStd",
                    "CldFrcStdErr", "nCld", "PCldTop", "PCldTopErr",
                    "TCldTopErr", "TSurfStd_QC", "TSurfAir_AC", "CldFrcStd_QC",
                    "PCldTop_QC", "TCldTop_QC", "cloud_phase_3x3",
                    "cloud_phase_bits", "ice_cld_opt_dpth:",
                    "ice_cld_opt_dpth_QC", "ice_cld_opt_dpth_ave_kern",
                    "ice_cld_eff_diam", "ice_cld_eff_diam_QC",
                    "ice_cld_eff_diam_ave_kern", "ice_cld_temp_eff",
                    "ice_cld_temp_eff_QC", "ice_cld_temp_eff_ave_kern",
                    "ice_cld_fit_reduced_chsq", "H20MMRLevSup",
                    "H20MMRLevSup_QC"}

# Populates keys with None value
granule_properties = {key: None for key in granule_properties}

debug = True    # Used to test functions without having to manually input

if debug == True:
    month = 10
    day = 25
    year = 2006
    granule = 42
else:
    print("Enter granule info below")
    month = input("Month(1-12): ")
    day = input("Day(1-31): ")
    year = str(input("Year(XXXX): "))
    granule = input("Granule: ")
    granule = "{0}".format(str(granule).zfill(3))

# TODO fills are not working
day = int("{0}".format(str(day).zfill(2)))   # Makes sure the day is in XX
month = int("{0}".format(str(month).zfill(2)))   # Makes sure the month is in XX
print("Searching for granule {} on {}-{}-{}".format(granule, month, day, year))

def convert_days(year, month, day):
    # Converts the user's date into the day of the year (1-365/366)
    user_date = datetime.datetime(year, month, day)
    day_of_year = (user_date - datetime.datetime(user_date.year, 1, 1)).days + 1
    return day_of_year

day_of_year = convert_days(year, month, day)

# TODO find url based on user input, then user will select which file to use
url = ("http://airsl2.gesdisc.eosdis.nasa.gov/pomegranate/Aqua_AIRS_Level2/AIRX2RET.006/{}/{}/AIRS.{}.{}.{}.001.L2.RetStd.v6.0.31.0.G16008144115.hdf/?output=html".format(year,
                                                                                                                                                                    day_of_year,
                                                                                                                                                                    year,
                                                                                                                                                                    month,
                                                                                                                                                                    day))
print(url)

def download_data(name, url):
    # Downloads json from Pomegranate server then returns a list of values
    print("Downloading {}...".format(name))
    raw_data = requests.get(url)
    data_json = json.loads(raw_data.text)
    data_useful = data_json["data"]
    data_flat = [item for sublist in data_useful for item in sublist]
    return data_flat

def main():
    for key in granule_properties:
        # Downloads data for all keys in dictionary
        granule_properties[key] = download_data(key, longitude_url)

    # granule_properties["longitude"] = download_data("longitude", longitude_url)
    print(granule_properties["longitude"][0])

    for i in range(len(granule_properties["longitude"])):
        # TODO: Make stuff here
        pass
