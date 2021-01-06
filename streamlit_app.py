import streamlit as st
import json
from dateutil.parser import parse

@st.cache
def load_data():
    data = []
    with open("data.json", "r") as f:
        for line in f.readlines():
            data.append([ parse(x) for x in json.loads(line)["timestamps"]])

    jan1 = parse("2021-1-1 00:00:00.000000 UTC")
    for e in data:
        e.append(jan1)

    # compute number of idle days for each app
    for e in data:
        e.sort()

    return data

def get_idle_times():
    data = load_data()

    idle_times = []
    for series in data:
        idle_times.append([])
        for i, _ in enumerate(series):
            if i < len(series)-1:
                elapsed_hours = round((series[i+1] - series[i]).total_seconds() / 3600, 0)
                if elapsed_hours > 0:
                    idle_times[len(idle_times)-1].append(elapsed_hours)
    return idle_times

idle_times = get_idle_times()

period = st.slider("Period (days)", 0, 30, 7) * 24

# Total idle time
#for e in [sum(x) for x in idle_times]:
#    st.write(e/24)

spin_downs = []
for e in idle_times:
    spin_downs.append([])
    last = spin_downs[len(spin_downs)-1]
    for x in e:
        if x >= period:
            last.append(x - period)

hours_saved = 0
for e in spin_downs:
    if len(e) > 0:
        #st.write(e)
        hours_saved += sum(e)

st.write("Total number of hours saved", hours_saved)
st.write("(WIP) Total number of hours saved %", 100 * hours_saved / (1500 * 30 * 24))


