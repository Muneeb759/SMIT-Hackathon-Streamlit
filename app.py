import streamlit as st
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from models import Student
from services import Manager, DataStorage


# Initialize session state
if 'manager' not in st.session_state:
    st.session_state.manager = Manager()
    st.session_state.storage = DataStorage()
    st.session_state.storage.load_from_json(st.session_state.manager)

# Page configuration
st.set_page_config(
    page_title="Student Management System",
    page_icon="🎓",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #2E86AB;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    .student-card {
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2E86AB;
        margin-bottom: 1rem;
        background-color: #f8f9fa;
    }
    .low-attendance {
        color: #dc3545;
        font-weight: bold;
    }
    .good-attendance {
        color: #28a745;
        font-weight: bold;
    }
    .excellent-attendance {
        color: #007bff;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("<h1 class='main-header'>🎓 Student Management System</h1>", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("Navigation")
menu = st.sidebar.radio(
    "Select Operation",
    ["Dashboard", "Add Student", "View Students", "Update Student", "Delete Student", "Manage Attendance", "Search & Filter"]
)

# Dashboard
if menu == "Dashboard":
    st.header("Dashboard")
    
    students = st.session_state.manager.list_students()
    
    # Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Students", len(students))
    
    with col2:
        grade_a = len([s for s in students if s.grade == 'A'])
        st.metric("Grade A Students", grade_a)
    
    with col3:
        avg_age = sum([s.age for s in students]) / len(students) if students else 0
        st.metric("Average Age", f"{avg_age:.1f}")
    
    with col4:
        low_attendance = len([s for s in students if s.attendance < 75])
        st.metric("Low Attendance", low_attendance, delta=None, delta_color="inverse")
    
    # Graphs Row
    if students:
        st.markdown("---")
        st.subheader("Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Grade Distribution Pie Chart
            grade_counts = {}
            for student in students:
                grade_counts[student.grade] = grade_counts.get(student.grade, 0) + 1
            
            # Ensure all grades are represented
            for grade in ['A', 'B', 'C', 'D', 'E', 'F']:
                if grade not in grade_counts:
                    grade_counts[grade] = 0
            
            fig_pie = px.pie(
                values=list(grade_counts.values()),
                names=list(grade_counts.keys()),
                title="Grade Distribution",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label+value')
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Attendance Bar Chart
            attendance_ranges = {
                '90-100%': len([s for s in students if s.attendance >= 90]),
                '75-89%': len([s for s in students if 75 <= s.attendance < 90]),
                'Below 75%': len([s for s in students if s.attendance < 75])
            }
            
            fig_bar = go.Figure(data=[
                go.Bar(
                    x=list(attendance_ranges.keys()),
                    y=list(attendance_ranges.values()),
                    marker_color=['#28a745', '#ffc107', '#dc3545'],
                    text=list(attendance_ranges.values()),
                    textposition='auto'
                )
            ])
            fig_bar.update_layout(
                title="Attendance Distribution",
                xaxis_title="Attendance Range",
                yaxis_title="Number of Students",
                showlegend=False
            )
            st.plotly_chart(fig_bar, use_container_width=True)
    
    st.markdown("---")
    st.subheader("👥 Recent Students")
    if students:
        for student in students[-5:]:
            # Check if attendance is low
            attendance_color = "🔴" if student.attendance < 75 else "🟢"
            
            with st.expander(f"{attendance_color} {student.name} ({student.student_id})"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"Age: {student.age}")
                    st.write(f"Grade: {student.grade}")
                    st.write(f"Email: {student.email}")
                with col2:
                    st.write(f"Phone: {student.phone}")
                    st.write(f"Attendance: {student.attendance}%")
                    st.write(f"Courses: {', '.join(student.courses) if student.courses else 'None'}")
                
                if student.attendance < 75:
                    st.error(f"Low Attendance Alert: {student.attendance}%")
    else:
        st.info("No students in the system yet.")

# Add Student
elif menu == "Add Student":
    st.header("➕ Add New Student")
    
    with st.form("add_student_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            student_id = st.text_input("Student ID*", placeholder="e.g., S001")
            name = st.text_input("Full Name*", placeholder="e.g., John Doe", help="Only letters and spaces allowed")
            age = st.number_input("Age*", min_value=1, max_value=100, value=20)
        
        with col2:
            grade = st.selectbox("Grade*", ["A", "B", "C", "D", "E", "F"])
            email = st.text_input("Email*", placeholder="student@email.com", help="Must be a valid email format")
            phone = st.text_input("Phone*", placeholder="0300-1234567", help="10-15 digits only, no alphabets")
        
        attendance = st.slider("Attendance %", min_value=0.0, max_value=100.0, value=100.0, step=0.1)
        courses = st.text_input("Courses (comma-separated)", placeholder="Math, Physics, Chemistry")
        
        submitted = st.form_submit_button("➕ Add Student", type="primary")
        
        if submitted:
            if not all([student_id, name, email, phone]):
                st.error("❌ Please fill all required fields marked with *")
            else:
                try:
                    student = Student(student_id, name, age, grade, email, phone, attendance)
                    if courses:
                        for course in courses.split(','):
                            student.add_course(course.strip())
                    
                    success, message = st.session_state.manager.add_student(student)
                    
                    if success:
                        st.session_state.storage.save_to_json(st.session_state.manager)
                        
                        @st.dialog("✅ Success!")
                        def show_success():
                            st.success(f"Student {name} added successfully!")
                            st.balloons()
                            if st.button("Close", type="primary"):
                                st.rerun()
                        
                        show_success()
                    else:
                        st.error(f"❌ {message}")
                except ValueError as e:
                    st.error(f"❌ Validation Error: {str(e)}")

# View Students
elif menu == "View Students":
    st.header("👥 All Students")
    
    students = st.session_state.manager.list_students()
    
    if students:
        st.write(f"Total: {len(students)} students")
        
        # Create a table
        for student in students:
            # Determine attendance status and color
            if student.attendance < 75:
                attendance_icon = "🔴"
                attendance_class = "low-attendance"
                name_color = "#dc3545"
            elif student.attendance >= 90:
                attendance_icon = "🟢"
                attendance_class = "excellent-attendance"
                name_color = "#007bff"
            else:
                attendance_icon = "🟡"
                attendance_class = "good-attendance"
                name_color = "#28a745"
            
            st.markdown(f"""
                <div class="student-card">
                    <strong style="color: {name_color}; font-size: 1.1em;">{attendance_icon} {student.name}</strong>
                    <span style="color: #6c757d;"> (ID: {student.student_id})</span>
                    <br>
                    <span style="color: #495057;">Age: {student.age} | Grade: {student.grade}</span> | 
                    <span class="{attendance_class}">Attendance: {student.attendance}%</span>
                    <br>
                    📧 <span style="color: #495057;">{student.email}</span> | 
                    📞 <span style="color: #495057;">{student.phone}</span>
                    <br>
                    📚 <span style="color: #495057;">Courses: {', '.join(student.courses) if student.courses else 'None'}</span>
                    {f'<br><span class="low-attendance">⚠️ LOW ATTENDANCE WARNING</span>' if student.attendance < 75 else ''}
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No students found in the system.")

# Update Student
elif menu == "Update Student":
    st.header("✏️ Update Student")
    
    students = st.session_state.manager.list_students()
    
    if students:
        student_options = {f"{s.student_id} - {s.name}": s.student_id for s in students}
        selected = st.selectbox("Select Student to Update", list(student_options.keys()))
        
        if selected:
            student_id = student_options[selected]
            student = st.session_state.manager.get_student(student_id)
            
            with st.form("update_student_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    name = st.text_input("Full Name", value=student.name, help="Only letters and spaces allowed")
                    age = st.number_input("Age", min_value=1, max_value=100, value=student.age)
                
                with col2:
                    grade = st.selectbox("Grade", ["A", "B", "C", "D", "E", "F"], 
                                       index=["A", "B", "C", "D", "E", "F"].index(student.grade))
                    email = st.text_input("Email", value=student.email, help="Must be a valid email format")
                
                phone = st.text_input("Phone", value=student.phone, help="10-15 digits only, no alphabets")
                attendance = st.slider("Attendance %", min_value=0.0, max_value=100.0, 
                                     value=student.attendance, step=0.1)
                courses = st.text_input("Courses (comma-separated)", value=', '.join(student.courses))
                
                submitted = st.form_submit_button("✏️ Update Student", type="primary")
                
                if submitted:
                    try:
                        # Validate inputs before updating
                        # Create a temporary student object to validate
                        temp_student = Student(student_id, name, age, grade, email, phone, attendance)
                        
                        # Update courses
                        student.courses = [c.strip() for c in courses.split(',') if c.strip()]
                        
                        success, message = st.session_state.manager.update_student(
                            student_id,
                            name=name,
                            age=age,
                            grade=grade,
                            email=email,
                            phone=phone,
                            attendance=attendance
                        )
                        
                        if success:
                            st.session_state.storage.save_to_json(st.session_state.manager)
                            
                            @st.dialog("✅ Success!")
                            def show_success():
                                st.success(f"Student {name} updated successfully!")
                                st.balloons()
                                if st.button("Close", type="primary"):
                                    st.rerun()
                            
                            show_success()
                        else:
                            st.error(f"❌ {message}")
                    except ValueError as e:
                        st.error(f"❌ Validation Error: {str(e)}")
    else:
        st.info("No students available to update.")

# Delete Student
elif menu == "Delete Student":
    st.header("🗑️ Delete Student")
    
    students = st.session_state.manager.list_students()
    
    if students:
        student_options = {f"{s.student_id} - {s.name}": s.student_id for s in students}
        selected = st.selectbox("Select Student to Delete", list(student_options.keys()))
        
        if selected:
            student_id = student_options[selected]
            student = st.session_state.manager.get_student(student_id)
            
            @st.dialog("⚠️ Confirm Delete Student")
            def delete_student_dialog(student_to_delete):
                st.error("**WARNING: Are you sure you want to delete this student?**")
                st.warning("This action cannot be undone!")
                
                # Show student details in a nice format
                st.markdown("---")
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Name:** {student_to_delete.name}")
                    st.write(f"**ID:** {student_to_delete.student_id}")
                    st.write(f"**Age:** {student_to_delete.age}")
                with col2:
                    st.write(f"**Grade:** {student_to_delete.grade}")
                    st.write(f"**Email:** {student_to_delete.email}")
                    st.write(f"**Attendance:** {student_to_delete.attendance}%")
                
                st.markdown("---")
                
                # Confirmation buttons
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🗑️ Yes, Delete Student", type="primary", use_container_width=True):
                        success, message = st.session_state.manager.delete_student(student_to_delete.student_id)
                        
                        if success:
                            st.session_state.storage.save_to_json(st.session_state.manager)
                            st.success(f"✅ {message}")
                            st.info(f"Student {student_to_delete.name} has been removed from the system.")
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
                
                with col2:
                    if st.button("❌ Cancel", use_container_width=True):
                        st.rerun()
            
            st.write("Click the button below to delete this student.")
            if st.button("🗑️ Delete Student", type="primary"):
                delete_student_dialog(student)
    else:
        st.info("No students available to delete.")

# Manage Attendance
elif menu == "Manage Attendance":
    st.header("📊 Manage Attendance")
    
    students = st.session_state.manager.list_students()
    
    if students:
        st.subheader("Bulk Attendance Update")
        
        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            filter_option = st.selectbox("Filter Students", 
                                        ["All Students", "Low Attendance (<75%)", "Good Attendance (≥75%)"])
        with col2:
            sort_option = st.selectbox("Sort By", 
                                      ["Name (A-Z)", "Attendance (Low to High)", "Attendance (High to Low)"])
        
        # Apply filters
        if filter_option == "Low Attendance (<75%)":
            filtered_students = [s for s in students if s.attendance < 75]
        elif filter_option == "Good Attendance (≥75%)":
            filtered_students = [s for s in students if s.attendance >= 75]
        else:
            filtered_students = students
        
        # Apply sorting
        if sort_option == "Name (A-Z)":
            filtered_students.sort(key=lambda s: s.name)
        elif sort_option == "Attendance (Low to High)":
            filtered_students.sort(key=lambda s: s.attendance)
        else:  # High to Low
            filtered_students.sort(key=lambda s: s.attendance, reverse=True)
        
        st.write(f"Showing {len(filtered_students)} student(s)")
        st.markdown("---")
        
        # Display students with attendance management
        for student in filtered_students:
            # Determine attendance status and color (text only, no background)
            if student.attendance < 75:
                attendance_icon = "🔴"
                text_color = "#dc3545"
                attendance_class = "low-attendance"
            elif student.attendance >= 90:
                attendance_icon = "🟢"
                text_color = "#007bff"
                attendance_class = "excellent-attendance"
            else:
                attendance_icon = "🟡"
                text_color = "#28a745"
                attendance_class = "good-attendance"
            
            col1, col2, col3 = st.columns([3, 2, 2])
            
            with col1:
                st.markdown(f"""
                    <div style="padding: 10px; border-radius: 5px; border-left: 4px solid {text_color};">
                        <strong style="color: {text_color};">{attendance_icon} {student.name}</strong>
                        <br><small style="color: #6c757d;">ID: {student.student_id} | Grade: {student.grade}</small>
                    </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                    <div style="padding: 10px; border-radius: 5px; text-align: center;">
                        <strong class="{attendance_class}" style="color: {text_color};">Attendance: {student.attendance}%</strong>
                    </div>
                """, unsafe_allow_html=True)
            
            with col3:
                new_attendance = st.number_input(
                    "New %", 
                    min_value=0.0, 
                    max_value=100.0, 
                    value=student.attendance,
                    step=0.1,
                    key=f"att_{student.student_id}",
                    label_visibility="collapsed"
                )
                if st.button("✏️ Update", key=f"btn_{student.student_id}"):
                    success, message = st.session_state.manager.update_student(
                        student.student_id,
                        attendance=new_attendance
                    )
                    
                    if success:
                        st.session_state.storage.save_to_json(st.session_state.manager)
                        
                        @st.dialog("✅ Attendance Updated!")
                        def show_success():
                            st.success(f"{student.name}'s attendance updated to {new_attendance}%")
                            if st.button("Close", type="primary"):
                                st.rerun()
                        
                        show_success()
                    else:
                        st.error(f"❌ {message}")
            
            st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)
        
        # Bulk operations
        st.markdown("---")
        st.subheader("Bulk Operations")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Mark all as present (100%)**")
            if st.button("✅ Set All to 100%", use_container_width=True):
                for student in st.session_state.manager.list_students():
                    st.session_state.manager.update_student(student.student_id, attendance=100.0)
                st.session_state.storage.save_to_json(st.session_state.manager)
                
                @st.dialog("✅ Bulk Update Complete!")
                def show_bulk_success():
                    st.success("All students marked as 100% attendance!")
                    st.balloons()
                    if st.button("Close", type="primary"):
                        st.rerun()
                
                show_bulk_success()
        
        with col2:
            custom_value = st.number_input("Set custom attendance % for all", 
                                          min_value=0.0, max_value=100.0, value=100.0, step=0.1)
            if st.button(f"📝 Set All to {custom_value}%", use_container_width=True):
                for student in st.session_state.manager.list_students():
                    st.session_state.manager.update_student(student.student_id, attendance=custom_value)
                st.session_state.storage.save_to_json(st.session_state.manager)
                
                @st.dialog("✅ Bulk Update Complete!")
                def show_bulk_custom_success():
                    st.success(f"All students set to {custom_value}% attendance!")
                    st.balloons()
                    if st.button("Close", type="primary"):
                        st.rerun()
                
                show_bulk_custom_success()
    else:
        st.info("No students in the system yet.")

# Search & Filter
elif menu == "Search & Filter":
    st.header("🔍 Search & Filter Students")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_name = st.text_input("Search by Name")
    
    with col2:
        search_grade = st.selectbox("Filter by Grade", ["All", "A", "B", "C", "D", "F"])
    
    with col3:
        search_age = st.number_input("Filter by Age (0 for all)", min_value=0, max_value=100, value=0)
    
    # Build filter
    filters = {}
    if search_name:
        filters['name'] = search_name
    if search_grade != "All":
        filters['grade'] = search_grade
    if search_age > 0:
        filters['age'] = search_age
    
    if filters:
        results = st.session_state.manager.search_students(**filters)
    else:
        results = st.session_state.manager.list_students()
    
    st.subheader(f"Results: {len(results)} students found")
    
    if results:
        for student in results:
            # Check attendance for color coding
            if student.attendance < 75:
                attendance_indicator = "🔴"
                name_style = 'style="color: #dc3545; font-weight: bold;"'
            elif student.attendance >= 90:
                attendance_indicator = "🟢"
                name_style = 'style="color: #007bff; font-weight: bold;"'
            else:
                attendance_indicator = "🟡"
                name_style = 'style="color: #28a745; font-weight: bold;"'
            
            with st.expander(f"{attendance_indicator} {student.name} ({student.student_id})"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Age:** {student.age}")
                    st.write(f"**Grade:** {student.grade}")
                    st.write(f"**Email:** {student.email}")
                with col2:
                    st.write(f"**Phone:** {student.phone}")
                    if student.attendance < 75:
                        st.markdown(f'**Attendance:** <span style="color: #dc3545; font-weight: bold;">{student.attendance}%</span>', unsafe_allow_html=True)
                    elif student.attendance >= 90:
                        st.markdown(f'**Attendance:** <span style="color: #007bff; font-weight: bold;">{student.attendance}%</span>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'**Attendance:** <span style="color: #28a745; font-weight: bold;">{student.attendance}%</span>', unsafe_allow_html=True)
                    st.write(f"**Courses:** {', '.join(student.courses) if student.courses else 'None'}")
                
                if student.attendance < 75:
                    st.markdown('<p style="color: #dc3545; font-weight: bold;">⚠️ Low Attendance Alert</p>', unsafe_allow_html=True)
    else:
        st.info("No students match the search criteria.")

# Footer
st.sidebar.markdown("---")
st.sidebar.info(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
st.sidebar.success(f"Total students in database: {len(st.session_state.manager.list_students())}")
