"""
=====================================================
  Help Desk Ticketing System — Main Application
  Author : Om M. Sutaria
  GitHub : https://github.com/OmSutaria/helpdesk-ticket-system
=====================================================
  A fully working CLI-based IT help desk ticketing system
  built with Python + SQLite.

  Simulates enterprise workflows like Jira Service Desk
  and ServiceNow:
    Open → In Progress → Escalated → Resolved → Closed

  Run: python helpdesk.py
=====================================================
"""

import os
import sys
from database import (
    initialize_db, create_ticket, get_all_tickets, get_ticket,
    assign_ticket, escalate_ticket, resolve_ticket, close_ticket,
    add_comment, get_comments, get_agents, search_tickets, get_stats
)

# ── COLOURS (ANSI) ───────────────────────────────────────────
class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    CYAN   = "\033[96m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    RED    = "\033[91m"
    GRAY   = "\033[90m"
    WHITE  = "\033[97m"
    BLUE   = "\033[94m"

# Windows doesn't support ANSI by default — detect and disable
if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.kernel32.SetConsoleMode(
            ctypes.windll.kernel32.GetStdHandle(-11), 7)
    except Exception:
        for attr in vars(C):
            if not attr.startswith("_"):
                setattr(C, attr, "")


# ── DISPLAY HELPERS ─────────────────────────────────────────
PRIORITY_COLOR = {
    "Low":      C.GREEN,
    "Medium":   C.YELLOW,
    "High":     C.RED,
    "Critical": C.RED + C.BOLD,
}
STATUS_COLOR = {
    "Open":        C.CYAN,
    "In Progress": C.YELLOW,
    "Escalated":   C.RED,
    "Resolved":    C.GREEN,
    "Closed":      C.GRAY,
}

def clr(text, color):
    return f"{color}{text}{C.RESET}"

def header(title):
    print(f"\n{C.BLUE}{'═' * 55}{C.RESET}")
    print(f"{C.BOLD}{C.WHITE}  {title}{C.RESET}")
    print(f"{C.BLUE}{'═' * 55}{C.RESET}\n")

def divider():
    print(f"{C.GRAY}{'─' * 55}{C.RESET}")

def success(msg): print(f"\n  {C.GREEN}✔  {msg}{C.RESET}\n")
def error(msg):   print(f"\n  {C.RED}✘  {msg}{C.RESET}\n")
def info(msg):    print(f"\n  {C.CYAN}ℹ  {msg}{C.RESET}\n")

def pause():
    input(f"\n  {C.GRAY}Press Enter to continue...{C.RESET}")


# ── TICKET DISPLAY ───────────────────────────────────────────
def print_ticket_row(t, index=None):
    prefix  = f"  [{index}]  " if index is not None else "  "
    p_color = PRIORITY_COLOR.get(t["priority"], C.WHITE)
    s_color = STATUS_COLOR.get(t["status"], C.WHITE)
    agent   = t["agent_name"] or "Unassigned"
    print(
        f"{prefix}"
        f"#{clr(str(t['id']).zfill(4), C.BOLD)}  "
        f"{clr(t['priority'][:4], p_color):<16}  "
        f"{clr(t['status'], s_color):<22}  "
        f"{clr(agent, C.CYAN):<18}  "
        f"{t['title'][:38]}"
    )

def print_ticket_detail(t):
    p_color = PRIORITY_COLOR.get(t["priority"], C.WHITE)
    s_color = STATUS_COLOR.get(t["status"], C.WHITE)
    print(f"\n  {C.BOLD}Ticket #{str(t['id']).zfill(4)}{C.RESET}")
    divider()
    print(f"  Title       : {C.WHITE}{t['title']}{C.RESET}")
    print(f"  Priority    : {clr(t['priority'], p_color)}")
    print(f"  Status      : {clr(t['status'], s_color)}")
    print(f"  Assigned To : {clr(t['agent_name'] or 'Unassigned', C.CYAN)}")
    print(f"  Created     : {C.GRAY}{t['created_at']}{C.RESET}")
    print(f"  Updated     : {C.GRAY}{t['updated_at']}{C.RESET}")
    if t["resolved_at"]:
        print(f"  Resolved    : {C.GRAY}{t['resolved_at']}{C.RESET}")
    print(f"\n  {C.BOLD}Description:{C.RESET}")
    print(f"  {t['description'] or '(none)'}")
    if t["resolution"]:
        print(f"\n  {C.BOLD}Resolution Note:{C.RESET}")
        print(f"  {C.GREEN}{t['resolution']}{C.RESET}")

    comments = get_comments(t["id"])
    if comments:
        print(f"\n  {C.BOLD}Comments ({len(comments)}):{C.RESET}")
        for c in comments:
            print(f"  {C.GRAY}[{c['created_at']}]  {clr(c['author'], C.CYAN)}{C.RESET}: {c['body']}")
    divider()


# ── MENU ACTIONS ─────────────────────────────────────────────
def menu_create():
    header("CREATE NEW TICKET")
    title = input("  Title (required): ").strip()
    if not title:
        error("Title cannot be empty.")
        return
    desc = input("  Description     : ").strip()
    print(f"\n  Priority options: {clr('Low', C.GREEN)} / {clr('Medium', C.YELLOW)} / {clr('High', C.RED)} / {clr('Critical', C.RED + C.BOLD)}")
    priority = input("  Priority [Medium]: ").strip().capitalize() or "Medium"
    if priority not in ("Low", "Medium", "High", "Critical"):
        priority = "Medium"

    tid = create_ticket(title, desc, priority)
    success(f"Ticket #{str(tid).zfill(4)} created  |  Priority: {priority}  |  Status: Open")


def menu_view_all():
    header("ALL TICKETS")
    print(f"  Filter: {clr('1', C.CYAN)} All   {clr('2', C.CYAN)} Open   {clr('3', C.CYAN)} In Progress   {clr('4', C.CYAN)} Resolved   {clr('5', C.CYAN)} Closed")
    choice = input("  Choose filter [1]: ").strip() or "1"
    filters = {"1": None, "2": "Open", "3": "In Progress", "4": "Resolved", "5": "Closed"}
    f = filters.get(choice, None)
    tickets = get_all_tickets(f)
    if not tickets:
        info("No tickets found.")
        return
    print(f"\n  {'#ID':<8}{'PRIORITY':<14}{'STATUS':<22}{'ASSIGNED TO':<20}TITLE")
    divider()
    for t in tickets:
        print_ticket_row(t)
    print(f"\n  {C.GRAY}Total: {len(tickets)} ticket(s){C.RESET}")


def menu_view_ticket():
    header("VIEW TICKET DETAIL")
    tid = input("  Enter Ticket ID: ").strip()
    if not tid.isdigit():
        error("Invalid ID.")
        return
    t = get_ticket(int(tid))
    if not t:
        error(f"Ticket #{tid} not found.")
        return
    print_ticket_detail(t)
    print(f"\n  {clr('C', C.CYAN)} Add comment   {clr('Enter', C.GRAY)} Back")
    cmd = input("  > ").strip().upper()
    if cmd == "C":
        author = input("  Your name: ").strip() or "Agent"
        body   = input("  Comment  : ").strip()
        if body:
            add_comment(int(tid), author, body)
            success("Comment added.")


def menu_assign():
    header("ASSIGN TICKET")
    tid = input("  Ticket ID: ").strip()
    if not tid.isdigit():
        error("Invalid ID.")
        return
    t = get_ticket(int(tid))
    if not t:
        error(f"Ticket #{tid} not found.")
        return
    print(f"  Ticket: {C.WHITE}{t['title']}{C.RESET}  |  Current agent: {t['agent_name'] or 'Unassigned'}\n")

    agents = get_agents()
    for i, a in enumerate(agents, 1):
        print(f"  [{i}]  {a['name']}")
    choice = input("\n  Select agent number: ").strip()
    if not choice.isdigit() or not (1 <= int(choice) <= len(agents)):
        error("Invalid selection.")
        return
    agent = agents[int(choice) - 1]
    assign_ticket(int(tid), agent["id"])
    success(f"Ticket #{tid} assigned to {agent['name']}  |  Status: In Progress")


def menu_escalate():
    header("ESCALATE TICKET")
    tid = input("  Ticket ID: ").strip()
    if not tid.isdigit():
        error("Invalid ID.")
        return
    t = get_ticket(int(tid))
    if not t:
        error(f"Ticket #{tid} not found.")
        return
    new_priority = escalate_ticket(int(tid))
    success(f"Ticket #{tid} escalated  |  New priority: {new_priority}  |  Status: Escalated")


def menu_resolve():
    header("RESOLVE TICKET")
    tid = input("  Ticket ID: ").strip()
    if not tid.isdigit():
        error("Invalid ID.")
        return
    t = get_ticket(int(tid))
    if not t:
        error(f"Ticket #{tid} not found.")
        return
    print(f"  Ticket: {C.WHITE}{t['title']}{C.RESET}\n")
    note = input("  Resolution note (what was done to fix it): ").strip()
    if not note:
        error("Resolution note is required.")
        return
    resolve_ticket(int(tid), note)
    success(f"Ticket #{tid} marked as Resolved.")

    close = input("  Also mark as Closed? [y/N]: ").strip().lower()
    if close == "y":
        close_ticket(int(tid))
        success(f"Ticket #{tid} closed.")


def menu_search():
    header("SEARCH TICKETS")
    query = input("  Search (title, description, status, priority): ").strip()
    if not query:
        return
    results = search_tickets(query)
    if not results:
        info(f"No results for '{query}'.")
        return
    print(f"\n  Results for '{clr(query, C.CYAN)}':\n")
    print(f"  {'#ID':<8}{'PRIORITY':<14}{'STATUS':<22}{'ASSIGNED TO':<20}TITLE")
    divider()
    for t in results:
        print_ticket_row(t)
    print(f"\n  {C.GRAY}Found: {len(results)} ticket(s){C.RESET}")


def menu_stats():
    header("DASHBOARD STATISTICS")
    s = get_stats()
    print(f"  {C.BOLD}Total Tickets:{C.RESET} {clr(s['total'], C.WHITE)}\n")

    print(f"  {C.BOLD}By Status:{C.RESET}")
    for status, cnt in s["by_status"].items():
        color = STATUS_COLOR.get(status, C.WHITE)
        bar   = "█" * cnt
        print(f"    {clr(status, color):<20}  {clr(str(cnt), C.WHITE)}  {C.GRAY}{bar}{C.RESET}")

    print(f"\n  {C.BOLD}By Priority:{C.RESET}")
    for priority, cnt in s["by_priority"].items():
        color = PRIORITY_COLOR.get(priority, C.WHITE)
        bar   = "█" * cnt
        print(f"    {clr(priority, color):<20}  {clr(str(cnt), C.WHITE)}  {C.GRAY}{bar}{C.RESET}")


# ── MAIN MENU ────────────────────────────────────────────────
MENU_OPTIONS = {
    "1": ("Create New Ticket",   menu_create),
    "2": ("View All Tickets",    menu_view_all),
    "3": ("View Ticket Detail",  menu_view_ticket),
    "4": ("Assign Ticket",       menu_assign),
    "5": ("Escalate Priority",   menu_escalate),
    "6": ("Resolve Ticket",      menu_resolve),
    "7": ("Search Tickets",      menu_search),
    "8": ("Dashboard Stats",     menu_stats),
    "0": ("Exit",                None),
}

def main():
    initialize_db()
    os.system("cls" if sys.platform == "win32" else "clear")

    print(f"{C.BLUE}{'═' * 55}{C.RESET}")
    print(f"{C.BOLD}{C.WHITE}   HELP DESK TICKETING SYSTEM{C.RESET}")
    print(f"{C.GRAY}   Author  : Om M. Sutaria{C.RESET}")
    print(f"{C.GRAY}   GitHub  : github.com/OmSutaria/helpdesk-ticket-system{C.RESET}")
    print(f"{C.BLUE}{'═' * 55}{C.RESET}")

    while True:
        print(f"\n{C.BOLD}  MAIN MENU{C.RESET}")
        divider()
        for key, (label, _) in MENU_OPTIONS.items():
            color = C.RED if key == "0" else C.CYAN
            print(f"  {clr(f'[{key}]', color)}  {label}")
        divider()

        choice = input(f"\n  {C.BOLD}Select option:{C.RESET} ").strip()
        if choice not in MENU_OPTIONS:
            error("Invalid option. Please choose from the menu.")
            continue
        if choice == "0":
            print(f"\n  {C.GREEN}Goodbye!{C.RESET}\n")
            break

        _, action = MENU_OPTIONS[choice]
        try:
            action()
        except KeyboardInterrupt:
            print()
            continue
        except Exception as e:
            error(f"Unexpected error: {e}")

        if choice not in ("8",):
            pause()

if __name__ == "__main__":
    main()
