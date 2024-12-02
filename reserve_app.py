import streamlit as st
import pandas as pd
import altair as alt
import os

def main():
    st.title("Heatmap Visualization")

    # Path to the CSV file in the repo
    csv_path = "data/balthazar_data.csv"
    if not os.path.exists(csv_path):
        st.error(f"CSV file not found at {csv_path}. Please check the path and try again.")
        return
    
    df = pd.read_csv(csv_path)

    # Ensure required columns exist
    required_columns = ['day_of_week', 'table_slot', 'slope', 'intercept', 'observation_count', 'table_size']
    if not all(col in df.columns for col in required_columns):
        st.error(f"The dataset must contain the following columns: {required_columns}")
        return

    # Create the Value column
    df['Value'] = (df['slope'] * df['observation_count']) + df['intercept']

    # Filter by table size
    st.sidebar.header("Filters")
    filter_table_size_2 = st.sidebar.checkbox("Show Table Size 2", value=True)
    filter_table_size_4 = st.sidebar.checkbox("Show Table Size 4", value=True)

    if not (filter_table_size_2 or filter_table_size_4):
        st.warning("At least one table size must be selected for visualization.")
        return

    table_size_filter = []
    if filter_table_size_2:
        table_size_filter.append(2)
    if filter_table_size_4:
        table_size_filter.append(4)

    filtered_df = df[df['table_size'].isin(table_size_filter)]

    heatmap = filtered_df.groupby(['day_of_week', 'table_slot'])['Value'].sum().reset_index()

    day_mapper = {1: 'Sunday', 2: 'Monday', 3: 'Tuesday', 4: 'Wednesday', 5: 'Thursday', 6: 'Friday', 7: 'Saturday'}
    heatmap['day_str'] = heatmap['day_of_week'].map(day_mapper)
    heatmap['table_slot'] = pd.to_datetime(heatmap['table_slot'], format='%H:%M').dt.time
    heatmap['table_slot_str'] = heatmap['table_slot'].apply(
        lambda x: f"{x.hour}:{x.minute:02d} {'AM' if x.hour < 12 else 'PM'}"
    )
 
    # Number of unique days and time slots
    num_days = heatmap['day_str'].nunique()
    num_time_slots = heatmap['table_slot_str'].nunique()

    # Define the size of the squares
    square_size = 40

    # Set chart properties to create squares
    heatmap_chart = alt.Chart(heatmap, title="Odds of Getting a Table").mark_rect().encode(
        y=alt.Y('day_str:O', sort=alt.EncodingSortField(field="day_of_week", order='ascending'), title='Weekday'),
        x=alt.X('table_slot_str:O', sort=alt.EncodingSortField(field="table_slot", order='ascending'), title='Time Slot'),
        color=alt.Color('Value:Q', title='Odds',scale=alt.Scale(
            domain=list(heatmap['Value'].quantile([0, 0.05, 0.5, 0.95, 1])),
            range=['white', '#d3f9d8', '#95d79e', '#4ca672', 'forestgreen']
        )),
        tooltip=[
            alt.Tooltip('day_str', title='Weekday'),
            alt.Tooltip('table_slot_str', title='Time Slot'),
            alt.Tooltip('Value', title='Odds of Table Availability')
        ]
    ).properties(
        width=square_size * num_time_slots,  
        height=square_size * num_days          
    ).configure_view(
        strokeWidth=0 
    )

    st.altair_chart(heatmap_chart, use_container_width=True)
if __name__ == "__main__":
    main()