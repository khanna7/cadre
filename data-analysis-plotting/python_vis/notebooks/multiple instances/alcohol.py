import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Define the data directory
data_dir = "emews/swift/turbine-output"
all_instances_data = []

# Read the data from CSV files
for i in range(1, 31):
    instance_dir = os.path.join(data_dir, f"instance_{i}")
    csv_files = [os.path.join(instance_dir, f) for f in os.listdir(instance_dir) if f.endswith('.csv')]
    instance_data = [pd.read_csv(f) for f in csv_files]
    all_instances_data.append(pd.concat(instance_data))

# Extract input parameters (assuming input_params is available in the environment)
input_params = {
    "ALC_USE_PROPS": {
        "0": 0.2,
        "1": 0.3,
        "2": 0.25,
        "3": 0.25
    }
}
alc_use_props = input_params["ALC_USE_PROPS"]
alc_use_targets = [alc_use_props["0"], alc_use_props["1"], alc_use_props["2"], alc_use_props["3"]]

# Compute metrics
all_alc_use_proportions_by_tick = []

for i, agent_df in enumerate(all_instances_data):
    last_tick = agent_df["tick"].max()
    selected_ticks = list(range(1, last_tick, 10)) + [last_tick]
    
    alc_use_proportions = agent_df[agent_df["tick"].isin(selected_ticks)].groupby("tick").apply(
        lambda x: pd.Series({
            "Non_Drinking": (x["alc_use_status"] == 0).mean(),
            "Category_I": (x["alc_use_status"] == 1).mean(),
            "Category_II": (x["alc_use_status"] == 2).mean(),
            "Category_III": (x["alc_use_status"] == 3).mean()
        })
    ).reset_index()
    
    alc_use_proportions_long = alc_use_proportions.melt(id_vars="tick", var_name="alc_use_status", value_name="proportion")
    alc_use_proportions_long["instance"] = i
    all_alc_use_proportions_by_tick.append(alc_use_proportions_long)

combined_alc_use_proportions = pd.concat(all_alc_use_proportions_by_tick)

aggregated_alc_use_proportions = combined_alc_use_proportions.groupby(["tick", "alc_use_status"]).agg(
    mean_proportion=("proportion", "mean"),
    min_proportion=("proportion", "min"),
    max_proportion=("proportion", "max")
).reset_index()

# Plot
alc_colors = {
    "Non_Drinking": "#377eb8", 
    "Category_I": "#ff7f00", 
    "Category_II": "#4daf4a", 
    "Category_III": "#e41a1c"
}

half_time = aggregated_alc_use_proportions["tick"].max() / 365 / 2

target_alc_use_df = pd.DataFrame({
    "alc_use_status": list(alc_colors.keys()),
    "target_pct": alc_use_targets,
    "color": list(alc_colors.values())
})

plt.figure(figsize=(10, 8))
sns.lineplot(data=aggregated_alc_use_proportions, x="tick", y="mean_proportion", hue="alc_use_status", palette=alc_colors)
plt.fill_between(data=aggregated_alc_use_proportions, x="tick", y1="min_proportion", y2="max_proportion", alpha=0.3)

for _, row in target_alc_use_df.iterrows():
    plt.text(half_time, row["target_pct"], f"Target: {row['target_pct'] * 100:.2f}%", color="black", va="bottom")

plt.title("")
plt.xlabel("Time (Years)")
plt.ylabel("Proportion")
plt.legend(title="")
plt.grid(True)
plt.savefig("agent-log-analysis/multiple-runs/plots/alc_use_time_labels.png")
plt.show()