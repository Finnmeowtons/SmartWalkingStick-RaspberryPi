import requests
from ..hardware.sim_module import get_operator, get_cell_info
from ..utils.config import OPENCELLID_API_KEY

def lookup_opencellid(mcc, mnc, lac, cellid):
    url = f"https://opencellid.org/cell/get?key={OPENCELLID_API_KEY}&mcc={mcc}&mnc={mnc}&lac={lac}&cellid={cellid}&format=json"
    r = requests.get(url)
    if r.status_code == 200:
        return r.json()
    return None

if __name__ == "__main__":
    print("Getting operator...")
    operator = get_operator()
    print("Operator:", operator)

    print("Getting cell info...")
    lac, cellid = get_cell_info()
    print("LAC:", lac, "CellID:", cellid)

    # Example for PH Globe: MCC=515, MNC=2
    mcc, mnc = 515, 2  

    if lac and cellid:
        print("Looking up location via OpenCellID...")
        location = lookup_opencellid(mcc, mnc, lac, cellid)
        print("Result:", location)
    else:
        print("Could not get cell tower info.")
