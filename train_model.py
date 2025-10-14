import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib

# 1️⃣ Load your dataset with explicit column names
column_names = [
    "Date","GameID","Drive","qtr","down","time","TimeUnder","TimeSecs","PlayTimeDiff","SideofField","yrdln","yrdline100","ydstogo","ydsnet","GoalToGo","FirstDown","posteam","DefensiveTeam","desc","PlayAttempted","Yards.Gained","sp","Touchdown","ExPointResult","TwoPointConv","DefTwoPoint","Safety","Onsidekick","PuntResult","PlayType","Passer","Passer_ID","PassAttempt","PassOutcome","PassLength","AirYards","YardsAfterCatch","QBHit","PassLocation","InterceptionThrown","Interceptor","Rusher","Rusher_ID","RushAttempt","RunLocation","RunGap","Receiver","Receiver_ID","Reception","ReturnResult","Returner","BlockingPlayer","Tackler1","Tackler2","FieldGoalResult","FieldGoalDistance","Fumble","RecFumbTeam","RecFumbPlayer","Sack","Challenge.Replay","ChalReplayResult","Accepted.Penalty","PenalizedTeam","PenaltyType","PenalizedPlayer","Penalty.Yards","PosTeamScore","DefTeamScore","ScoreDiff","AbsScoreDiff","HomeTeam","AwayTeam","Timeout_Indicator","Timeout_Team","posteam_timeouts_pre","HomeTimeouts_Remaining_Pre","AwayTimeouts_Remaining_Pre","HomeTimeouts_Remaining_Post","AwayTimeouts_Remaining_Post","No_Score_Prob","Opp_Field_Goal_Prob","Opp_Safety_Prob","Opp_Touchdown_Prob","Field_Goal_Prob","Safety_Prob","Touchdown_Prob","ExPoint_Prob","TwoPoint_Prob","ExpPts","EPA","airEPA","yacEPA","Home_WP_pre","Away_WP_pre","Home_WP_post","Away_WP_post","Win_Prob","WPA","airWPA","yacWPA","Season"
]
df = pd.read_csv("NFL Play by Play 2009-2016 (v3).csv", names=column_names, header=0, low_memory=False)
print("Columns in DataFrame:", df.columns.tolist())

# 2️⃣ Filter for relevant plays (column name is 'PlayType')
df = df[df['PlayType'].isin(['pass', 'run','Run','Pass'])]


 # Feature engineering
df["red_zone"] = df["yrdline100"] <= 20
df["short_yard"] = df["ydstogo"] <= 2
df["third_long"] = (df["down"] == 3) & (df["ydstogo"] >= 8)
df["half"] = df["qtr"].apply(lambda x: 1 if x in [1, 2] else 0)

# 3️⃣ Select useful features (update names to match provided columns)
features = [
    "down",
    "ydstogo",
    "qtr",
    "yrdline100",
    "red_zone",
    "short_yard",
    "third_long",
    "half"
]
    # Add more features as needed from your list


# Clean missing values
df = df.dropna(subset=features + ['PlayType'])
df[features] = df[features].fillna(0)

# 4️⃣ Split into X and y
X = df[features]
y = df['PlayType']

# 5️⃣ Split data into train/test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 6️⃣ Train a RandomForest model
clf = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    random_state=42,
    n_jobs=-1
)
clf.fit(X_train, y_train)

# 7️⃣ Evaluate accuracy
print("✅ Model trained successfully")
print("Accuracy:", clf.score(X_test, y_test))

# 8️⃣ Save model compatible with your local environment
joblib.dump(clf, "playcall_model.pkl")
print("💾 Model saved as playcall_model.pkl")