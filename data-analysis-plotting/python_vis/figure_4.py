import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import yaml

# Utility functions
def calculate_proportions(df):
    if df.empty:
        print("Warning: DataFrame is empty in calculate_proportions")
        return pd.DataFrame(columns=['Category', 'Proportion'])
    
    # Calculate proportions
    proportions = df['alc_use_status'].value_counts(normalize=True).reindex([0, 1, 2, 3], fill_value=0).reset_index()
    proportions.columns = ['Category', 'Proportion']
    
    # Map category labels
    proportions['Category'] = proportions['Category'].map({0: 'Non-Drinking', 1: 'Cat I', 2: 'Cat II', 3: 'Cat III'})
    
    return proportions

def summary_after_release(days, agent_dt):
    filter_condition = (agent_dt['last_release_tick'] > 0) & (agent_dt['tick'] <= agent_dt['last_release_tick'] + days)
    agents_within_period = agent_dt[filter_condition]
    proportions = calculate_proportions(agents_within_period)
    print(f"Summary for {days} days after release:\n", proportions)
    return proportions

# Load data
with open("/Users/ryaneng/Desktop/browncs/sph_lab/cadre/python/myparams/model_params.yaml", 'r') as stream:
    input_params = yaml.safe_load(stream)

# Load the agent log environment CSV file
agent_log_env = pd.read_csv("/Users/ryaneng/Desktop/browncs/sph_lab/cadre/python/output_20240702_204607/agent_log.csv")

agent_dt = agent_log_env

# Verify the data is loaded correctly
print("Data head:\n", agent_dt.head())
print("Columns:\n", agent_dt.columns)

# Ticks of interest
selected_ticks = list(range(1, agent_dt["tick"].max() + 1, 10))
last_tick = agent_dt["tick"].max()
print("Selected ticks:", selected_ticks)
print("Last tick:", last_tick)

# Population subsets by release status
desired_tick = last_tick
all_agents = agent_dt[agent_dt["tick"] == desired_tick]
never_released_agents = agent_dt[(agent_dt["tick"] == desired_tick) & (agent_dt["n_releases"] == 0)]
released_agents = agent_dt[(agent_dt["tick"] == desired_tick) & (agent_dt["n_releases"] >= 1)]

# Verify subsets
print("All agents count:", len(all_agents))
print("Never released agents count:", len(never_released_agents))
print("Released agents count:", len(released_agents))

# Alcohol use state distributions in above subsets
all_agents_summary = calculate_proportions(all_agents)
never_released_agents_summary = calculate_proportions(never_released_agents)
released_agents_summary = calculate_proportions(released_agents)

print("All agents summary:\n", all_agents_summary)
print("Never released agents summary:\n", never_released_agents_summary)
print("Released agents summary:\n", released_agents_summary)

# Summarize alcohol use rates in general population
alcohol_summaries = []
for tick in selected_ticks:
    agents_at_tick = agent_dt[agent_dt["tick"] == tick]
    proportions = calculate_proportions(agents_at_tick)
    alcohol_summaries.append({"proportions": proportions, "tick": tick})

alcohol_proportions_df = pd.concat([pd.DataFrame(s["proportions"]).assign(Tick=s["tick"]) for s in alcohol_summaries])
print("Alcohol proportions DataFrame:\n", alcohol_proportions_df)

# Compare alcohol use rates in short time frame after release (1 year)
fixed_time_after_release = 365
within_fixed_time_after_release_agents = agent_dt[(agent_dt["last_release_tick"] > 0) & (agent_dt["tick"] <= agent_dt["last_release_tick"] + fixed_time_after_release)]
within_fixed_time_after_release_summary = calculate_proportions(within_fixed_time_after_release_agents)

print("Summary for Agents Within One Year After Release")
print(within_fixed_time_after_release_summary)

# Sensitivity Analysis on parameter of time after release
time_periods = [1, 7, 14, 30, 90, 180, 365]
summaries = [summary_after_release(days, agent_dt) for days in time_periods]

    
# Plot heavy drinking/AUD after release
labels = ["1D", "1W", "2W", "1M", "3M", "6M", "1Y"]
heavy_use_or_AUD_proportions = [s.loc[s["Category"] == "Cat III", "Proportion"].sum() if "Cat III" in s["Category"].values else 0 for s in summaries]

heavy_use_AUD_df = pd.DataFrame({
    "Time": time_periods,
    "Labels": labels,
    "Proportion": heavy_use_or_AUD_proportions
})

print("Heavy use AUD DataFrame:\n", heavy_use_AUD_df)

plt.figure(figsize=(10, 6))
sns.lineplot(data=heavy_use_AUD_df, x="Time", y="Proportion", marker="o")
plt.xticks(ticks=time_periods, labels=labels)
plt.yticks(np.arange(0, 0.6, 0.1))
plt.xlabel("Time After Release")
plt.ylabel("Proportion of Agents with AUD")
plt.title("Heavy Drinking/AUD After Release")
plt.ylim(0, 0.5)
plt.grid(True)
plt.show()

# Compare Heavy Use/AUD in general population with the post-release group
general_heavy_AUD_df = alcohol_proportions_df[alcohol_proportions_df["Category"] == "Cat III"]
combined_proportions = general_heavy_AUD_df.groupby("Tick").sum().reset_index()
last_combined_rate = combined_proportions.tail(10)["Proportion"].mean()
last_combined_rate_df = pd.DataFrame({
    "Time": range(max(heavy_use_AUD_df["Time"]), 366),
    "Proportion": last_combined_rate
})

general_population = pd.DataFrame({
    "Time": heavy_use_AUD_df["Time"],
    "Proportion": last_combined_rate_df["Proportion"]
})

plt.figure(figsize=(10, 6))
sns.lineplot(data=heavy_use_AUD_df, x="Time", y="Proportion", label="Previously Incarcerated", linewidth=1.5)
sns.lineplot(data=general_population, x="Time", y="Proportion", label="Overall", linewidth=1.5)
plt.ylim(0, 1)
plt.xlabel("Time After Release")
plt.ylabel("Proportion")
plt.title("Heavy Drinking/AUD Comparison")
plt.xticks(ticks=heavy_use_AUD_df["Time"], labels=heavy_use_AUD_df["Labels"], rotation=90)
plt.legend()
plt.grid(True)
plt.show()

def calculate_proportions_smoking(df):
    proportions = df['smoking_status'].value_counts(normalize=True).reset_index()
    proportions.columns = ['Category', 'Proportion']
    proportions['Category'] = pd.Categorical(proportions['Category'], categories=["Never", "Former", "Current"])
    proportions = proportions.sort_values('Category').reset_index(drop=True)
    return proportions

def summary_after_release_smoking(days, agent_dt, ):
    filter_condition = (agent_dt['last_release_tick'] > 0) & (agent_dt['tick'] - agent_dt['last_release_tick'] <= days)
    agents_within_period = agent_dt[filter_condition]
    proportions = calculate_proportions_smoking(agents_within_period)
    agent_count = len(agents_within_period)
    return {'proportions': proportions, 'agent_count': agent_count}

# Smoking ratio at last tick of current smoking to all persons
last_tick_data = agent_dt[agent_dt["tick"] == last_tick]
smoking_ratio = last_tick_data.groupby(last_tick_data['n_releases'] >= 1).apply(lambda df: pd.Series({
    'n_current_smokers': (df['smoking_status'] == 'Current').sum(),
    'n_total_persons': df['smoking_status'].isin(['Current', 'Former', 'Never']).sum()
})).reset_index()

# Compute the ratio of current smokers to total smokers in each group
smoking_ratio['ratio'] = smoking_ratio['n_current_smokers'] / smoking_ratio['n_total_persons']
print(smoking_ratio)

# Compute change in current smoking over time since release
time_periods = [1, 7, 14, 30, 90, 180, 365]
labels = ["1D", "1W", "2W", "1M", "3M", "6M", "1Y"]
summaries_smoking = [summary_after_release_smoking(days, agent_dt) for days in time_periods]

# Visualization (smoking in released persons)
current_smoker_proportions = [
    s['proportions'].loc[s['proportions']['Category'] == 'Current', 'Proportion'].sum() 
    if 'Category' in s['proportions'].columns and 'Current' in s['proportions']['Category'].values 
    else 0
    for s in summaries_smoking
]

current_smoker_df = pd.DataFrame({
    "Time": time_periods,
    "Labels": labels,
    "Proportion": current_smoker_proportions
})

plt.figure(figsize=(10, 6))
sns.lineplot(data=current_smoker_df, x="Time", y="Proportion", marker="o")
plt.xticks(ticks=time_periods, labels=labels)
plt.yticks(np.arange(0, 1.1, 0.2))
plt.xlabel("Time After Release")
plt.ylabel("Proportion of Current Smoking")
plt.title("Current Smoking After Release")
plt.ylim(0, 1)
plt.grid(True)
plt.show()

# Visualization (smoking in general population)
smokers_by_tick = agent_dt[agent_dt["tick"].isin(selected_ticks)].groupby("tick").apply(
    lambda df: pd.Series({
        'current_smokers': (df['smoking_status'] == 'Current').mean(),
        'former_smokers': (df['smoking_status'] == 'Former').mean(),
        'never_smokers': (df['smoking_status'] == 'Never').mean()
    })
).reset_index()

# Mean from the last 10 rows
mean_current_smoker = smokers_by_tick.tail(10)["current_smokers"].mean()

# General population data frame
general_population = pd.DataFrame({
    "Time": current_smoker_df["Time"],
    "Proportion": [mean_current_smoker] * len(current_smoker_df["Time"])
})

plt.figure(figsize=(10, 6))
sns.lineplot(data=current_smoker_df, x="Time", y="Proportion", label="Previously Incarcerated", linewidth=1.5)
sns.lineplot(data=general_population, x="Time", y="Proportion", label="Overall", linewidth=1.5)
plt.ylim(0, 1)
plt.xlabel("Time After Release")
plt.ylabel("Proportion")
plt.title("Current Smoking Comparison")
plt.xticks(ticks=current_smoker_df["Time"], labels=current_smoker_df["Labels"], rotation=90)
plt.legend()
plt.grid(True)
plt.show()


