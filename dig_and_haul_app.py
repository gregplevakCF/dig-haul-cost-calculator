"""
Dig and Haul Cost Calculator - Streamlit Web App
Run with: streamlit run dig_and_haul_app.py
"""

import streamlit as st
import pandas as pd
import math

# Page configuration
st.set_page_config(
    page_title="Dig and Haul Cost Calculator",
    page_icon="🚜",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .big-font {
        font-size:20px !important;
        font-weight: bold;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# Logo and Title
col1, col2 = st.columns([1, 4])
with col1:
    st.image("Clean_Futures_2.png", width=200)
with col2:
    st.title("Dig and Haul Cost Calculator")
    st.markdown("Calculate costs and CO2 emissions for excavating contaminated soil and replacing with clean backfill")

# Sidebar for inputs
st.sidebar.header("📋 Project Inputs")

# Project Info
st.sidebar.subheader("Project Information")
total_volume = st.sidebar.number_input("Total Volume to Excavate (CY)", min_value=1, value=1000, step=50)
work_hours_per_day = st.sidebar.number_input("Work Hours per Day", min_value=1, value=10, step=1)

# Equipment
st.sidebar.subheader("Equipment at Site")
num_excavators = st.sidebar.number_input("Number of Excavators", min_value=0, value=1, step=1)
excavator_rate = st.sidebar.number_input("Excavator Hourly Rate ($)", min_value=0, value=150, step=5)
excavator_fuel = st.sidebar.number_input("Excavator Fuel (gal/hr)", min_value=0.0, value=6.0, step=0.5)
excavator_capacity = st.sidebar.number_input("Excavator Production (CY/hr)", min_value=0, value=40, step=5)

num_loaders = st.sidebar.number_input("Number of Loaders", min_value=0, value=1, step=1)
loader_rate = st.sidebar.number_input("Loader Hourly Rate ($)", min_value=0, value=125, step=5)
loader_fuel = st.sidebar.number_input("Loader Fuel (gal/hr)", min_value=0.0, value=5.0, step=0.5)
loader_capacity = st.sidebar.number_input("Loader Production (CY/hr)", min_value=0, value=35, step=5)

# Trucking
st.sidebar.subheader("Trucking")
num_trucks = st.sidebar.number_input("Number of Trucks", min_value=1, value=3, step=1)
truck_capacity = st.sidebar.number_input("Truck Capacity (CY)", min_value=1, value=18, step=1)
truck_hourly_rate = st.sidebar.number_input("Truck Hourly Rate (includes driver)", min_value=0, value=85, step=5)
truck_fuel_rate = st.sidebar.number_input("Truck Fuel (gal/hr)", min_value=0.0, value=4.0, step=0.5)
fuel_cost = st.sidebar.number_input("Fuel Cost ($/gallon)", min_value=0.0, value=3.50, step=0.10)

st.sidebar.subheader("Trip Times")
loading_time = st.sidebar.number_input("Loading Time (hours)", min_value=0.0, value=0.25, step=0.05)
travel_time = st.sidebar.number_input("Travel to Landfill (hours, one-way)", min_value=0.0, value=0.5, step=0.1)
landfill_time = st.sidebar.number_input("Time at Landfill (wait + dump, hours)", min_value=0.0, value=0.5, step=0.1)

# Backfill
st.sidebar.subheader("Backfill")
backfill_at_landfill = st.sidebar.checkbox("Backfill Available at Landfill", value=True)
backfill_cost = st.sidebar.number_input("Backfill Cost ($/CY)", min_value=0, value=15, step=1)

if not backfill_at_landfill:
    travel_to_backfill = st.sidebar.number_input("Travel to Backfill Site (hours)", min_value=0.0, value=0.5, step=0.1)
    backfill_loading_time = st.sidebar.number_input("Backfill Loading Time (hours)", min_value=0.0, value=0.25, step=0.05)
    backfill_equip_cost = st.sidebar.number_input("Backfill Site Equipment ($/hr)", min_value=0, value=150, step=10)
else:
    travel_to_backfill = 0
    backfill_loading_time = 0
    backfill_equip_cost = 0

# Disposal
st.sidebar.subheader("Disposal")
disposal_cost = st.sidebar.number_input("Disposal Cost ($/CY)", min_value=0, value=45, step=1)

# Calculate button
calculate = st.sidebar.button("🧮 Calculate", type="primary")

# Main content area
if calculate or 'results' in st.session_state:
    
    # Perform calculations
    # Equipment capacity
    excavator_total_capacity = num_excavators * excavator_capacity
    loader_total_capacity = num_loaders * loader_capacity
    
    # Sequential equipment - use minimum (bottleneck)
    if excavator_total_capacity > 0 and loader_total_capacity > 0:
        excavation_capacity = min(excavator_total_capacity, loader_total_capacity)
        if excavator_total_capacity < loader_total_capacity:
            equipment_bottleneck = "Excavator"
        elif loader_total_capacity < excavator_total_capacity:
            equipment_bottleneck = "Loader"
        else:
            equipment_bottleneck = "Balanced"
    elif excavator_total_capacity > 0:
        excavation_capacity = excavator_total_capacity
        equipment_bottleneck = "N/A"
    else:
        excavation_capacity = loader_total_capacity
        equipment_bottleneck = "N/A"
    
    excavation_volume_per_day = excavation_capacity * work_hours_per_day
    
    # Trip time calculation
    if backfill_at_landfill:
        trip_time = loading_time + travel_time + landfill_time + travel_time + loading_time
    else:
        trip_time = loading_time + travel_time + landfill_time + travel_to_backfill + backfill_loading_time + travel_time + loading_time
    
    # Trucking capacity
    trips_per_truck_per_day = work_hours_per_day / trip_time
    total_trips_per_day = trips_per_truck_per_day * num_trucks
    truck_volume_per_day = total_trips_per_day * truck_capacity
    
    # Determine bottleneck
    limiting_volume = min(excavation_volume_per_day, truck_volume_per_day)
    if limiting_volume == truck_volume_per_day:
        bottleneck = "Trucking"
    else:
        bottleneck = "Excavation"
    
    # Project duration
    project_days = math.ceil(total_volume / limiting_volume)
    project_hours = project_days * work_hours_per_day
    
    # Number of trips
    num_trips = math.ceil(total_volume / truck_capacity)
    
    # Costs
    # Equipment
    excavator_cost = num_excavators * excavator_rate * project_hours
    excavator_fuel_cost = num_excavators * excavator_fuel * project_hours * fuel_cost
    loader_cost = num_loaders * loader_rate * project_hours
    loader_fuel_cost = num_loaders * loader_fuel * project_hours * fuel_cost
    
    total_equipment_cost = excavator_cost + loader_cost
    total_equipment_fuel_cost = excavator_fuel_cost + loader_fuel_cost
    
    # Trucking
    total_truck_hours = num_trips * trip_time
    trucking_cost = total_truck_hours * truck_hourly_rate
    truck_fuel_cost = total_truck_hours * truck_fuel_rate * fuel_cost
    
    # Disposal
    total_disposal_cost = total_volume * disposal_cost
    
    # Backfill
    total_backfill_cost = total_volume * backfill_cost
    backfill_site_cost = 0
    if not backfill_at_landfill:
        backfill_site_cost = total_truck_hours * backfill_equip_cost
    
    # Total cost
    total_cost = (total_equipment_cost + total_equipment_fuel_cost + 
                  trucking_cost + truck_fuel_cost + 
                  total_disposal_cost + total_backfill_cost + backfill_site_cost)
    
    cost_per_cy = total_cost / total_volume
    
    # CO2 calculations
    total_fuel_gallons = (num_excavators * excavator_fuel * project_hours + 
                         num_loaders * loader_fuel * project_hours +
                         total_truck_hours * truck_fuel_rate)
    co2_lbs = total_fuel_gallons * 22.4  # EPA standard
    co2_tons = co2_lbs / 2000
    
    # Store results
    st.session_state['results'] = {
        'total_cost': total_cost,
        'cost_per_cy': cost_per_cy,
        'project_days': project_days,
        'project_hours': project_hours,
        'num_trips': num_trips,
        'bottleneck': bottleneck,
        'co2_tons': co2_tons,
        'excavator_capacity': excavator_total_capacity,
        'loader_capacity': loader_total_capacity,
        'excavation_capacity': excavation_capacity,
        'equipment_bottleneck': equipment_bottleneck,
        'truck_volume_per_day': truck_volume_per_day,
        'excavation_volume_per_day': excavation_volume_per_day,
        'total_equipment_cost': total_equipment_cost,
        'total_equipment_fuel_cost': total_equipment_fuel_cost,
        'trucking_cost': trucking_cost,
        'truck_fuel_cost': truck_fuel_cost,
        'total_disposal_cost': total_disposal_cost,
        'total_backfill_cost': total_backfill_cost,
        'backfill_site_cost': backfill_site_cost,
        'total_fuel_gallons': total_fuel_gallons,
        'trip_time': trip_time,
        'trips_per_truck_per_day': trips_per_truck_per_day
    }
    
    results = st.session_state['results']
    
    # Display results
    st.header("📊 Results Summary")
    
    # Key metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Cost", f"${results['total_cost']:,.0f}")
        st.metric("Cost per CY", f"${results['cost_per_cy']:.2f}")
    
    with col2:
        st.metric("Project Duration", f"{results['project_days']} days")
        st.metric("Work Hours", f"{results['project_hours']} hrs")
    
    with col3:
        st.metric("CO2 Emissions", f"{results['co2_tons']:.2f} tons")
        st.metric("Truck Trips", f"{results['num_trips']} trips")
    
    with col4:
        st.metric("Bottleneck", results['bottleneck'])
        st.metric("Equipment Limit", results['equipment_bottleneck'])
    
    # Detailed breakdowns
    st.header("📈 Detailed Analysis")
    
    tab1, tab2, tab3 = st.tabs(["💰 Cost Breakdown", "⚙️ Capacity Analysis", "🌍 Environmental Impact"])
    
    with tab1:
        st.subheader("Cost Breakdown")
        
        col1, col2 = st.columns(2)
        
        with col1:
            cost_data = {
                'Category': [
                    'Equipment Rental',
                    'Equipment Fuel',
                    'Trucking',
                    'Truck Fuel',
                    'Disposal',
                    'Backfill Material',
                    'Backfill Site Equipment'
                ],
                'Cost': [
                    f"${results['total_equipment_cost']:,.0f}",
                    f"${results['total_equipment_fuel_cost']:,.0f}",
                    f"${results['trucking_cost']:,.0f}",
                    f"${results['truck_fuel_cost']:,.0f}",
                    f"${results['total_disposal_cost']:,.0f}",
                    f"${results['total_backfill_cost']:,.0f}",
                    f"${results['backfill_site_cost']:,.0f}"
                ]
            }
            df_costs = pd.DataFrame(cost_data)
            st.dataframe(df_costs, hide_index=True, use_container_width=True)
        
        with col2:
            # Pie chart of costs
            cost_values = [
                results['total_equipment_cost'],
                results['total_equipment_fuel_cost'],
                results['trucking_cost'],
                results['truck_fuel_cost'],
                results['total_disposal_cost'],
                results['total_backfill_cost'],
                results['backfill_site_cost']
            ]
            cost_labels = ['Equipment', 'Equip Fuel', 'Trucking', 'Truck Fuel', 'Disposal', 'Backfill', 'Backfill Site']
            
            # Create simple bar chart
            chart_data = pd.DataFrame({
                'Category': cost_labels,
                'Cost': cost_values
            })
            st.bar_chart(chart_data.set_index('Category'))
    
    with tab2:
        st.subheader("Capacity Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Equipment Capacity**")
            capacity_data = {
                'Component': [
                    'Excavator Capacity',
                    'Loader Capacity',
                    'Excavation Capacity (bottleneck)',
                    'Equipment Bottleneck',
                    'Excavation Volume per Day'
                ],
                'Value': [
                    f"{results['excavator_capacity']} CY/hr" if results['excavator_capacity'] > 0 else 'N/A',
                    f"{results['loader_capacity']} CY/hr" if results['loader_capacity'] > 0 else 'N/A',
                    f"{results['excavation_capacity']} CY/hr",
                    results['equipment_bottleneck'],
                    f"{results['excavation_volume_per_day']:.0f} CY"
                ]
            }
            df_capacity = pd.DataFrame(capacity_data)
            st.dataframe(df_capacity, hide_index=True, use_container_width=True)
        
        with col2:
            st.markdown("**Trucking Capacity**")
            truck_data = {
                'Component': [
                    'Number of Trucks',
                    'Truck Capacity',
                    'Trip Time',
                    'Trips per Truck per Day',
                    'Total Trips per Day',
                    'Truck Volume per Day'
                ],
                'Value': [
                    f"{num_trucks}",
                    f"{truck_capacity} CY",
                    f"{results['trip_time']:.2f} hrs",
                    f"{results['trips_per_truck_per_day']:.1f}",
                    f"{results['trips_per_truck_per_day'] * num_trucks:.1f}",
                    f"{results['truck_volume_per_day']:.0f} CY"
                ]
            }
            df_trucks = pd.DataFrame(truck_data)
            st.dataframe(df_trucks, hide_index=True, use_container_width=True)
        
        # Bottleneck explanation
        st.info(f"""
        **System Bottleneck: {results['bottleneck']}**
        
        - Excavation can move: {results['excavation_volume_per_day']:.0f} CY/day
        - Trucks can move: {results['truck_volume_per_day']:.0f} CY/day
        - Limiting factor: {min(results['excavation_volume_per_day'], results['truck_volume_per_day']):.0f} CY/day
        
        {"Consider adding more trucks to increase productivity." if results['bottleneck'] == 'Trucking' else "Consider adding more excavation equipment or increasing production rates."}
        """)
    
    with tab3:
        st.subheader("Environmental Impact")
        
        col1, col2 = st.columns(2)
        
        with col1:
            env_data = {
                'Metric': [
                    'Total Fuel Consumed',
                    'CO2 Emissions (lbs)',
                    'CO2 Emissions (tons)',
                    'CO2 per Cubic Yard'
                ],
                'Value': [
                    f"{results['total_fuel_gallons']:.0f} gallons",
                    f"{co2_lbs:,.0f} lbs",
                    f"{results['co2_tons']:.2f} tons",
                    f"{co2_lbs / total_volume:.2f} lbs/CY"
                ]
            }
            df_env = pd.DataFrame(env_data)
            st.dataframe(df_env, hide_index=True, use_container_width=True)
        
        with col2:
            st.metric("🌳 Equivalent Trees Needed", f"{int(results['co2_tons'] * 16.5):,}")
            st.caption("Trees needed to offset CO2 over 1 year (EPA estimate)")
            
            st.metric("🚗 Equivalent Car Miles", f"{int(results['co2_tons'] * 2500):,}")
            st.caption("Miles driven by average car (EPA estimate)")
    
    # Download results
    st.header("💾 Download Results")
    
    # Create downloadable CSV
    results_summary = pd.DataFrame({
        'Metric': [
            'Total Volume (CY)',
            'Total Cost',
            'Cost per CY',
            'Project Duration (days)',
            'Project Hours',
            'Number of Trips',
            'Bottleneck',
            'Equipment Bottleneck',
            'CO2 Emissions (tons)',
            'Total Fuel (gallons)'
        ],
        'Value': [
            total_volume,
            f"${results['total_cost']:,.2f}",
            f"${results['cost_per_cy']:.2f}",
            results['project_days'],
            results['project_hours'],
            results['num_trips'],
            results['bottleneck'],
            results['equipment_bottleneck'],
            f"{results['co2_tons']:.2f}",
            f"{results['total_fuel_gallons']:.0f}"
        ]
    })
    
    csv = results_summary.to_csv(index=False)
    st.download_button(
        label="📥 Download Results as CSV",
        data=csv,
        file_name="dig_and_haul_results.csv",
        mime="text/csv"
    )

else:
    # Welcome screen
    st.info("👈 Enter your project parameters in the sidebar and click **Calculate** to see results")
    
    st.markdown("""
    ### How to Use This Calculator
    
    1. **Enter project information** - total volume and work hours
    2. **Configure equipment** - excavators and loaders at the site
    3. **Set trucking parameters** - number of trucks, capacity, and trip times
    4. **Specify backfill location** - at landfill or separate site
    5. **Enter costs** - disposal and backfill pricing
    6. **Click Calculate** to see results!
    
    ### What You'll Get
    
    - **Total project cost** and cost per cubic yard
    - **Project duration** based on equipment and truck capacity
    - **Bottleneck analysis** - what's limiting your productivity
    - **CO2 emissions** tracking
    - **Detailed breakdowns** of costs and capacity
    
    ### Key Features
    
    ✅ **Sequential equipment modeling** - excavator → loader chain  
    ✅ **Bottleneck identification** - trucking vs excavation  
    ✅ **Environmental tracking** - CO2 emissions  
    ✅ **Cost optimization** - see where money is going  
    ✅ **Downloadable results** - export to CSV
    """)

# Footer
st.markdown("---")
footer_col1, footer_col2 = st.columns([3, 1])
with footer_col1:
    st.markdown("**Dig and Haul Cost Calculator** v1.1 | Built by Clean Futures with Streamlit")
with footer_col2:
    st.image("Clean_Futures_2.png", width=150)
