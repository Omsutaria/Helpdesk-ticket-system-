"""
=====================================================
  Help Desk Ticketing System — Database Layer
  Author : Om M. Sutaria
  GitHub : https://github.com/OmSutaria/helpdesk-ticket-system
=====================================================
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "tickets.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_db():
    """Create tables if they don't exist."""
    conn = get_connection()
    cur  = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS agents (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            name     TEXT NOT NULL UNIQUE,
            email    TEXT,
            active   INTEGER DEFAULT 1
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT NOT NULL,
            description TEXT,
            priority    TEXT NOT NULL DEFAULT 'Medium',
            status      TEXT NOT NULL DEFAULT 'Open',
            agent_id    INTEGER,
            created_at  TEXT NOT NULL,
            updated_at  TEXT NOT NULL,
            resolved_at TEXT,
            resolution  TEXT,
            FOREIGN KEY (agent_id) REFERENCES agents(id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id  INTEGER NOT NULL,
            author     TEXT NOT NULL,
            body       TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (ticket_id) REFERENCES tickets(id)
        )
    """)

    # Seed some default agents
    cur.execute("SELECT COUNT(*) FROM agents")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO agents (name, email) VALUES (?, ?)",
            [
                ("Om Sutaria",   "omsutaria.om@gmail.com"),
                ("Alice Smith",  "alice@company.com"),
                ("Bob Johnson",  "bob@company.com"),
                ("Unassigned",   None),
            ]
        )

    conn.commit()
    conn.close()


# ── TICKET CRUD ─────────────────────────────────────────────

def create_ticket(title, description, priority):
    from datetime import datetime
    now  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("""
        INSERT INTO tickets (title, description, priority, status, created_at, updated_at)
        VALUES (?, ?, ?, 'Open', ?, ?)
    """, (title, description, priority, now, now))
    ticket_id = cur.lastrowid
    conn.commit()
    conn.close()
    return ticket_id


def get_all_tickets(status_filter=None):
    conn = get_connection()
    cur  = conn.cursor()
    if status_filter:
        cur.execute("""
            SELECT t.*, a.name AS agent_name
            FROM tickets t LEFT JOIN agents a ON t.agent_id = a.id
            WHERE t.status = ? ORDER BY t.id DESC
        """, (status_filter,))
    else:
        cur.execute("""
            SELECT t.*, a.name AS agent_name
            FROM tickets t LEFT JOIN agents a ON t.agent_id = a.id
            ORDER BY t.id DESC
        """)
    rows = cur.fetchall()
    conn.close()
    return rows


def get_ticket(ticket_id):
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("""
        SELECT t.*, a.name AS agent_name
        FROM tickets t LEFT JOIN agents a ON t.agent_id = a.id
        WHERE t.id = ?
    """, (ticket_id,))
    row = cur.fetchone()
    conn.close()
    return row


def assign_ticket(ticket_id, agent_id):
    from datetime import datetime
    now  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("""
        UPDATE tickets SET agent_id=?, status='In Progress', updated_at=?
        WHERE id=?
    """, (agent_id, now, ticket_id))
    conn.commit()
    conn.close()


def escalate_ticket(ticket_id):
    from datetime import datetime
    now  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    priority_map = {"Low": "Medium", "Medium": "High", "High": "Critical", "Critical": "Critical"}
    ticket = get_ticket(ticket_id)
    if not ticket:
        return None
    new_priority = priority_map.get(ticket["priority"], "Critical")
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("""
        UPDATE tickets SET priority=?, status='Escalated', updated_at=? WHERE id=?
    """, (new_priority, now, ticket_id))
    conn.commit()
    conn.close()
    return new_priority


def resolve_ticket(ticket_id, resolution_note):
    from datetime import datetime
    now  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("""
        UPDATE tickets SET status='Resolved', resolution=?, resolved_at=?, updated_at=?
        WHERE id=?
    """, (resolution_note, now, now, ticket_id))
    conn.commit()
    conn.close()


def close_ticket(ticket_id):
    from datetime import datetime
    now  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("UPDATE tickets SET status='Closed', updated_at=? WHERE id=?", (now, ticket_id))
    conn.commit()
    conn.close()


def add_comment(ticket_id, author, body):
    from datetime import datetime
    now  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("""
        INSERT INTO comments (ticket_id, author, body, created_at)
        VALUES (?, ?, ?, ?)
    """, (ticket_id, author, body, now))
    conn.commit()
    conn.close()


def get_comments(ticket_id):
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("SELECT * FROM comments WHERE ticket_id=? ORDER BY id", (ticket_id,))
    rows = cur.fetchall()
    conn.close()
    return rows


def get_agents():
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("SELECT * FROM agents WHERE active=1 ORDER BY id")
    rows = cur.fetchall()
    conn.close()
    return rows


def search_tickets(query):
    conn = get_connection()
    cur  = conn.cursor()
    like = f"%{query}%"
    cur.execute("""
        SELECT t.*, a.name AS agent_name
        FROM tickets t LEFT JOIN agents a ON t.agent_id = a.id
        WHERE t.title LIKE ? OR t.description LIKE ? OR t.status LIKE ? OR t.priority LIKE ?
        ORDER BY t.id DESC
    """, (like, like, like, like))
    rows = cur.fetchall()
    conn.close()
    return rows


def get_stats():
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("SELECT status, COUNT(*) as cnt FROM tickets GROUP BY status")
    status_counts = {row["status"]: row["cnt"] for row in cur.fetchall()}
    cur.execute("SELECT priority, COUNT(*) as cnt FROM tickets GROUP BY priority")
    priority_counts = {row["priority"]: row["cnt"] for row in cur.fetchall()}
    cur.execute("SELECT COUNT(*) as total FROM tickets")
    total = cur.fetchone()["total"]
    conn.close()
    return {"total": total, "by_status": status_counts, "by_priority": priority_counts}
