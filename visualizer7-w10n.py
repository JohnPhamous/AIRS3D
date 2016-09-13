try:
    import bpy, requests, json
except ImportError:
    import requests, json

longitude_url = (
    'http://airsl2.gesdisc.eosdis.nasa.gov/pomegranate/Aqua_AIRS_Level2/AIRX2RET.006/2016/008/AIRS.2016.01.08.001.L2.RetStd.v6.0.31.0.G16008144115.hdf/Longitude[]?output=json')

def download_data(name, url):
    # Downloads json from Pomegranate server then returns a list of values
    print("Downloading {}...".format(name))
    raw_data = requests.get(url)
    data_json = json.loads(raw_data.text)
    data_useful = data_json["data"]
    data_flat = [item for sublist in data_useful for item in sublist]
    return data_flat

longitude = download_data("longitude", longitude_url)
print(longitude[0])
