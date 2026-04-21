![Python](https://img.shields.io/badge/Python-3.10-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-App-red)
![Status](https://img.shields.io/badge/Status-Production-green)



🌊 SEACOM Subsea Cable Fault Locator Tool
📌 Overview

The SEACOM Cable Fault Locator Tool is a Streamlit-based application designed to assist Network Operations Center (NOC) teams in quickly identifying subsea cable faults using PFE (Power Feeding Equipment) voltage inputs.

This tool converts electrical measurements into geographical fault locations, enabling faster troubleshooting and reduced downtime.

🚀 Live Demo

👉 https://cable-fault-locator-bynciqsgvd9zvtzyenzdj.streamlit.app/

⚙️ Key Features
🔌 Multi-station support
Mtunzini
Zafarana
Mumbai
Mombasa
Maputo
⚡ Voltage-to-distance fault calculation
📍 Segment & repeater identification
🗺 Interactive subsea cable map
🔴 Dynamic fault location plotting
🌐 Multi-branch cable visualization
🧠 How It Works
User selects:
Cable Landing Station (CLS)
Ground type (Station/Ocean)
PFE Voltage
System calculates:
Distance = (Voltage - Reference Voltage) / 0.64
Maps fault distance to:
Cable segment
Repeater location
Geographic coordinates
Displays:
Fault summary
Interactive map with marker
🗂 Data Sources
1. Electrical Data

Contains:

PFE voltage references
Segment mapping
Repeater details
Distance from CLS
2. Cable Route Data

Contains:

Latitude/Longitude per repeater
Distance from each landing station
Multi-branch topology
🛠 Tech Stack
Python
Streamlit
Pandas
Plotly
📊 System Architecture

User Input → Data Processing → Fault Calculation → Coordinate Mapping → Visualization

⚠️ Challenges Solved
CSV encoding issues
Multi-station data normalization
Incorrect map plotting (straight-line issue)
Fault marker accuracy
Dynamic column handling
📈 Business Impact
Reduces fault localization time
Eliminates manual calculations
Improves NOC efficiency
Enables visual fault analysis
🔮 Future Enhancements
NMS (Zabbix) integration
Automated fault alerts
Dual-end fault triangulation
Historical fault analytics
👤 Author

Dibakar Halder
Subsea NOC Head | Telecom & Submarine Cable Specialist

📜 License

This project is for educational and operational improvement purposes.
