# 🎫 Help Desk Ticketing Simulation System

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python)
![Database](https://img.shields.io/badge/Database-SQLite-lightblue?style=flat-square)
![CLI](https://img.shields.io/badge/Interface-CLI-orange?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

> A command-line IT support ticketing system built in Python + SQLite — simulating real-world help desk workflows including ticket creation, assignment, escalation, and resolution tracking.

---

## 🎯 What It Does

This project mimics how enterprise ticketing tools like **Jira Service Desk** and **ServiceNow** work under the hood:

- 📝 **Create** support tickets with title, description, and priority
- 👤 **Assign** tickets to agents
- 🔼 **Escalate** ticket priority (Low → Medium → High → Critical)
- ✅ **Resolve & close** tickets with resolution notes
- 📋 **View all open tickets** in a formatted table
- 🔍 **Search** tickets by ID, status, or priority

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python 3 | Core logic & CLI interface |
| SQLite3 | Persistent ticket storage |
| `tabulate` | Pretty-print ticket tables |
| `datetime` | Timestamps on all actions |

---

## 🚀 Getting Started

```bash
# 1. Clone the repo
git clone https://github.com/OmSutaria/helpdesk-ticket-system.git

# 2. Navigate into the folder
cd helpdesk-ticket-system

# 3. Install the one dependency
pip install tabulate

# 4. Run the system
python helpdesk.py
```

---

## 📂 Project Structure

```
helpdesk-ticket-system/
│
├── helpdesk.py         # Main CLI app & menu logic
├── database.py         # SQLite setup & all DB queries
├── ticket.py           # Ticket class & business logic
├── tickets.db          # Auto-created SQLite database
└── README.md
```

---

## 🖥️ Example Usage

```
===========================
   HELP DESK SYSTEM MENU
===========================
[1] Create New Ticket
[2] View All Open Tickets
[3] Assign Ticket
[4] Escalate Priority
[5] Resolve Ticket
[6] Search Tickets
[0] Exit
---------------------------
Select option: 1

Enter ticket title: Laptop not connecting to VPN
Enter description: User unable to connect since this morning
Select priority [Low/Medium/High]: High

✅ Ticket #1042 created successfully!
   Status: Open | Priority: High | Assigned: Unassigned
```

---

## 📊 Ticket Status Workflow

```
[Open] ──► [In Progress] ──► [Resolved] ──► [Closed]
              │
              └──► [Escalated] ──► [In Progress]
```

---

## 💡 Key Learning Outcomes

- Relational database design (tickets, agents, comments tables)
- CRUD operations with Python's `sqlite3` module
- OOP design using a `Ticket` class
- CLI menu navigation and input validation
- Workflow state management

---

## 👤 Author

**Om M. Sutaria**
📧 omsutaria.om@gmail.com | 🔗 [GitHub](https://github.com/OmSutaria)

---

## 📜 License

MIT License — free to use and adapt.
