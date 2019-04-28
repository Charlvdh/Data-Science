# Import required mudules

import pandas as pd
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
from itertools import combinations

# Read in the csv file as a DataFrame

sap = pd.read_csv("sphist.csv", index_col=False)

# Convert the Date column to datetime

sap["Date"] = pd.to_datetime(sap["Date"])

# The dataframe is currently sored by date in descending order
# Let's change it to ascending order
# Also reset index so starts at 0

sap = sap.sort_values(by="Date", ascending=True)

sap = sap.reset_index(drop=True)

# Calculate 5 days moving average, 30 day moving average
# 5 day standard deviation and 30 day standerd deviation and and them as columns

# ma_5
def add_moving_average_col(period):
    control = []
    col = []
    for row in sap.iterrows():
        row = row[1]
        if len(control) < period:
            control.append(row["Close"])
            col.append(0)
        else:
            col.append(np.mean(control))
            del control[0]
            control.append(row["Close"])
    sap[f"{period}_day_ma"] = col

add_moving_average_col(5)

# ma_30
add_moving_average_col(30)

# std_5
def add_moving_std_col(period):
    control = []
    col = []
    for row in sap.iterrows():
        row = row[1]
        if len(control) < period:
            control.append(row["Close"])
            col.append(0)
        else:
            col.append(np.std(control))
            del control[0]
            control.append(row["Close"])
    sap[f"{period}_day_std"] = col

add_moving_std_col(5)

# std_30
add_moving_std_col(30)

# Also add the prior day close and volume as columns

# pr_day_close
def prior_day(attribute):
    col = sap[attribute].shift(1)
    sap[f"pr_day_{attribute}".lower()] = col

prior_day("Close")

# pr-day_volume
prior_day("Volume")


# Remove the first 30 rows as these rows do not have values for
# all indicators
sap.drop(range(0,31), inplace=True)

# Drop na rows
sap.dropna(axis=0, inplace=True)

# Split df into train and test sets with train being all datapoints
# before 2013-01-01
train = sap.loc[sap["Date"] < datetime(year=2013, month=1, day=1)]
test = sap.loc[sap["Date"] >= datetime(year=2013, month=1, day=1)]

# Let's build, train and test a model with absolute mean error
# as the error metric

# For features we can only use metrics we would know at the end
# of the previous day
all_features = ['5_day_ma', '30_day_ma', '5_day_std', '30_day_std',
'pr_day_close', 'pr_day_volume']

target = "Close"

def train_and_test():

# In order to find the best combination of columns to use
# generate a model for every combination and calculate and
# compare error metrics

    maes = {}
    combinations_list = []

    for i in range(2, len(all_features)):

        new_combinations = combinations(all_features, i)

        for combination in new_combinations:

            combinations_as_a_list = list(combination)
            # In order to store the list as a dictionary value it is
            # necessary to join the items into a string and then
            # split them out to a list later
            key = '-'.join(combinations_as_a_list)
            combinations_list.append(key)

    for features in combinations_list:

        features = features.split('-')

        model = LinearRegression()
        model.fit(train[features], train[target])
        predictions = model.predict(test[features])

        mae = mean_absolute_error(test[target], predictions)

        features = '-'.join(features)

        maes[features] = mae

    # Turn the dict into a dataframe

    df = pd.DataFrame.from_dict(maes, orient="index")
    df.columns = ["Value"]

    # As per inspection of a scatter plot ot the mae values,
    # there are a few high outliers. Remove all maes over 100
    # to eliminate these

    df = df.loc[df["Value"] < 100]

    # There seem to be some in the range 
    # some in the range 25 - 30
    # some in the range 15 - 20
    # some in the range 1

    plt.scatter(range(1, len(df)+1), df["Value"])
    plt.show()

    # best_mae = min(maes.values())
    # best_features = min(maes, key=maes.get)
    #
    # worst_mae = max(maes.values())
    # worst_features = max(maes, key=maes.get)
    #
    # print(f"Best Features: {best_features}\nBest Mean Absolute Error: {best_mae}\nWorst Features: {worst_features}\nWorst Mean Absolute Error {worst_mae}\nAverage MSE: {sum(maes.values())/len(maes.values())}")

    # Plot the maes
    # It appears that there are a few very high outlying mae values
    # Cap mae at 100 to eliminate them


train_and_test()
