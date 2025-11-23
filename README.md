Student Management System

A Python-based Student Management System using OOP architecture and a Streamlit UI. Supports full CRUD, persistent storage (JSON + CSV), filters, and attendance tracking with visual dashboards.

Core Features

 OOP Design

   Student class (info + courses + attendance)
   Manager class (CRUD + search + list)
   DataStorage (save/load from JSON & CSV)

 CRUD Operations

   Add, update, delete, list students
   Input validation + error handling

 Data Storage

   JSON (main store)
   CSV auto-generated
   Courses stored as arrays (JSON) / strings (CSV)

 Search & Filters

   By name (partial)
   By grade
   By age
   By performance/attendance

 Streamlit UI

   Forms, alerts, tables
   Dashboard metrics
   Graphs via Plotly

Dashboard Highlights

 Grade distribution pie chart

 Attendance bars:

   90–100% (Good)
   75–89% (Average)
   < 75% flagged 🔴

 Low attendance warnings across UI

Enhanced Delete Flow

 Detailed student preview before deletion
 Confirmation step (not one-click)
 Success/cancel messages

This avoids accidental data loss.

Project Structure

Hackathon/
├── app.py
├── students.json
├── students.csv
├── Test.ipynb (for Test Only)
└── README.md

Running the App

powershell
pip install streamlit plotly
streamlit run app.py

Default URL: 'http://localhost:8501'

Customization

To add new student fields:

 Update `Student.__init__`
 Update `to_dict()`
 Update Streamlit forms

Requirements

 Python 3.7+
 streamlit + plotly
 json, csv, datetime, os