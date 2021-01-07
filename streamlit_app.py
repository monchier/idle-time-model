import streamlit as st
import json
from dateutil.parser import parse
import pandas as pd
import numpy as np
import altair as alt


def load_data_df():
    jan1 = parse("2021-1-1 00:00:00.000000 UTC")
    df = pd.read_json('data.json', lines=True) #, nrows=10)
    df.timestamps = df.timestamps.apply(pd.to_datetime)
    df.timestamp = df.timestamps.apply(lambda x: x + np.array([pd.to_datetime(jan1)]))
    df.timestamps = df.timestamps.apply(np.sort)
    return df

@st.cache
def load_data():
    data = []
    with open("data.json", "r") as f:
        for line in f.readlines():
            data.append([ parse(x) for x in json.loads(line)["timestamps"]])

    dec1 = parse("2020-12-1 00:00:00.000000 UTC")
    jan1 = parse("2021-1-1 00:00:00.000000 UTC")
    for e in data:
        e.append(dec1)
        e.append(jan1)

    # compute number of idle days for each app
    for e in data:
        e.sort()

    return data

@st.cache
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

#st.write(load_data_df())
#import sys
#sys.exit()
idle_times = get_idle_times()

days = 31

st.title("Spin Down Simulation")
st.markdown("This app simulates a spin down algoritm where apps are shut down after a period since the last access. The data used by this app"
"are derived from our segment database `identify` table. We aggregate this table to obtain the time series of the app reloads for each app."
"This information is used to compute when an app can be shut down after a configurable `period` of inactivity. The time remaining after"
"the shutdown is considered 'saved' and accounts towards the dollars saved")
st.markdown("We assume that all apps are active for the whole month. This is conservative, since some apps may not be active at all during the nonth and some apps may be started later in a month. We assume apps do not get deleted (this can be a source of inaccuracy). We also assume"
"that the baseline system has all nodes to accomodate all apps. This can be also a source of inaccuracy since apps actually trickle in the "
"system during the month.")


st.write("Enter a period: that is the number of days after which we turn off an app.")
period = st.slider("Period (days)", 0, days, 7) * 24

# Total idle time
#for e in [sum(x) for x in idle_times]:
#    st.write(e/24)

def get_hours_saved(period):
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

    return hours_saved

hours_saved = get_hours_saved(period)

total_apps = len(idle_times)

app_per_core = 1

machines = total_apps / app_per_core / 32

st.write("Number of apps:", len(idle_times))
st.write("Number of 32-core nodes in the baseline system:", machines)

total_number_of_cores = 32 * machines

total_core_hours = total_number_of_cores * days * 24

core_hours_saved = hours_saved / app_per_core

cost_of_a_core_per_hour = 740 / 32 / days / 24

st.write("Cost of a core for a month [$]: ", cost_of_a_core_per_hour * days * 24)

monthly_cost = cost_of_a_core_per_hour * total_core_hours

st.write("Baseline cost of the cluser [$]:", monthly_cost)

st.write("Total number of core-hours saved:", hours_saved)
st.write("Total dollars saved:", hours_saved * cost_of_a_core_per_hour)

core_hours_per_month = days * 24 / app_per_core

savings = hours_saved * cost_of_a_core_per_hour

st.write("Cost reduction [%]",  100 * savings / monthly_cost)

