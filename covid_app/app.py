from cProfile import label
import urllib.request
import json
import matplotlib.pyplot as plt
import pandas as pd
from flask import Flask, request, Response, jsonify
from io import BytesIO


app = Flask(__name__)


@app.route('/')
def home():
    with open("index.html") as f:
        html = f.read()
    return html


@app.route('/dashboard.svg')
def dash():
    json_files = []
    regions = list(range(1, 11))
    for region in regions:
        url = f"https://idph.illinois.gov/DPHPublicInformation/api/COVIDExport/GetResurgenceDataHospitalAvailability?regionID={region}&daysIncluded=20"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            page = response.read()
        my_json = page.decode('utf8').replace("'", '"')
        data = json.loads(my_json)
        json_files.append(data)

    fig, ax = plt.subplots()
    for jsonf in json_files:
        dates = []
        icu_per = []
        for inst in jsonf:
            region_name = inst["regionDescription"]
            dates.append(inst["reportDate"][:10])
            icu_per.append(inst["AverageICUAvailPct"])
        plt.plot(dates, icu_per, label=region_name)
    plt.xlabel('Dates', fontsize=12)
    plt.ylabel('ICU Availability Percent', fontsize=12)
    plt.xticks(rotation=90)
    plt.title('ICU Availability vs Time', fontsize=20)
    plt.legend(bbox_to_anchor=(1.05, 0.6))
    fake_file = BytesIO()
    ax.get_figure().savefig(fake_file, format="svg", bbox_inches="tight")
    plt.close(fig)
    return Response(fake_file.getvalue(),
                    headers={"Content-Type": "image/svg+xml"})


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, threaded=False)
