import streamlit as st
import sqlite3
from datetime import date

st.set_page_config(page_title="To-Do App")

# ---------- STYLE ----------
st.markdown("""
<style>
body {background-color: #0f172a;}

.title {
    font-size: 40px;
    font-weight: bold;
    color: #38bdf8;
}

.card {
    background: #1e293b;
    padding: 15px;
    border-radius: 15px;
    margin-bottom: 10px;
    color: white;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
}

.high {color:#ef4444;}
.medium {color:#facc15;}
.low {color:#22c55e;}

.done {text-decoration: line-through;}
</style>
""", unsafe_allow_html=True)

# ---------- DB ----------
conn = sqlite3.connect("todo.db", check_same_thread=False)
c = conn.cursor()

c.execute("CREATE TABLE IF NOT EXISTS users(username TEXT, password TEXT)")
c.execute("""CREATE TABLE IF NOT EXISTS tasks(
    username TEXT, task TEXT, priority TEXT, due TEXT, done INTEGER)""")
conn.commit()

# ---------- SESSION ----------
if "user" not in st.session_state:
    st.session_state.user = None

# ---------- LOGIN ----------
def login():
    st.title("Login")

    user = st.text_input("Username")
    pw = st.text_input("Password", type="password")

    if st.button("Login"):
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (user,pw))
        if c.fetchone():
            st.session_state.user = user
            st.rerun()
        else:
            st.error("Invalid login")

    if st.button("Register"):
        c.execute("INSERT INTO users VALUES (?,?)",(user,pw))
        conn.commit()
        st.success("User created")

# ---------- MAIN ----------
if st.session_state.user:

    st.markdown('<div class="title">📝 Advanced To-Do App</div>', unsafe_allow_html=True)

    # ---------- Sample Tasks ----------
    if st.button("📥 Sample Tasks Add"):
        tasks_list = [
            ("Study Python", "High"),
            ("Practice coding", "High"),
            ("Complete assignment", "Medium"),
            ("Exercise", "Low"),
            ("Attend class", "High"),
            ("Sleep early", "Low")
        ]

        for t, p in tasks_list:
            c.execute("INSERT INTO tasks VALUES (?,?,?,?,?)",
                      (st.session_state.user, t, p, str(date.today()), 0))
        conn.commit()
        st.rerun()

    # ---------- Add Task ----------
    task = st.text_input("Enter Task")
    priority = st.selectbox("Priority", ["High","Medium","Low"])
    due = st.date_input("Due Date", min_value=date.today())

    if st.button("Add Task"):
        if task:
            c.execute("INSERT INTO tasks VALUES (?,?,?,?,?)",
                      (st.session_state.user, task, priority, str(due), 0))
            conn.commit()
            st.success("Task Added")

    # ---------- Fetch ----------
    c.execute("SELECT rowid,* FROM tasks WHERE username=?",
              (st.session_state.user,))
    data = c.fetchall()

    # ---------- Dashboard ----------
    total = len(data)
    done_count = len([x for x in data if x[5] == 1])
    pending = total - done_count

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Tasks", total)
    col2.metric("Completed", done_count)
    col3.metric("Pending", pending)

    if total > 0:
        st.progress(done_count / total)

    st.subheader("Your Tasks")

    # ---------- Display ----------
    for row in data:
        id_, user, task, priority, due, done = row

        color = priority.lower()

        st.markdown(f"""
        <div class="card">
        <b class="{color}">{priority}</b> |
        {"✅" if done else "⏳"} {task} <br>
        📅 {due}
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([2,1,1])

        with col2:
            if st.button("✔ Done", key=f"d{id_}"):
                c.execute("UPDATE tasks SET done=1 WHERE rowid=?", (id_,))
                conn.commit()
                st.rerun()

        with col3:
            if st.button("🗑 Delete", key=f"x{id_}"):
                c.execute("DELETE FROM tasks WHERE rowid=?", (id_,))
                conn.commit()
                st.rerun()

else:
    login()