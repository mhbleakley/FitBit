import fitbit
import gather_keys_oauth2 as Oauth2
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import style
from matplotlib.ticker import MaxNLocator
import datetime
import os
import sys
import time

# personal key to access fitbit account
personal_info = open("info.txt", "r")
CLIENT_ID = personal_info.readline().strip()
CLIENT_SECRET = personal_info.readline().strip()
personal_info.close()

# useful dates
two_days_ago = str((datetime.datetime.now() - datetime.timedelta(days=2)).strftime("%Y-%m-%d"))
yesterday = str((datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d"))
today = str(datetime.datetime.now().strftime("%Y-%m-%d"))

# generate list of dates to grab raw_data from
days = 627
end_date = datetime.datetime.now() - datetime.timedelta(days=1)  # ends yesterday
datetime_list = [end_date - datetime.timedelta(days=x) for x in range(days)]
date_list = []
for date_time in datetime_list:
    date_list.append(date_time.strftime("%Y-%m-%d"))


# grab raw_data from list of dates
def collect_data(dates):
    server = Oauth2.OAuth2Server(CLIENT_ID, CLIENT_SECRET)
    server.browser_authorize()
    ACCESS_TOKEN = str(server.fitbit.client.session.token['access_token'])
    REFRESH_TOKEN = str(server.fitbit.client.session.token['refresh_token'])
    auth2_client = fitbit.Fitbit(CLIENT_ID, CLIENT_SECRET, oauth2=True, access_token=ACCESS_TOKEN, refresh_token=REFRESH_TOKEN)

    activities = ["heart", "steps", "calories", "distance", "floors", "elevation"]

    for i, date in enumerate(dates):
        for activity in activities:
            if not os.path.exists("raw_data/{}_{}.csv".format(date, activity)):
                stats = auth2_client.intraday_time_series('activities/{}'.format(activity), base_date=date, detail_level='1min')
                time_list = []
                val_list = []
                for i in stats['activities-{}-intraday'.format(activity)]['dataset']:
                    val_list.append(i['value'])
                    time_list.append(i['time'])
                df = pd.DataFrame({'{}'.format(activity): val_list, 'time': time_list})
                df.to_csv("raw_data/{}_{}.csv".format(date, activity), columns=['time', '{}'.format(activity)], header=True, index=False)
                print(str(date), str(activity))
                time.sleep(24)
                


collect_data(date_list)


# make steps etc. cumulative
def process_data(dates, keep_every=1):
    cumulative = ["steps", "calories", "distance", "floors", "elevation", "heart"]
    for activity in cumulative:
        for date in dates:
            # if not os.path.exists("processed_data/{}_{}.csv".format(activity, date)):
            df = pd.read_csv("raw_data/{}_{}.csv".format(activity, date))
            df["total"] = df["{}".format(activity)].cumsum()
            df = df.iloc[::keep_every, :]
            df.to_csv("processed_data/{}_{}.csv".format(activity, date), columns=['time', '{}'.format(activity), "total"],
                      header=True, index=False)


# process_data(date_list, 10)


def visualize_data(date):
    style.use("dark_background")
    fig, axs = plt.subplots(2, 2)
    activities = ["heart", "steps", "distance", "calories"]
    values = ["heart", "total", "total", "total"]
    titles = ["Heart Rate (BPM)", "Steps", "Distance (Miles)", "Calories"]
    styles = ["r-", "b-", "g-", "y-"]
    k = 0
    for i in range(2):
        for j in range(2):
            df = pd.read_csv("processed_data/{}_{}.csv".format(activities[k], date))
            axs[i, j].plot(df["time"].tolist(), df["{}".format(values[k])].tolist(), styles[k], linewidth=.75)
            axs[i, j].set_title(titles[k])
            axs[i, j].xaxis.set_major_locator(MaxNLocator(3))
            axs[i, j].yaxis.set_major_locator(MaxNLocator(4))
            axs[i, j].grid(linewidth=.5)
            k += 1
    plt.tight_layout()
    plt.savefig("results.png")


# visualize_data("2022-05-10")

sys.exit()