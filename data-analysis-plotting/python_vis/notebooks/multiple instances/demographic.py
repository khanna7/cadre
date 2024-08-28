import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load data from CSV files
data_dir = "emews/swift/turbine-output"
all_instances_data = []

for i in range(1, 31):
    instance_dir = os.path.join(data_dir, f"instance_{i}")
    csv_files = [os.path.join(instance_dir, f) for f in os.listdir(instance_dir) if f.endswith('.csv')]
    instance_data = [pd.read_csv(f) for f in csv_files]
    all_instances_data.append(pd.concat(instance_data))

# Input parameters for target values
input_params = {
    "RACE_DISTRIBUTION": {
        "White": 0.6,
        "Black": 0.2,
        "Hispanic": 0.15,
        "Asian": 0.05
    },
    "FEMALE_PROP": 0.5
}

# Race distribution
target_values = pd.DataFrame({
    "race": list(input_params["RACE_DISTRIBUTION"].keys()),
    "target_pct": list(input_params["RACE_DISTRIBUTION"].values())
})

all_race_proportions_by_tick = []

for i, instance_data in enumerate(all_instances_data):
    last_tick = instance_data['tick'].max()
    selected_ticks = list(range(1, last_tick, 10)) + [last_tick]
    
    race_proportions = instance_data[instance_data['tick'].isin(selected_ticks)].groupby('tick').apply(
        lambda x: pd.Series({
            "White": (x['race'] == "White").mean(),
            "Black": (x['race'] == "Black").mean(),
            "Hispanic": (x['race'] == "Hispanic").mean(),
            "Asian": (x['race'] == "Asian").mean()
        })
    ).reset_index()
    
    race_proportions_long = race_proportions.melt(id_vars="tick", var_name="race", value_name="proportion")
    race_proportions_long['instance'] = i + 1
    all_race_proportions_by_tick.append(race_proportions_long)

combined_race_proportions = pd.concat(all_race_proportions_by_tick)

aggregated_race_proportions = combined_race_proportions.groupby(['tick', 'race']).agg(
    mean_proportion=('proportion', 'mean'),
    sd_proportion=('proportion', 'std')
).reset_index()

race_proportions_stats = combined_race_proportions.groupby(['tick', 'race']).agg(
    min_proportion=('proportion', 'min'),
    max_proportion=('proportion', 'max')
).reset_index()

# Plot race distribution
target_values['color'] = ["#377eb8", "#ff7f00", "#4daf4a", "#e41a1c"]
half_time = combined_race_proportions['tick'].max() / 365 / 2

plt.figure(figsize=(10, 8))
for race, color in zip(target_values['race'], target_values['color']):
    race_data = race_proportions_stats[race_proportions_stats['race'] == race]
    plt.fill_between(race_data['tick'] / 365, race_data['min_proportion'], race_data['max_proportion'], color=color, alpha=0.3)
    mean_data = aggregated_race_proportions[aggregated_race_proportions['race'] == race]
    plt.plot(mean_data['tick'] / 365, mean_data['mean_proportion'], color=color, label=race)

for _, row in target_values.iterrows():
    plt.text(half_time, row['target_pct'] + 0.03, f"Target: {row['target_pct']:.3f}", color=row['color'], size=12)

plt.xlabel("Time (Years)")
plt.ylabel("Proportion")
plt.legend(title="Race")
plt.ylim(0, 1)
plt.title("Race Distribution Over Time")
plt.savefig(os.path.join("agent-log-analysis", "multiple-runs", "plots", "race_distribution_plot.png"))
plt.show()

# Sex distribution
all_gender_proportions_by_tick = []

for i, instance_data in enumerate(all_instances_data):
    last_tick = instance_data['tick'].max()
    selected_ticks = list(range(1, last_tick, 10)) + [last_tick]
    
    gender_proportions = instance_data[instance_data['tick'].isin(selected_ticks)].groupby('tick').apply(
        lambda x: pd.Series({
            "male": (x['female'] == 0).mean(),
            "female": (x['female'] == 1).mean()
        })
    ).reset_index()
    
    gender_proportions_long = gender_proportions.melt(id_vars="tick", var_name="gender", value_name="proportion")
    gender_proportions_long['instance'] = i + 1
    all_gender_proportions_by_tick.append(gender_proportions_long)

combined_gender_proportions = pd.concat(all_gender_proportions_by_tick)

aggregated_gender_proportions = combined_gender_proportions.groupby(['tick', 'gender']).agg(
    mean_proportion=('proportion', 'mean'),
    sd_proportion=('proportion', 'std')
).reset_index()

gender_proportions_stats = combined_gender_proportions.groupby(['tick', 'gender']).agg(
    min_proportion=('proportion', 'min'),
    max_proportion=('proportion', 'max')
).reset_index()

# Plot sex distribution
colors = {"male": "#1b9e77", "female": "#d95f02"}
half_time = aggregated_gender_proportions['tick'].max() / 365 / 2

female_target_pct = input_params["FEMALE_PROP"]
male_target_pct = 1 - female_target_pct

target_sex_distribution_df = pd.DataFrame({
    "gender": ["male", "female"],
    "target_pct": [male_target_pct, female_target_pct],
    "color": ["#1b9e77", "#d95f02"]
})
target_sex_distribution_df['label_y'] = [male_target_pct - 0.05, female_target_pct + 0.03]

plt.figure(figsize=(10, 8))
for gender, color in colors.items():
    gender_data = gender_proportions_stats[gender_proportions_stats['gender'] == gender]
    plt.fill_between(gender_data['tick'] / 365, gender_data['min_proportion'], gender_data['max_proportion'], color=color, alpha=0.3)
    mean_data = aggregated_gender_proportions[aggregated_gender_proportions['gender'] == gender]
    plt.plot(mean_data['tick'] / 365, mean_data['mean_proportion'], color=color, label=gender)

for _, row in target_sex_distribution_df.iterrows():
    plt.text(half_time, row['label_y'], f"Target: {row['target_pct']:.3f}", color=row['color'], size=12)

plt.xlabel("Time (Years)")
plt.ylabel("Proportion")
plt.legend(title="Gender")
plt.ylim(0, 1)
plt.title("Sex Distribution Over Time")
plt.savefig(os.path.join("agent-log-analysis", "multiple-runs", "plots", "sex_distribution_plot.png"))
plt.show()