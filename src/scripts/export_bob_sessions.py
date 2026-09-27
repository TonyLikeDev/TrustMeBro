#!/usr/bin/env python3
"""
Script trích xuất toàn bộ session của IBM Bob từ ~/.bob/db/bob.db
và lưu thành các file Markdown & JSON vào thư mục bob-session/ và bob_sessions/session_logs/
"""

import os
import sys
import json
import sqlite3
from datetime import datetime

def format_timestamp(ts):
    if not ts:
        return "N/A"
    try:
        if ts > 1e11: # milliseconds
            ts = ts / 1000
        return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        return str(ts)

def sanitize_filename(name):
    clean = "".join([c if c.isalnum() or c in "._- " else "_" for c in name])
    return clean.strip().replace(" ", "_")[:60]

def main():
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        db_candidates = [sys.argv[1]]
    else:
        home = os.path.expanduser("~")
        project_root = os.path.dirname(os.path.abspath(__file__))
        db_candidates = [
            os.path.join(project_root, "bob.db"),
            os.path.join(project_root, "bob-session", "bob.db"),
            "/home/pro/.bob/db/bob.db",
            "/home/pro/.bob/dev-db/bob.db",
            "/home/pro/.bobide/db/bob.db",
            os.path.join(home, ".bob", "db", "bob.db"),
            os.path.join(home, ".bob", "dev-db", "bob.db"),
            os.path.join(home, ".bobide", "db", "bob.db"),
        ]
    
    db_path = None
    for cand in db_candidates:
        if os.path.exists(cand):
            db_path = cand
            break
            
    if not db_path:
        print(f"❌ Không tìm thấy database của Bob tại các vị trí mặc định:")
        for cand in db_candidates:
            print(f"   - {cand}")
        sys.exit(1)
        
    print(f"🔍 Đang đọc database Bob: {db_path}")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Đọc danh sách tasks
    try:
        cur.execute("SELECT id, project_id, title, status, first_message, directory, costs, created_at, updated_at FROM tasks ORDER BY created_at ASC")
        tasks = cur.fetchall()
    except Exception as e:
        print(f"❌ Lỗi khi đọc bảng tasks: {e}")
        sys.exit(1)
        
    print(f"✅ Đã tìm thấy {len(tasks)} session tasks.")
    
    # Xác định output directories
    project_root = os.path.dirname(os.path.abspath(__file__))
    out_dir_local = os.path.join(project_root, "bob-session")
    out_dir_hackathon = os.path.abspath(os.path.join(project_root, "..", "bob_sessions", "session_logs"))
    
    os.makedirs(out_dir_local, exist_ok=True)
    if os.path.exists(os.path.dirname(out_dir_hackathon)):
        os.makedirs(out_dir_hackathon, exist_ok=True)
    else:
        out_dir_hackathon = None

    all_sessions_data = []
    summary_rows = []
    
    for idx, task in enumerate(tasks, 1):
        task_id, project_id, title, status, first_message, directory, costs_raw, created_at, updated_at = task
        title_display = title.strip() if title and title.strip() else (first_message[:40] if first_message else f"Session_{idx}")
        
        # Parse costs
        costs_info = {}
        if costs_raw:
            try:
                costs_info = json.loads(costs_raw)
            except Exception:
                costs_info = {"raw": str(costs_raw)}
                
        # Lấy messages
        cur.execute("SELECT id, role, data, created_at FROM messages WHERE task_id = ? ORDER BY created_at ASC", (task_id,))
        raw_messages = cur.fetchall()
        
        session_obj = {
            "index": idx,
            "id": task_id,
            "title": title_display,
            "status": status,
            "directory": directory,
            "costs": costs_info,
            "created_at": format_timestamp(created_at),
            "updated_at": format_timestamp(updated_at),
            "messages_count": len(raw_messages),
            "messages": []
        }
        
        # Tạo Markdown chi tiết cho session
        md_lines = []
        md_lines.append(f"# Bob Session {idx:02d}: {title_display}")
        md_lines.append(f"- **Task ID**: `{task_id}`")
        md_lines.append(f"- **Status**: `{status}`")
        md_lines.append(f"- **Directory**: `{directory}`")
        md_lines.append(f"- **Created At**: `{format_timestamp(created_at)}`")
        md_lines.append(f"- **Updated At**: `{format_timestamp(updated_at)}`")
        md_lines.append(f"- **Token & Cost Consumption**:\n```json\n{json.dumps(costs_info, indent=2, ensure_ascii=False)}\n```")
        md_lines.append("\n---\n")
        
        for msg in raw_messages:
            msg_id, role, data_str, msg_time = msg
            parsed_data = None
            try:
                parsed_data = json.loads(data_str)
            except Exception:
                parsed_data = data_str
                
            session_obj["messages"].append({
                "id": msg_id,
                "role": role,
                "created_at": format_timestamp(msg_time),
                "data": parsed_data
            })
            
            md_lines.append(f"### [{role.upper()}] — {format_timestamp(msg_time)}")
            if isinstance(parsed_data, dict):
                # Hiển thị text hoặc prompt rõ ràng nếu có
                text_content = parsed_data.get("text") or parsed_data.get("content") or parsed_data.get("message")
                if text_content and isinstance(text_content, str):
                    md_lines.append(text_content)
                    md_lines.append("\n*Chi tiết metadata:*")
                md_lines.append(f"```json\n{json.dumps(parsed_data, indent=2, ensure_ascii=False)}\n```")
            elif isinstance(parsed_data, list):
                md_lines.append(f"```json\n{json.dumps(parsed_data, indent=2, ensure_ascii=False)}\n```")
            else:
                md_lines.append(str(parsed_data))
            md_lines.append("\n---\n")
            
        all_sessions_data.append(session_obj)
        summary_rows.append(f"| {idx} | `{task_id[:8]}...` | {title_display} | `{status}` | {len(raw_messages)} | {format_timestamp(created_at)} |")
        
        md_filename = f"session_{idx:02d}_{sanitize_filename(title_display)}.md"
        
        # Ghi ra thư mục local bob-session/
        with open(os.path.join(out_dir_local, md_filename), "w", encoding="utf-8") as f:
            f.write("\n".join(md_lines))
            
        # Ghi ra thư mục bob_sessions/session_logs/ nếu có
        if out_dir_hackathon:
            with open(os.path.join(out_dir_hackathon, md_filename), "w", encoding="utf-8") as f:
                f.write("\n".join(md_lines))
                
        print(f"  [+] Đã xuất session {idx:02d}: {title_display} ({len(raw_messages)} messages)")
        
    # Ghi file JSON tổng hợp
    json_path = os.path.join(out_dir_local, "all_bob_sessions.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_sessions_data, f, indent=2, ensure_ascii=False)
        
    # Ghi file SUMMARY.md
    summary_content = [
        "# Tổng hợp toàn bộ Session của IBM Bob",
        f"- **Thời gian xuất**: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`",
        f"- **Tổng số Session**: `{len(tasks)}`",
        f"- **Nguồn Database**: `{db_path}`",
        "",
        "## Danh sách Sessions",
        "| # | Task ID | Tiêu đề | Trạng thái | Số Messages | Bắt đầu lúc |",
        "|---|---------|---------|------------|-------------|-------------|",
        *summary_rows,
        "",
        "---",
        "*(Dữ liệu được trích xuất tự động từ SQLite `bob.db` phục vụ nộp bài Hackathon)*"
    ]
    
    with open(os.path.join(out_dir_local, "SUMMARY.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(summary_content))
        
    if out_dir_hackathon:
        with open(os.path.join(out_dir_hackathon, "SUMMARY.md"), "w", encoding="utf-8") as f:
            f.write("\n".join(summary_content))
            
    print("\n🎉 HOÀN TẤT TRÍCH XUẤT TOÀN BỘ SESSIONS CỦA BOB!")
    print(f"📁 Lưu tại:")
    print(f"   1. {out_dir_local}")
    if out_dir_hackathon:
        print(f"   2. {out_dir_hackathon}")

if __name__ == "__main__":
    main()
