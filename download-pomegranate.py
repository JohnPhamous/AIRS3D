import requests, json

url = 'http://airsl2.gesdisc.eosdis.nasa.gov/pomegranate/Aqua_AIRS_Level2/AIRX2RET.006/2016/008/AIRS.2016.01.08.001.L2.RetStd.v6.0.31.0.G16008144115.hdf/Longitude[]?output=json'

def download_data(url):
    # Downloads the data from Pomegranate server then returns a list of values
    raw_data = requests.get(url)
    data_json = json.loads(raw_data.text)
    data_useful = data_json["data"]
    data_flat = [item for sublist in data_useful for item in sublist]
    return data_flat
