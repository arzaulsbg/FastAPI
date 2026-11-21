
import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(
    page_title="Student Registry",
    page_icon="🎓",
    layout="wide"
)

if "api_url" not in st.session_state:
    st.session_state.api_url = "http://127.0.0.1:8000"

if "activity" not in st.session_state:
    st.session_state.activity = []

if "selected_student_id" not in st.session_state:
    st.session_state.selected_student_id = None


# =========================================================
# CSS
# =========================================================
st.markdown("""
<style>
.stApp {
    background: #101010;
    color: #f3f4f6;
}

[data-testid="stSidebar"] {
    background: #171717;
    border-right: 1px solid #292929;
}

[data-testid="stSidebar"] * {
    color: #eeeeee;
}

.block-container {
    padding-top: 1.2rem;
    padding-bottom: 2rem;
    max-width: 1500px;
}

h1 {
    font-family: Georgia, serif !important;
    font-size: 42px !important;
    font-weight: 400 !important;
    letter-spacing: -1px;
}

h2, h3 {
    font-weight: 500 !important;
}

div[data-testid="stMetric"] {
    background: #191919;
    border: 1px solid #2b2b2b;
    border-radius: 14px;
    padding: 16px 18px;
}

div[data-testid="stMetricLabel"] {
    color: #9ca3af;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 1px;
}

div[data-testid="stMetricValue"] {
    color: #ffffff;
    font-family: Georgia, serif;
}

div[data-testid="stMetricDelta"] {
    font-size: 11px;
}

.stButton button {
    background: #eeeeea;
    color: #141414;
    border-radius: 10px;
    border: 1px solid #dddddd;
    font-weight: 600;
}

.stButton button:hover {
    background: #cfcfc9;
    color: #111111;
    border: 1px solid #cfcfc9;
}

.stTextInput input, .stNumberInput input,
.stSelectbox div[data-baseweb="select"],
.stMultiSelect div[data-baseweb="select"] {
    background: #222226 !important;
    color: white !important;
}

div[data-testid="stDataFrame"] {
    border: 1px solid #303030;
    border-radius: 10px;
}

div[data-testid="stTabs"] button {
    color: #d1d5db;
}

div[data-testid="stForm"] {
    border: 1px solid #2d2d2d;
    border-radius: 12px;
    padding: 18px;
    background: #191919;
}

.registry-caption {
    color: #999999;
    font-size: 13px;
}

.registry-label {
    font-size: 10px;
    color: #a3a3a3;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}

.registry-card {
    background: #191919;
    border: 1px solid #2a2a2a;
    border-radius: 12px;
    padding: 14px;
}

div[data-testid="stProgress"] > div > div {
    background-color: #ef4444;
}

hr {
    border-color: #292929;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# API FUNCTIONS
# =========================================================
def api_request(method, endpoint, payload=None):

    url = st.session_state.api_url.rstrip("/") + endpoint

    try:
        response = requests.request(
            method,
            url,
            json=payload,
            timeout=10
        )

        if response.status_code == 204:
            return {"message": "Success"}

        try:
            result = response.json()
        except ValueError:
            result = response.text

        if response.ok:
            return result

        if isinstance(result, dict):
            error = result.get("detail", result)
        else:
            error = result

        st.error(f"{response.status_code}: {error}")
        return None

    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to FastAPI.")
        return None

    except requests.exceptions.Timeout:
        st.error("Request timed out.")
        return None

    except requests.exceptions.RequestException as e:
        st.error(str(e))
        return None


def fetch_students():
    result = api_request("GET", "/students")
    if result is None:
        return None
    return pd.DataFrame(result)


def fetch_student(student_id):
    return api_request("GET", f"/students/{student_id}")


def add_activity(action):
    st.session_state.activity.insert(
        0,
        {
            "action": action,
            "time": datetime.now().strftime("%H:%M:%S")
        }
    )


def grade(marks):

    if marks >= 90:
        return "A+"
    elif marks >= 80:
        return "A"
    elif marks >= 70:
        return "B"
    elif marks >= 60:
        return "C"
    elif marks >= 50:
        return "D"
    else:
        return "F"


def grade_color(marks):

    if marks >= 90:
        return "#7dd3a7"
    elif marks >= 80:
        return "#a8d59a"
    elif marks >= 70:
        return "#d6d47c"
    elif marks >= 60:
        return "#e4a45e"
    elif marks >= 50:
        return "#df805b"
    else:
        return "#ef4444"


# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:

    st.markdown("## ‹‹")

    st.markdown(
        "<span class='registry-label'>CONNECTION</span>",
        unsafe_allow_html=True
    )

    st.text_input(
        "API Base URL",
        key="api_url"
    )

    api_url = st.session_state.api_url.rstrip("/")

    try:
        connection = requests.get(
            api_url + "/students",
            timeout=3
        )

        if connection.ok:
            connection_students = connection.json()
            st.success(f"● Connected · {len(connection_students)} students")
        else:
            st.warning("API responding")

    except requests.exceptions.RequestException:
        st.error("● Disconnected")

    if st.button("⟳ Refresh", use_container_width=True):
        st.rerun()

    st.divider()

    st.markdown(
        "<span class='registry-label'>QUICK FIND</span>",
        unsafe_allow_html=True
    )

    quick_find = st.text_input(
        "Quick find",
        placeholder="Name, email or ID",
        label_visibility="collapsed"
    )

    # Load the students for quick find
    quick_data = fetch_students()

    if quick_data is not None and not quick_data.empty:

        quick_df = quick_data.copy()

        if quick_find:

            matching = quick_df[
                quick_df.astype(str).apply(
                    lambda row: row.str.lower().str.contains(
                        quick_find.lower(),
                        na=False
                    ).any(),
                    axis=1
                )
            ]

            if not matching.empty:

                quick_options = matching["id"].tolist()

                quick_choice = st.selectbox(
                    "Matches",
                    quick_options,
                    format_func=lambda x: (
                        str(x) + " · " +
                        matching.loc[
                            matching["id"] == x,
                            "name"
                        ].iloc[0]
                    ),
                    label_visibility="collapsed"
                )

                if st.button("Open profile", use_container_width=True):
                    st.session_state.selected_student_id = quick_choice
                    st.rerun()

            else:
                st.caption("No matching students.")

    st.divider()

    with st.expander("Endpoints used"):

        st.code(
            """
GET     /students
GET     /students/{id}
POST    /students
PUT     /students/{id}
PATCH   /students/{id}
DELETE  /students/{id}
            """,
            language="text"
        )

    st.divider()

    st.caption("STUDENT REGISTRY")
    st.caption("FastAPI · PostgreSQL")


# =========================================================
# FETCH MAIN DATA
# =========================================================
df = fetch_students()


# =========================================================
# HEADER
# =========================================================
header_col1, header_col2 = st.columns([5, 1])

with header_col1:

    st.markdown(
        "<h1>Student <span style='color:#9ac9b6'>Registry</span></h1>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<p class='registry-caption'>"
        "A front desk for your FastAPI student records."
        "</p>",
        unsafe_allow_html=True
    )

with header_col2:

    st.write("")

    create_toggle = st.button(
        "＋ New student",
        use_container_width=True
    )


# =========================================================
# CREATE STUDENT FORM
# =========================================================
if create_toggle:
    st.session_state.show_create = not st.session_state.get(
        "show_create", False
    )

if st.session_state.get("show_create", False):

    with st.expander("Create student", expanded=True):

        with st.form("create_student_form"):

            c1, c2 = st.columns(2)

            with c1:

                new_id = st.number_input(
                    "Student ID",
                    min_value=1,
                    step=1
                )

                new_name = st.text_input("Name")
                new_age = st.number_input(
                    "Age",
                    min_value=10,
                    max_value=100,
                    value=18
                )

                new_department = st.text_input("Course / Department")

            with c2:

                new_semester = st.text_input("Semester")
                new_email = st.text_input("Email")
                new_marks = st.number_input(
                    "Marks",
                    min_value=0.0,
                    max_value=100.0,
                    value=0.0
                )
                new_city = st.text_input("City")

            create_submit = st.form_submit_button(
                "Create student"
            )

            if create_submit:

                payload = {
                    "id": int(new_id),
                    "name": new_name,
                    "age": int(new_age),
                    "department": new_department,
                    "semester": new_semester,
                    "email": new_email,
                    "marks": new_marks,
                    "city": new_city
                }

                result = api_request(
                    "POST",
                    "/students",
                    payload
                )

                if result is not None:

                    st.success(
                        result.get(
                            "message",
                            "Student created"
                        )
                    )

                    add_activity(
                        f"Created student {new_name}"
                    )

                    st.session_state.show_create = False
                    st.rerun()


# =========================================================
# DASHBOARD METRICS
# =========================================================
if df is not None and not df.empty:

    df["grade"] = df["marks"].apply(grade)

    total = len(df)
    average = df["marks"].mean()
    highest = df["marks"].max()
    passing = (df["marks"] >= 60).sum()

    top_student = df.loc[
        df["marks"].idxmax()
    ]

    m1, m2, m3, m4 = st.columns(4)

    m1.metric(
        "STUDENTS",
        total,
        f"across {df['department'].nunique()} courses"
    )

    m2.metric(
        "CLASS AVERAGE",
        f"{average:.1f}",
        f"{passing} of {total} passing (60+)"
    )

    m3.metric(
        "TOP SCORER",
        f"{highest:.0f}",
        top_student["name"] + " · " + top_student["department"]
    )

    with m4:

        st.markdown(
            "<div class='registry-card'>"
            "<span class='registry-label'>GRADE SPREAD</span>"
            "</div>",
            unsafe_allow_html=True
        )

        grade_order = ["A+", "A", "B", "C", "D", "F"]

        grade_counts = df["grade"].value_counts()

        segments = []
        grade_colors = {
    "A+": "#7dd3a7",
    "A": "#a8d59a",
    "B": "#d6d47c",
    "C": "#e4a45e",
    "D": "#df805b",
    "F": "#ef4444"
}

        for g in grade_order:

            count = grade_counts.get(g, 0)

            if count > 0:

                width = (count / total) * 100
                color = grade_colors[g]

                segment = (
            f"<div title='{g}: {count}' "
            f"style='width:{width}%;"
            f"height:10px;"
            f"background:{color};'>"
            f"</div>"
        )

        segments.append(segment)

        st.markdown(
            "<div style='display:flex;overflow:hidden;"
            "border-radius:20px;margin-top:12px;'>"
            + "".join(segments)
            + "</div>",
            unsafe_allow_html=True
        )

        st.caption("A+   A   B   C   D   F")


# =========================================================
# TABS
# =========================================================
tab_roster, tab_insights, tab_activity = st.tabs(
    ["Roster", "Insights", "Activity"]
)


# =========================================================
# ROSTER
# =========================================================
with tab_roster:

    if df is None:

        st.warning("Unable to retrieve records.")

    elif df.empty:

        st.info("No students found.")

    else:

        # Search
        search_col, page_col = st.columns([5, 1])

        with search_col:

            search = st.text_input(
                "Search roster",
                placeholder="⌕  Search by name, email or ID...",
                label_visibility="collapsed",
                key="roster_search"
            )

        with page_col:

            per_page = st.selectbox(
                "Per page",
                [5, 10, 20, 50],
                index=1
            )

        filtered = df.copy()

        # Search filter
        if search:

            filtered = filtered[
                filtered.astype(str).apply(
                    lambda row: row.str.lower().str.contains(
                        search.lower(),
                        na=False
                    ).any(),
                    axis=1
                )
            ]

        # Department filters
        departments = sorted(
            df["department"].unique().tolist()
        )

        selected_departments = st.multiselect(
            "Courses",
            departments,
            placeholder="Filter by course"
        )

        if selected_departments:

            filtered = filtered[
                filtered["department"].isin(
                    selected_departments
                )
            ]

        # Sort controls
        sort_col, order_col, marks_col = st.columns([2, 1, 3])

        with sort_col:

            sort_by = st.selectbox(
                "Sort by",
                ["Marks", "Name", "Age"]
            )

        with order_col:

            sort_order = st.selectbox(
                "Order",
                ["Desc", "Asc"]
            )

        with marks_col:

            mark_range = st.slider(
                "Marks range",
                0,
                100,
                (0, 100)
            )

        filtered = filtered[
            filtered["marks"].between(
                mark_range[0],
                mark_range[1]
            )
        ]

        sort_mapping = {
            "Marks": "marks",
            "Name": "name",
            "Age": "age"
        }

        filtered = filtered.sort_values(
            sort_mapping[sort_by],
            ascending=(sort_order == "Asc")
        )

        # Pagination
        max_page = max(
            1,
            (len(filtered) - 1) // per_page + 1
        )

        page = st.number_input(
            "Page",
            min_value=1,
            max_value=max_page,
            value=1,
            step=1
        )

        start = (page - 1) * per_page
        end = start + per_page

        page_df = filtered.iloc[start:end].copy()

        # Table
        st.markdown(
            "<div class='registry-caption'>"
            f"GET /students · {len(filtered)} records"
            "</div>",
            unsafe_allow_html=True
        )

        display_df = page_df[
            [
                "id",
                "name",
                "department",
                "age",
                "marks",
                "grade"
            ]
        ].copy()

        display_df.columns = [
            "ID",
            "Name",
            "Course",
            "Age",
            "Marks",
            "Grade"
        ]

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )

        st.caption(
            "Choose a student below to open their profile."
        )

        profile_options = filtered["id"].tolist()

        if profile_options:

            profile_id = st.selectbox(
                "Open profile",
                profile_options,
                format_func=lambda x: (
                    str(x) + " · " +
                    filtered.loc[
                        filtered["id"] == x,
                        "name"
                    ].iloc[0]
                ),
                index=(
                    profile_options.index(
                        st.session_state.selected_student_id
                    )
                    if st.session_state.selected_student_id
                    in profile_options
                    else 0
                )
            )

            st.session_state.selected_student_id = profile_id

            selected = filtered[
                filtered["id"] == profile_id
            ].iloc[0]

            # Profile panel
            st.divider()

            p1, p2 = st.columns([2, 1])

            with p1:

                st.subheader(selected["name"])

                st.caption(
                    f"ID: {selected['id']} · "
                    f"{selected['department']} · "
                    f"{selected['semester']}"
                )

                st.markdown("#### Student details")

                detail_df = pd.DataFrame(
                    [
                        {
                            "Email": selected["email"],
                            "Age": selected["age"],
                            "City": selected["city"],
                            "Marks": selected["marks"],
                            "Grade": selected["grade"]
                        }
                    ]
                )

                st.dataframe(
                    detail_df,
                    hide_index=True,
                    use_container_width=True
                )

            with p2:

                st.markdown("#### Performance")

                st.metric(
                    "Marks",
                    selected["marks"]
                )

                st.progress(
                    int(selected["marks"]),
                    text=f"Grade {selected['grade']}"
                )

                if st.button("Load full edit", key="load_edit"):
                    st.session_state.edit_student = selected.to_dict()
                    st.rerun()


# =========================================================
# INSIGHTS
# =========================================================
with tab_insights:

    st.subheader("Class Insights")

    if df is not None and not df.empty:

        i1, i2 = st.columns(2)

        with i1:

            st.markdown("#### Average marks by course")

            dept_average = df.groupby(
                "department"
            )["marks"].mean()

            st.bar_chart(dept_average)

        with i2:

            st.markdown("#### Student count by course")

            dept_count = df["department"].value_counts()

            st.bar_chart(dept_count)

        st.markdown("#### Student marks")

        st.line_chart(
            df.set_index("name")["marks"]
        )

        st.markdown("#### Grade breakdown")

        grade_counts = df["grade"].value_counts()

        st.bar_chart(grade_counts)


# =========================================================
# ACTIVITY
# =========================================================
with tab_activity:

    st.subheader("Recent Activity")

    if not st.session_state.activity:

        st.info(
            "No activity recorded in this session yet."
        )

    else:

        for item in st.session_state.activity:

            st.markdown(
                f"**{item['action']}** "
                f"<span style='color:#999'>{item['time']}</span>",
                unsafe_allow_html=True
            )

            st.divider()


# =========================================================
# FULL EDIT FORM (FROM PROFILE)
# =========================================================
if "edit_student" in st.session_state:

    data = st.session_state.edit_student

    st.divider()

    st.subheader(
        f"✏️ Edit Student · {data['name']}"
    )

    with st.form("full_edit_form"):

        c1, c2 = st.columns(2)

        with c1:

            edit_name = st.text_input(
                "Name",
                value=data["name"]
            )

            edit_age = st.number_input(
                "Age",
                min_value=10,
                max_value=100,
                value=int(data["age"])
            )

            edit_department = st.text_input(
                "Department",
                value=data["department"]
            )

            edit_semester = st.text_input(
                "Semester",
                value=data["semester"]
            )

        with c2:

            edit_email = st.text_input(
                "Email",
                value=data["email"]
            )

            edit_marks = st.number_input(
                "Marks",
                min_value=0.0,
                max_value=100.0,
                value=float(data["marks"])
            )

            edit_city = st.text_input(
                "City",
                value=data["city"]
            )

        save = st.form_submit_button(
            "Save changes"
        )

        if save:

            payload = {
                "name": edit_name,
                "age": int(edit_age),
                "department": edit_department,
                "semester": edit_semester,
                "email": edit_email,
                "marks": edit_marks,
                "city": edit_city
            }

            result = api_request(
                "PUT",
                f"/students/{data['id']}",
                payload
            )

            if result is not None:

                st.success("Student updated.")

                add_activity(
                    f"Updated {edit_name}"
                )

                del st.session_state.edit_student
                st.rerun()


# =========================================================
# DELETE FROM PROFILE
# =========================================================
if "edit_student" in st.session_state:

    data = st.session_state.edit_student

    with st.expander("Danger zone · Delete student"):

        confirm_delete = st.checkbox(
            f"Confirm deletion of {data['name']}"
        )

        if st.button("Delete this student"):

            if not confirm_delete:

                st.warning("Please confirm.")

            else:

                result = api_request(
                    "DELETE",
                    f"/students/{data['id']}"
                )

                if result is not None:

                    add_activity(
                        f"Deleted {data['name']}"
                    )

                    del st.session_state.edit_student
                    st.success("Student deleted.")
                    st.rerun()
