import streamlit as st
import pandas as pd
import plotly.express as px

# Load data
df_main = pd.read_csv("data/aqi_master_clean.csv")
df_main['Date'] = pd.to_datetime(df_main['Date'], format='mixed', dayfirst=True)

diwali_summary = pd.read_csv("results/diwali_summary.csv")
mannwhitney = pd.read_csv("results/diwali_mannwhitney_results.csv")

st.title("Diwali Air Quality Impact")
st.markdown("How does Diwali affect air quality across cities and years?")

st.divider()

# City selector
cities = sorted(diwali_summary["City"].unique())
selected_city = st.selectbox("Select a City", cities)

city_summary = diwali_summary[
    diwali_summary["City"] == selected_city
].copy()

city_mw = mannwhitney[
    mannwhitney["City"] == selected_city
].iloc[0]

st.divider()

# Mann-Whitney verdict card
st.subheader("Statistical Verdict")

p_value = city_mw["P_Value"]
festival_mean = round(city_mw["Festival_Mean"], 1)
octnov_mean = round(city_mw["OctNov_Mean"], 1)
diff = round(festival_mean - octnov_mean, 1)

if p_value < 0.05:
    st.error(f"""
    **Diwali significantly elevates air pollution in {selected_city}**
    Festival-period AQI ({festival_mean}) was on average **{diff} points higher**
    than the seasonal Oct–Nov baseline ({octnov_mean}).
    *(Mann-Whitney p = {round(p_value, 3)} - statistically significant)*
    """)
elif p_value < 0.10:
    st.warning(f"""
    **Diwali shows a borderline effect on air pollution in {selected_city}**
    Festival-period AQI ({festival_mean}) was **{diff} points higher**
    than the seasonal baseline ({octnov_mean}) on average.
    *(Mann-Whitney p = {round(p_value, 3)} - borderline significance)*
    """)
else:
    st.info(f"""
    **No statistically significant Diwali effect detected in {selected_city}**
    Festival-period AQI ({festival_mean}) was close to the seasonal
    Oct–Nov baseline ({octnov_mean}).
    *(Mann-Whitney p = {round(p_value, 3)})*
    """)

st.divider()

# Pre / Festival / Post grouped bar chart
st.subheader("Pre, During and Post Diwali AQI by Year")
st.caption(
    "Compares average AQI in the 7 days before Diwali, "
    "the 5 festival days, and the 7 days after. "
    "2020 marked separately due to COVID-19 disruptions."
)

# Melt to long format for grouped bar
city_melt = city_summary.melt(
    id_vars=["City", "Year"],
    value_vars=["Pre_Mean", "Festival_Mean", "Post_Mean"],
    var_name="Period",
    value_name="AQI"
)

period_labels = {
    "Pre_Mean": "Pre Diwali",
    "Festival_Mean": "Festival",
    "Post_Mean": "Post Diwali"
}
city_melt["Period"] = city_melt["Period"].map(period_labels)

fig_grouped = px.bar(
    city_melt,
    x="Year",
    y="AQI",
    color="Period",
    barmode="group",
    title=f"{selected_city} - AQI Around Diwali by Year",
    color_discrete_map={
        "Pre Diwali": "#4C9BE8",
        "Festival": "#E8524C",
        "Post Diwali": "#F0A500"
    },
    category_orders={"Period": ["Pre Diwali", "Festival", "Post Diwali"]}
)

# Annotate 2020
fig_grouped.add_annotation(
    x=2020,
    y=city_summary[city_summary["Year"] == 2020]["Festival_Mean"].values[0] + 15,
    text="⚠️ COVID-19<br>anomaly",
    showarrow=True,
    arrowhead=2,
    arrowcolor="gray",
    font=dict(size=11, color="gray"),
    bgcolor="white",
    bordercolor="gray"
)

fig_grouped.update_layout(
    xaxis=dict(tickmode="linear"),
    xaxis_title="Year",
    yaxis_title="Mean AQI",
    legend_title="Period",
    hovermode="x unified"
)
st.plotly_chart(fig_grouped, use_container_width=True)

st.caption(
    "Note: Year-to-year variation is expected. "
    "The statistical test above compares aggregate distributions "
    "across all years rather than individual year patterns."
)

st.divider()

# Impact score bar chart
st.subheader("Diwali Impact Score by Year")
st.caption(
    "Impact Score = Festival AQI minus Pre-Diwali AQI. "
    "Positive means pollution rose during Diwali. "
    "Negative means it was lower than the preceding week."
)

city_summary["Color"] = city_summary["Impact_Score"].apply(
    lambda x: "Higher than baseline" if x > 0 else "Lower than baseline"
)

fig_impact = px.bar(
    city_summary,
    x="Year",
    y="Impact_Score",
    color="Color",
    color_discrete_map={
        "Higher than baseline": "#E8524C",
        "Lower than baseline": "#00B050"
    },
    title=f"{selected_city} - Diwali Impact Score (Festival AQI − Pre-Diwali AQI)",
)

fig_impact.add_hline(
    y=0,
    line_dash="dash",
    line_color="black",
    line_width=1
)

# Annotate 2020
impact_2020 = city_summary[
    city_summary["Year"] == 2020
]["Impact_Score"].values[0]

fig_impact.add_annotation(
    x=2020,
    y=impact_2020 - 12 if impact_2020 < 0 else impact_2020 + 12,
    text="⚠️ COVID-19",
    showarrow=False,
    font=dict(size=11, color="gray")
)

fig_impact.update_layout(
    xaxis=dict(tickmode="linear"),
    xaxis_title="Year",
    yaxis_title="Impact Score (AQI points)",
    legend_title="",
    showlegend=True
)
st.plotly_chart(fig_impact, use_container_width=True)

st.caption(
    "Note: Year-to-year variation is expected. "
    "The statistical test above compares aggregate distributions "
    "across all years rather than individual year patterns."
)

st.divider()

# Bottom summary
st.subheader("Diwali Insight")

# Exclude 2020 for summary
city_excl_2020 = city_summary[city_summary["Year"] != 2020]
avg_impact = round(city_excl_2020["Impact_Score"].mean(), 1)
worst_year = city_excl_2020.loc[
    city_excl_2020["Impact_Score"].idxmax(), "Year"
]
worst_impact = round(city_excl_2020["Impact_Score"].max(), 1)

direction = "higher" if avg_impact > 0 else "lower"

st.info(f"""
**{selected_city} Diwali summary (excluding 2020):**
- Festival-period AQI was on average **{abs(avg_impact)} AQI points {direction}**
  than the preceding week across all Diwali windows
- Worst Diwali spike: **{worst_year}** with an impact score of **+{worst_impact}**
- 2020 excluded from summary - COVID-19 restrictions and firework bans
  produced anomalous negative impact scores across most cities
""")
