import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Page configuration
st.set_page_config(page_title="KHWEZI MINING MONITORING APPLICATION", layout="wide")
st.title("KHWEZI MINING MONITORING SYSTEM")
st.markdown("""
<style>
.main-header {
    background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
    padding: 1.2rem;
    border-radius: 10px;
    color: white;
    margin-bottom: 1rem;
}
.alert-critical {
    background-color: #ffebee;
    border-left: 6px solid #c62828;
    padding: 1rem;
    border-radius: 6px;
    margin: 0.6rem 0;
    font-family: monospace;
}
.alert-warning {
    background-color: #fff8e1;
    border-left: 6px solid #f9a825;
    padding: 1rem;
    border-radius: 6px;
    margin: 0.6rem 0;
    font-family: monospace;
}
.alert-normal {
    background-color: #e8f5e9;
    border-left: 6px solid #2e7d32;
    padding: 1rem;
    border-radius: 6px;
    margin: 0.6rem 0;
    font-family: monospace;
}
.risk-box {
    padding: 1.5rem;
    border-radius: 10px;
    text-align: center;
    color: white;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

# LUXURY BLACK & METALLIC GOLD THEME
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-color: #0B0C10;
    }

    /* Sidebar background */
    [data-testid="stSidebar"] {
        background-color: #111111;
        border-right: 1px solid #D4AF37;
    }

    /* METALLIC GOLD TEXT EFFECT FOR HEADERS */
    h1, h2, h3, h4, h5, h6 {
        background: linear-gradient(to right, #BF953F, #FCF6BA, #B38728, #FBF5B7, #AA771C);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        text-shadow: 0px 0px 15px rgba(212, 175, 55, 0.2); /* Soft glow */
    }

    /* Normal text color */
    p, span, div {
        color: #E0E0E0;
    }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(to right, #BF953F, #FCF6BA, #B38728);
        color: #0B0C10 !important;
        border: none;
        font-weight: bold;
        box-shadow: 0px 4px 10px rgba(212, 175, 55, 0.3);
    }
    .stButton>button:hover {
        background: linear-gradient(to right, #FCF6BA, #BF953F, #FCF6BA);
        box-shadow: 0px 4px 15px rgba(212, 175, 55, 0.6);
    }

    /* Dataframes / Tables */
    [data-testid="stDataFrame"] {
        background-color: #151515;
        border: 1px solid #333;
    }

    /* Big Numbers (Metrics) */
    [data-testid="stMetricValue"] {
        background: linear-gradient(to right, #BF953F, #FCF6BA, #B38728);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
        font-size: 2.5rem !important;
    }

    /* Metric Labels */
    [data-testid="stMetricLabel"] {
        color: #888888;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 0.8rem !important;
    }
    
      /* CUSTOM ALERT BOXES */
    .alert-box {
        background-color: #1A1A1A; /* Dark grey background */
        border-left: 6px solid #D4AF37; /* Gold border */
        padding: 1.2rem;
        border-radius: 8px;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.5);
        font-family: monospace;
        color: #E0E0E0; /* Light grey text */
        white-space: pre-wrap; /* Keeps the line breaks from the alert text */
    }
    
    /* Override the category label to be gold */
    .category-label {
        color: #D4AF37;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 5px;
    }  
    

    
</style>
""", unsafe_allow_html=True)

# Load Data
@st.cache_data
def load_data():
    workers = pd.read_csv('workers_database.csv')
    incidents = pd.read_csv('safety_incidents_database.csv')
    equipment = pd.read_csv( 'Equipment_database.csv')
    users = pd.read_csv('Users_database.csv', sep=';')
    return workers, incidents, equipment, users
workers_df, incidents_df, equipment_df, users_df= load_data()

users_df.columns = users_df.columns.str.strip()

# MEMBER 4: RISK & ALERT HELPER FUNCTIONS

# Convert date columns to datetime for alert generation
incidents_df['Date'] = pd.to_datetime(incidents_df['Date'], errors='coerce')
equipment_df['Next_Maintenance_Due'] = pd.to_datetime(equipment_df['Next_Maintenance_Due'], errors='coerce')
equipment_df['Last_Maintenance_Date'] = pd.to_datetime(equipment_df['Last_Maintenance_Date'], errors='coerce')

# Thresholds (Educational prototype thresholds only)
TEMP_NORMAL_MAX   = 80     # °C
TEMP_WARNING_MAX  = 100    # °C
VIB_NORMAL_MAX    = 5.0    # mm/s
VIB_WARNING_MAX   = 8.0    # mm/s
HIGH_DOWNTIME_HOURS   = 20
LOW_AVAILABILITY_PCT  = 75.0
HIGH_ALERT_COUNT      = 10

# Risk functions
def calculate_risk_score(likelihood: int, consequence: int) -> int:
    if not (1 <= likelihood <= 5) or not (1 <= consequence <= 5):
        raise ValueError("Likelihood and Consequence must be between 1 and 5.")
    return likelihood * consequence

def classify_risk(score: int) -> str:
    if 1 <= score <= 4:
        return "Low"
    elif 5 <= score <= 9:
        return "Medium"
    elif 10 <= score <= 16:
        return "High"
    elif 17 <= score <= 25:
        return "Critical"
    else:
        return "Unknown"

def is_high_or_critical(classification: str) -> bool:
    return classification in ("High", "Critical")

# Equipment status helpers
def temp_status(temp: float) -> str:
    if temp < TEMP_NORMAL_MAX:
        return "Normal"
    elif temp <= TEMP_WARNING_MAX:
        return "Warning"
    return "Critical"

def vib_status(vib: float) -> str:
    if vib < VIB_NORMAL_MAX:
        return "Normal"
    elif vib <= VIB_WARNING_MAX:
        return "Warning"
    return "Critical"

def calculate_availability(op_hours: float, downtime: float) -> float:
    total = op_hours + downtime
    if total == 0:
        return 0.0
    return round((op_hours / total) * 100, 2)

# Alert formatter
def format_alert(severity, source, equipment_id="N/A", parameter="N/A",
                 value="N/A", status="N/A",
                 recommended_action="Inspect and take appropriate action."):
    return (
        f"MINING MONITORING ALERT\n"
        f"[{severity.upper()}]\n"
        f"Source: {source}\n"
        f"Equipment/Worker ID: {equipment_id}\n"
        f"Parameter: {parameter}\n"
        f"Value: {value}\n"
        f"Status: {status}\n"
        f"Recommended Action:\n{recommended_action}"
    )

# Alert generators
def generate_equipment_alerts(equipment_df):
    alerts = []
    for _, row in equipment_df.iterrows():
        eq_id = row['Equipment_ID']
        eq_type = row['Equipment_Type']
        t_stat = temp_status(row['Temperature_C'])
        if t_stat == "Critical":
            alerts.append(format_alert("CRITICAL", f"Equipment ({eq_type})", eq_id,
                "Temperature", f"{row['Temperature_C']} °C",
                "Above Critical Threshold (>100 °C)",
                "Inspect equipment and initiate appropriate maintenance/safety procedures."))
        elif t_stat == "Warning":
            alerts.append(format_alert("WARNING", f"Equipment ({eq_type})", eq_id,
                "Temperature", f"{row['Temperature_C']} °C",
                "Approaching Critical Threshold (80–100 °C)",
                "Monitor temperature closely and schedule inspection."))
        v_stat = vib_status(row['Vibration_mm_s'])
        if v_stat == "Critical":
            alerts.append(format_alert("CRITICAL", f"Equipment ({eq_type})", eq_id,
                "Vibration", f"{row['Vibration_mm_s']} mm/s",
                "Above Critical Threshold (>8 mm/s)",
                "Inspect equipment and initiate appropriate maintenance/safety procedures."))
        elif v_stat == "Warning":
            alerts.append(format_alert("WARNING", f"Equipment ({eq_type})", eq_id,
                "Vibration", f"{row['Vibration_mm_s']} mm/s",
                "Approaching Critical Threshold (5–8 mm/s)",
                "Monitor vibration trend and schedule inspection."))
    return alerts

def generate_maintenance_alerts(equipment_df):
    alerts = []
    today = pd.Timestamp(datetime.now().date())
    for _, row in equipment_df.iterrows():
        eq_id = row['Equipment_ID']
        eq_type = row['Equipment_Type']
        availability = calculate_availability(
            row['Monitoring_Period_Operating_Hours'],
            row['Monitoring_Period_Downtime_Hours']
        )
        if pd.notna(row['Next_Maintenance_Due']) and row['Next_Maintenance_Due'] < today:
            days_overdue = (today - row['Next_Maintenance_Due']).days
            alerts.append(format_alert("CRITICAL", f"Maintenance ({eq_type})", eq_id,
                "Maintenance Due Date", str(row['Next_Maintenance_Due'].date()),
                f"Overdue by {days_overdue} day(s)",
                "Schedule and complete overdue maintenance immediately."))
        if row['Monitoring_Period_Downtime_Hours'] > HIGH_DOWNTIME_HOURS:
            alerts.append(format_alert("WARNING", f"Maintenance ({eq_type})", eq_id,
                "Downtime", f"{row['Monitoring_Period_Downtime_Hours']} hrs",
                f"Exceeds {HIGH_DOWNTIME_HOURS} hrs in monitoring period",
                "Investigate cause of excessive downtime and improve reliability."))
        if availability < LOW_AVAILABILITY_PCT:
            alerts.append(format_alert("WARNING", f"Maintenance ({eq_type})", eq_id,
                "Availability", f"{availability}%",
                f"Below {LOW_AVAILABILITY_PCT}% threshold",
                "Review maintenance strategy and operational plan."))
        if row['Alert_Count'] >= HIGH_ALERT_COUNT:
            alerts.append(format_alert("WARNING", f"Maintenance ({eq_type})", eq_id,
                "Alert Count", str(row['Alert_Count']),
                f"Repeated alerts (>= {HIGH_ALERT_COUNT})",
                "Perform root-cause analysis to reduce repeat alerts."))
    return alerts

def generate_worker_alerts(workers_df):
    alerts = []
    for _, row in workers_df.iterrows():
        w_id = row['Worker_ID']
        dept = row['Department']
        if row['PPE_Compliance'] == "No":
            alerts.append(format_alert("WARNING", f"Worker Safety ({dept})", w_id,
                "PPE Compliance", "No",
                "Worker not compliant with PPE requirements",
                "Stop task, provide correct PPE, and re-brief worker."))
        if row['Fatigue_Level'] == "High":
            alerts.append(format_alert("CRITICAL", f"Worker Safety ({dept})", w_id,
                "Fatigue Level", "High",
                "Worker fatigue exceeds safe working level",
                "Remove worker from high-risk task and review shift roster."))
        if row['Safety_Training_Status'] == "Incomplete":
            alerts.append(format_alert("WARNING", f"Worker Safety ({dept})", w_id,
                "Safety Training Status", "Incomplete",
                "Worker has not completed required safety training",
                "Schedule worker for outstanding safety training."))
    return alerts

def generate_incident_alerts(incidents_df):
    alerts = []
    for _, row in incidents_df.iterrows():
        inc_id = row['Incident_ID']
        if row['Risk_Level'] in ("High", "Critical"):
            sev = "CRITICAL" if row['Risk_Level'] == "Critical" else "WARNING"
            alerts.append(format_alert(sev, f"Safety Incident ({row['Department']})", inc_id,
                "Incident Risk Level", row['Risk_Level'],
                f"{row['Incident_Type']} at {row['Location']} ({row['Incident_Status']})",
                row['Corrective_Action']))
        if row['Lost_Time_Injury'] == "Yes":
            alerts.append(format_alert("CRITICAL", f"Safety Incident ({row['Department']})", inc_id,
                "Lost Time Injury", f"Yes ({row['Days_Lost']} days lost)",
                f"{row['Severity']} — {row['Incident_Type']}",
                row['Corrective_Action']))
    return alerts
# RBAC PERMISSIONS
PERMISSIONS = {
    "Administrator":        ["Dashboard", "Worker Database", "Incident Database", "Equipment Health",
                             "Alerts & Notifications", "Risk Assessment", "Safety Analysis",
                             "Integrated Analysis", "Manage Users"],
    "Safety Officer":       ["Dashboard", "Worker Database", "Incident Database",
                             "Alerts & Notifications", "Risk Assessment", "Safety Analysis",
                             "Integrated Analysis"],
    "Mining Engineer":      ["Dashboard", "Worker Database", "Incident Database", "Equipment Health",
                             "Alerts & Notifications", "Risk Assessment", "Safety Analysis",
                             "Integrated Analysis"],
    "Maintenance Engineer": ["Dashboard", "Equipment Health", "Alerts & Notifications"],
    "Manager":              ["Dashboard", "Worker Database", "Incident Database", "Equipment Health",
                             "Alerts & Notifications", "Risk Assessment", "Safety Analysis",
                             "Integrated Analysis"]}


# SESSION STATE INIT
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.session_state.full_name = None

#  LOGIN SCREEN (only shown if not logged in)
if not st.session_state.logged_in:
    st.title(" Khwezi Mining Monitoring System")
    st.subheader("Please log in to continue")

    with st.form("login_form"):
        username_input = st.text_input("Username")
        password_input = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")

    if submit_button:
        if not username_input or not password_input:
            st.error("Please enter both username and password.")
        else:
            user_row = users_df[
                (users_df['username'] == username_input) &
                (users_df['password'] == password_input)
            ]
            if not user_row.empty:
                st.session_state.logged_in = True
                st.session_state.username = user_row.iloc[0]['username']
                st.session_state.role = user_row.iloc[0]['role']
                st.session_state.full_name = user_row.iloc[0]['full_name']
                st.rerun()
            else:
                st.error("Invalid username or password.")

    st.stop()  # hides everything below until logged in

# USER IS NOW LOGGED IN
st.sidebar.title("Navigation")
st.sidebar.write(f"{st.session_state.full_name}")
st.sidebar.write(f" {st.session_state.role}")

if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()
allowed_pages = PERMISSIONS.get(st.session_state.role, [])
page = st.sidebar.radio("Go to:", allowed_pages)


# PAGE 1: WORKER DATABASE
if page == "Worker Database":
    st.header("Worker Safety Database")

    # WARNINGS
    st.subheader("Safety Warnings")
    low_ppe = workers_df[workers_df['PPE_Compliance'] == 'No']
    high_fatigue = workers_df[workers_df['Fatigue_Level'] == 'High']

    col1, col2 = st.columns(2)
    with col1:
        if not low_ppe.empty:
            st.warning(f"ALERT: {len(low_ppe)} workers have LOW PPE compliance!")
        else:
            st.success("All workers have acceptable PPE compliance.")
    with col2:
        if not high_fatigue.empty:
            st.error(f"ALERT: {len(high_fatigue)} workers have HIGH fatigue levels!")
        else:
            st.success("Fatigue levels are within safe limits.")

    # Show who is at risk
    st.write("**Workers flagged for review:**")
    at_risk = workers_df[(workers_df['PPE_Compliance'] == 'No') | (workers_df['Fatigue_Level'] == 'High')]
    st.dataframe(at_risk, use_container_width=True)

    # SEARCH & FILTER
    st.subheader("Search & Filter Workers")
    col1, col2, col3 = st.columns(3)
    with col1:
        search_id = st.text_input("Search by Worker ID (e.g., WRK-001)")
    with col2:
        filter_dept = st.selectbox("Filter by Department", ["All"] + list(workers_df['Department'].unique()))
    with col3:
        filter_risk = st.selectbox("Filter by Risk Level", ["All"] + list(workers_df['Risk_Level'].unique()))

    filtered_workers = workers_df.copy()
    if search_id:
        filtered_workers = filtered_workers[filtered_workers['Worker_ID'].str.contains(search_id, case=False)]
    if filter_dept != "All":
        filtered_workers = filtered_workers[filtered_workers['Department'] == filter_dept]
    if filter_risk != "All":
        filtered_workers = filtered_workers[filtered_workers['Risk_Level'] == filter_risk]

    st.dataframe(filtered_workers, use_container_width=True)
    st.metric("Total Workers Displayed", len(filtered_workers))

elif page == "Incident Database":
    st.header("Incident Management")

    #  FILTERS
    st.subheader("View & Filter Incidents")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        filter_severity = st.multiselect(
            "Severity",
            options=incidents_df['Severity'].unique(),
            default=incidents_df['Severity'].unique(),
            key="inc_severity"
        )
    with col2:
        filter_shift = st.multiselect(
            "Shift",
            options=incidents_df['Shift'].unique(),
            default=incidents_df['Shift'].unique(),
            key="inc_shift"
        )
    with col3:
        filter_status = st.multiselect(
            "Status",
            options=incidents_df['Incident_Status'].unique(),
            default=incidents_df['Incident_Status'].unique(),
            key="inc_status"
        )
    with col4:
        search_inc = st.text_input("Search by Incident ID", key="inc_search")

    # APPLY FILTERS
    filtered_incidents = incidents_df[
        (incidents_df['Severity'].isin(filter_severity)) &
        (incidents_df['Shift'].isin(filter_shift)) &
        (incidents_df['Incident_Status'].isin(filter_status))
        ]

    if search_inc:
        filtered_incidents = filtered_incidents[
            filtered_incidents['Incident_ID'].str.contains(search_inc, case=False)
        ]

    st.dataframe(filtered_incidents, use_container_width=True)
    st.metric("Total Incidents Displayed", len(filtered_incidents))

    # TRENDS CHART
    st.subheader("Incident Trends Over Time")
    if not filtered_incidents.empty:
        temp_df = filtered_incidents.copy()
        temp_df['Date'] = pd.to_datetime(temp_df['Date'])
        trend_data = temp_df.groupby(temp_df['Date'].dt.date).size().reset_index(name='Count')
        fig = px.line(trend_data, x='Date', y='Count', title='Incidents per Day', markers=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No incidents match your filters.")

elif page == "Equipment Health":
    st.header("Equipment Health")

    # STATUS FUNCTION
    # Educational prototype thresholds only
    TEMP_WARNING = 80
    TEMP_CRITICAL = 100
    VIB_WARNING = 5
    VIB_CRITICAL = 8

    def status_check(temp, vib):
        if temp >= TEMP_CRITICAL or vib >= VIB_CRITICAL:
            return "CRITICAL"
        elif temp >= TEMP_WARNING or vib >= VIB_WARNING:
            return "WARNING"
        else:
            return "NORMAL"

    equipment_df["Status"] = equipment_df.apply(
        lambda row: status_check(row["Temperature_C"], row["Vibration_mm_s"]), axis=1
    )

    #  CHARTS ROW 1
    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(
            equipment_df.sort_values("Availability_Percent"),
            x="Equipment_ID", y="Availability_Percent",
            color="Maintenance_Status",
            title="Equipment Availability (%)",
            color_discrete_map={"Operational": "#2ecc71", "Under Maintenance": "#e74c3c"}
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.scatter(
            equipment_df, x="Temperature_C", y="Vibration_mm_s",
            color="Equipment_Type", size="Alert_Count",
            hover_data=["Equipment_ID", "Manufacturer"],
            title="Temperature vs Vibration (size = alerts)"
        )
        st.plotly_chart(fig, use_container_width=True)

    # CHARTS ROW 2
    col3, col4 = st.columns(2)

    with col3:
        fig = px.histogram(
            equipment_df, x="Downtime_Hours", color="Department",
            title="Downtime Distribution by Department"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        fig = px.box(
            equipment_df, x="Equipment_Type", y="Operating_Hours",
            color="Equipment_Type", title="Operating Hours by Type"
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    # ALERT TABLE
    st.subheader("Equipment Needing Attention")
    flagged = equipment_df[
        (equipment_df["Alert_Count"] >= 8) |
        (equipment_df["Availability_Percent"] < 80) |
        (equipment_df["Brake_Status"] != "Normal") |
        (equipment_df["Engine_Status"] != "Normal") |
        (equipment_df["Status"] != "NORMAL")
    ][["Equipment_ID", "Equipment_Type", "Department", "Operating_Hours",
       "Temperature_C", "Vibration_mm_s", "Brake_Status", "Engine_Status",
       "Availability_Percent", "Maintenance_Status", "Alert_Count", "Status"]]
    st.dataframe(flagged, use_container_width=True)

    # SUMMARY METRICS
    st.subheader("Equipment Summary")
    col1, col2, col3 = st.columns(3)
    with col1:
        normal_count = len(equipment_df[equipment_df["Status"] == "NORMAL"])
        st.metric("Normal Equipment", normal_count)
    with col2:
        warning_count = len(equipment_df[equipment_df["Status"] == "WARNING"])
        st.metric("Warning Equipment", warning_count)
    with col3:
        critical_count = len(equipment_df[equipment_df["Status"] == "CRITICAL"])
        st.metric("Critical Equipment", critical_count)

elif page == "Safety Analysis":
    st.header("Health and Safety Analysis (Appendix A)")
    st.write("Using Pandas `groupby` to answer the safety questions.")

    # QUESTION 1: Incidents by Department
    st.subheader("1. Incidents by Department")
    dept_incidents = incidents_df.groupby('Department').size().reset_index(name='Incident Count')
    dept_incidents = dept_incidents.sort_values('Incident Count', ascending=False)
    fig_dept = px.bar(
        dept_incidents,
        x='Department',
        y='Incident Count',
        color='Department',
        title='Incidents by Department'
    )
    st.plotly_chart(fig_dept, use_container_width=True)

    # QUESTION 2: Incidents by Shift (Day vs Night)
    st.subheader("2. Incidents by Shift (Day vs Night)")
    shift_counts = incidents_df.groupby('Shift').size().reset_index(name='Count')
    fig_shift = px.pie(
        shift_counts,
        names='Shift',
        values='Count',
        title='Incident Distribution by Shift',
        hole=0.4
    )
    st.plotly_chart(fig_shift, use_container_width=True)

    # QUESTION 3: Incidents by Severity
    st.subheader("3. Incident Severity Breakdown")
    severity_counts = incidents_df.groupby('Severity').size().reset_index(name='Count')
    fig_sev = px.bar(
        severity_counts,
        x='Severity',
        y='Count',
        color='Severity',
        title='Incidents by Severity'
    )
    st.plotly_chart(fig_sev, use_container_width=True)

    # QUESTION 4: Incidents by Risk Level
    st.subheader("4. Risk Level Breakdown")
    risk_counts = incidents_df.groupby('Risk_Level').size().reset_index(name='Count')
    fig_risk = px.pie(
        risk_counts,
        names='Risk_Level',
        values='Count',
        title='Incidents by Risk Level',
        hole=0.4
    )
    st.plotly_chart(fig_risk, use_container_width=True)

    #  QUESTION 5: Lost Time Injuries vs Non-Lost Time
    st.subheader("5. Lost-Time Injuries vs Non-Lost Time")
    lost_time_counts = incidents_df.groupby('Lost_Time_Injury').size().reset_index(name='Count')
    fig_lti = px.bar(
        lost_time_counts,
        x='Lost_Time_Injury',
        y='Count',
        color='Lost_Time_Injury',
        title='Lost-Time Injury Breakdown'
    )
    st.plotly_chart(fig_lti, use_container_width=True)

    # SUMMARY METRICS
    st.subheader("Summary Metrics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Incidents", len(incidents_df))
    with col2:
        lti_count = len(incidents_df[incidents_df['Lost_Time_Injury'] == 'Yes'])
        st.metric("Lost-Time Injuries", lti_count)
    with col3:
        dmre_count = len(incidents_df[incidents_df['Reported_To_DMRE'] == 'Yes'])
        st.metric("Reported to DMRE", dmre_count)

# DASHBOARD (Member 1)
if page == "Dashboard":
    st.header("Mining Monitoring Dashboard")

    # Safety KPIs
    total_workers = len(workers_df)
    total_incidents = len(incidents_df)
    near_misses = len(incidents_df[incidents_df['Incident_Category'] == 'Near Miss'])
    high_fatigue = len(workers_df[workers_df['Fatigue_Level'] == 'High'])
    low_ppe = len(workers_df[workers_df['PPE_Compliance'] == 'No'])
    ppe_pct = round((1 - low_ppe / total_workers) * 100, 1) if total_workers else 0

    # Equipment KPIs
    total_equipment = len(equipment_df)
    under_maint = len(equipment_df[equipment_df['Maintenance_Status'] == 'Under Maintenance'])
    avg_avail = round(equipment_df['Availability_Percent'].mean(), 1)
    critical_alerts = len(equipment_df[equipment_df['Alert_Count'] >= 8])

    st.subheader(" Safety KPIs")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Workers", total_workers)
    c2.metric("Total Incidents", total_incidents)
    c3.metric("Near Misses", near_misses)
    c4.metric("PPE Compliance", f"{ppe_pct}%")

    st.subheader("Equipment KPIs")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Equipment", total_equipment)
    c2.metric("Under Maintenance", under_maint)
    c3.metric("Avg Availability", f"{avg_avail}%")
    c4.metric("Critical Alerts", critical_alerts)

    st.subheader("Risk Indicators")
    c1, c2, c3 = st.columns(3)
    c1.metric("High Fatigue Workers", high_fatigue)
    c2.metric("Low PPE Workers", low_ppe)
    c3.metric("High/Critical Incidents",
              len(incidents_df[incidents_df['Risk_Level'].isin(['High', 'Critical'])]))

    st.divider()
    st.info("KPI data is pulled live from the workers, incidents, and equipment databases.")


# RISK ASSESSMENT
elif page == "Risk Assessment":
    st.header("Risk Assessment")
    st.write("Risk Score = Likelihood × Consequence (1–5 scale)")

    # Interactive calculator
    st.subheader("Interactive Risk Score Calculator")
    col1, col2 = st.columns(2)
    with col1:
        likelihood = st.slider("Likelihood (1 = Rare, 5 = Almost Certain)", 1, 5, 3)
    with col2:
        consequence = st.slider("Consequence (1 = Insignificant, 5 = Catastrophic)", 1, 5, 3)

    score = calculate_risk_score(likelihood, consequence)
    classification = classify_risk(score)

    c1, c2 = st.columns(2)
    c1.metric("Risk Score", score)
    c2.metric("Classification", classification)

    if is_high_or_critical(classification):
        st.error(f" WARNING — {classification.upper()} RISK. "
                 "This activity requires immediate management intervention before work proceeds.")
    else:
        st.success(f"{classification} risk — proceed with standard controls.")

    # Risk matrix
    st.subheader("Risk Classification Matrix")
    matrix_rows = []
    for l in range(5, 0, -1):
        row = {"Likelihood": l}
        for c in range(1, 6):
            s = l * c
            row[f"C={c}"] = f"{s} ({classify_risk(s)})"
        matrix_rows.append(row)
    st.dataframe(pd.DataFrame(matrix_rows), hide_index=True, use_container_width=True)

    # Verify existing incidents
    st.subheader("Incident Risk Verification")
    if 'Likelihood' in incidents_df.columns and 'Consequence' in incidents_df.columns:
        verified = incidents_df.copy()
        verified['Computed_Score'] = verified['Likelihood'] * verified['Consequence']
        verified['Computed_Class'] = verified['Computed_Score'].apply(classify_risk)
        mismatches = verified[verified['Computed_Class'] != verified['Risk_Level']]

        c1, c2, c3 = st.columns(3)
        c1.metric("Incidents Checked", len(verified))
        c2.metric("Matches", len(verified) - len(mismatches))
        c3.metric("Mismatches", len(mismatches))

        if len(mismatches) > 0:
            st.warning(f"{len(mismatches)} incident(s) have stored Risk_Level different from computed.")
        else:
            st.success("All stored incident risk levels match computed classification.")

        # Distribution chart
        dist = verified['Computed_Class'].value_counts().reset_index()
        dist.columns = ['Classification', 'Count']
        fig = px.pie(dist, names='Classification', values='Count',
                     title='Computed Risk Classification Distribution')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Likelihood/Consequence columns not found in incidents data.")

# INTEGRATED ANALYSIS

elif page == "Integrated Analysis":
    st.header("Integrated Safety & Equipment Analysis")
    st.write("Cross-analysis combining safety incidents, workers, and equipment data.")

    # Q1: Which departments have both high safety risk and high equipment downtime?
    st.subheader("1. Departments with High Safety Risk & High Equipment Downtime")
    dept_incidents = incidents_df.groupby('Department').size().reset_index(name='Incidents')
    dept_downtime = equipment_df.groupby('Department')['Downtime_Hours'].sum().reset_index(name='Total Downtime')
    merged = pd.merge(dept_incidents, dept_downtime, on='Department', how='outer').fillna(0)
    fig = px.scatter(merged, x='Incidents', y='Total Downtime', text='Department',
                     title='Incidents vs Equipment Downtime by Department', size='Total Downtime')
    fig.update_traces(textposition='top center')
    st.plotly_chart(fig, use_container_width=True)

    # Q2: Which equipment contributes to the greatest number of alerts?
    st.subheader("2. Equipment with the Most Alerts")
    top_alerts = equipment_df.nlargest(10, 'Alert_Count')[['Equipment_ID', 'Equipment_Type', 'Alert_Count']]
    fig = px.bar(top_alerts, x='Equipment_ID', y='Alert_Count', color='Equipment_Type',
                 title='Top 10 Equipment by Alert Count')
    st.plotly_chart(fig, use_container_width=True)

    # Q3: What are the most common causes of safety incidents?
    st.subheader("3. Most Common Causes of Safety Incidents")
    causes = incidents_df.groupby('Cause').size().reset_index(name='Count').sort_values('Count', ascending=False).head(10)
    fig = px.bar(causes, x='Count', y='Cause', orientation='h', title='Top 10 Incident Causes')
    st.plotly_chart(fig, use_container_width=True)

    # Q4: Are safety incidents associated with particular shifts?
    st.subheader("4. Safety Incidents by Shift")
    shift_inc = incidents_df.groupby('Shift').size().reset_index(name='Count')
    fig = px.pie(shift_inc, names='Shift', values='Count', title='Incidents by Shift', hole=0.4)
    st.plotly_chart(fig, use_container_width=True)

    # Q5: Which equipment should receive maintenance priority?
    st.subheader("5. Maintenance Priority (Lowest Availability + Most Alerts)")
    priority = equipment_df.copy()
    priority['Priority_Score'] = (100 - priority['Availability_Percent']) + priority['Alert_Count'] * 5
    priority = priority.nlargest(10, 'Priority_Score')[
        ['Equipment_ID', 'Equipment_Type', 'Availability_Percent', 'Alert_Count', 'Priority_Score']
    ]
    st.dataframe(priority, use_container_width=True)

    st.divider()
    st.info("Integrated analysis combines data from Member 2 (incidents/workers) and Member 3 (equipment).")


# MANAGE USERS (Admin only)

elif page == "Manage Users":
    st.header(" Manage Users")
    st.write("Administrator access only.")
    st.dataframe(users_df, use_container_width=True)

    st.subheader("Add New User (Demo)")
    with st.form("new_user_form"):
        new_username = st.text_input("Username")
        new_full_name = st.text_input("Full Name")
        new_role = st.selectbox("Role", list(PERMISSIONS.keys()))
        new_password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Add User")

        if submit:
            if not new_username or not new_full_name or not new_password:
                st.warning("Please fill in all fields.")
            elif new_username in users_df['username'].values:
                st.error(f"Username '{new_username}' already exists.")
            else:
                st.success(f"User '{new_username}' added successfully! (Simulation only)")
# ALERTS & NOTIFICATIONS

elif page == "Alerts & Notifications":
    st.header("Alerts & Notifications")
    st.write("Auto-generated from equipment, maintenance, worker safety and incident data.")

    equipment_alerts  = generate_equipment_alerts(equipment_df)
    maintenance_alerts = generate_maintenance_alerts(equipment_df)
    worker_alerts     = generate_worker_alerts(workers_df)
    incident_alerts   = generate_incident_alerts(incidents_df)

    all_alerts = (
        [("Equipment", a)   for a in equipment_alerts] +
        [("Maintenance", a) for a in maintenance_alerts] +
        [("Worker Safety", a) for a in worker_alerts] +
        [("Incidents", a)   for a in incident_alerts]
    )

    def sev_of(alert_text):
        for line in alert_text.splitlines():
            if line.startswith("[") and line.endswith("]"):
                return line.strip("[]")
        return "NORMAL"

    crit_count = sum(1 for _, a in all_alerts if sev_of(a) == "CRITICAL")
    warn_count = sum(1 for _, a in all_alerts if sev_of(a) == "WARNING")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Alerts", len(all_alerts))
    c2.metric("Critical", crit_count)
    c3.metric("Warning", warn_count)
    c4.metric("Normal", len(all_alerts) - crit_count - warn_count)

    st.markdown("---")

    category_filter = st.multiselect(
        "Filter by category",
        ["Equipment", "Maintenance", "Worker Safety", "Incidents"],
        default=["Equipment", "Maintenance", "Worker Safety", "Incidents"],
        key="alert_cat"
    )
    severity_filter = st.multiselect(
        "Filter by severity",
        ["CRITICAL", "WARNING", "NORMAL"],
        default=["CRITICAL", "WARNING"],
        key="alert_sev"
    )

    filtered = [(cat, a) for cat, a in all_alerts
                if cat in category_filter and sev_of(a) in severity_filter]

    st.subheader(f"Active Alerts ({len(filtered)})")
    if not filtered:
        st.success("No alerts match the selected filters.")
    else:
        for cat, alert_text in filtered:
            # Render the custom dark alert box
            st.markdown(f"""
            <div class="category-label">Category: {cat}</div>
            <div class="alert-box">{alert_text}</div>
            """, unsafe_allow_html=True)