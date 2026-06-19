#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Session End Archiver Hook - Python implementation for Windows.
Reads the latest Gemini/Antigravity conversation log (transcript.jsonl)
and updates the Archive Department ledger.
"""

import os
import sys
import json
import glob
import re
from datetime import datetime

def find_latest_transcript():
    """Finds the most recently modified transcript.jsonl in the local AppData brain directory."""
    home = os.path.expanduser("~")
    # Base folder of brain directories on Windows
    base_dir = os.path.join(home, ".gemini", "antigravity", "brain")
    if not os.path.exists(base_dir):
        return None, None
        
    pattern = os.path.join(base_dir, "**", ".system_generated", "logs", "transcript.jsonl")
    files = glob.glob(pattern, recursive=True)
    if not files:
        return None, None
        
    # Sort files by modification time descending
    files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    latest_file = files[0]
    
    # Extract session ID (parent directory of .system_generated)
    # The path looks like: .../brain/<session_id>/.system_generated/logs/transcript.jsonl
    norm_path = os.path.normpath(latest_file)
    parts = norm_path.split(os.sep)
    try:
        # Search for brain directory in the split path and grab the next segment
        brain_idx = parts.index("brain")
        session_id = parts[brain_idx + 1]
    except (ValueError, IndexError):
        session_id = "unknown_session"
        
    return latest_file, session_id

def parse_transcript(transcript_path):
    """Parses user requests, tools used, and files modified from the JSONL transcript."""
    user_requests = []
    modified_files = set()
    tools_used = set()
    
    if not transcript_path or not os.path.exists(transcript_path):
        return None
        
    with open(transcript_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                
                # Extract user input prompts
                if data.get("type") == "USER_INPUT":
                    content = data.get("content", "")
                    # Extract contents of <USER_REQUEST> if present
                    match = re.search(r'<USER_REQUEST>(.*?)</USER_REQUEST>', content, re.DOTALL)
                    if match:
                        req_text = match.group(1).strip()
                    else:
                        req_text = content.strip()
                    if req_text:
                        user_requests.append(req_text)
                        
                # Extract tool calls from model planning responses
                if "tool_calls" in data:
                    for tc in data["tool_calls"]:
                        name = tc.get("name")
                        if name:
                            tools_used.add(name)
                            
                        # Detect if it's a file writing/modifying tool
                        is_modification = name in ['write_to_file', 'replace_file_content', 'multi_replace_file_content']
                        
                        args = tc.get("args", {})
                        if isinstance(args, str):
                            try:
                                args = json.loads(args)
                            except:
                                pass
                        if isinstance(args, dict) and is_modification:
                            target = args.get("TargetFile")
                            if target:
                                if isinstance(target, str):
                                    target = target.strip('"\'')
                                    modified_files.add(os.path.normpath(target))
            except Exception:
                pass
                
    return {
        "requests": user_requests,
        "files": sorted(list(modified_files)),
        "tools": sorted(list(tools_used))
    }

def format_summary_entry(session_id, data, workspace_root):
    """Formats the extracted session summary into a clean Georgian markdown ledger entry."""
    today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    short_id = session_id[:8]
    
    file_links = []
    for f in data["files"]:
        try:
            rel = os.path.relpath(f, workspace_root)
            rel_url = rel.replace("\\", "/")
            abs_url = f.replace("\\", "/")
            basename = os.path.basename(f)
            file_links.append(f"- [{basename}](file:///{abs_url}) (`{rel_url}`)")
        except Exception:
            basename = os.path.basename(f)
            file_links.append(f"- {basename}")
            
    files_str = "\n".join(file_links) if file_links else "- ფაილები არ შეცვლილა (None)"
    
    # Extract last 5 unique prompts
    recent_requests = []
    seen = set()
    for r in reversed(data["requests"]):
        cleaned = r.replace('\n', ' ').strip()
        if cleaned and cleaned not in seen:
            seen.add(cleaned)
            recent_requests.append(cleaned)
        if len(recent_requests) >= 5:
            break
    recent_requests.reverse()
    
    requests_str = "\n".join([f"  - {r}" for r in recent_requests]) if recent_requests else "  - მომხმარებლის მოთხოვნა არ დაფიქსირებულა."
    
    tools_str = ", ".join([f"`{t}`" for t in data["tools"]]) if data["tools"] else "None"
    
    entry = f"""### 📁 სესია: {today} (სესიის ID: {short_id})
* **სტატუსი:** ✅ დასრულებული (Archived)
* **გამოყენებული ხელსაწყოები:** {tools_str}
* **შეცვლილი ფაილები:**
{files_str}
* **განხილული ძირითადი საკითხები (User Prompts):**
{requests_str}"""
    return entry

def update_archive_department(session_id, summary_entry, workspace_root):
    """Inserts or updates the session entry inside Archive Department.md in an idempotent way."""
    # The vault reorganization (2026-06-12) moved this file under Central AI Team\Departments;
    # check known locations first, then fall back to a recursive search.
    candidates = [
        os.path.join(workspace_root, "Archive Department.md"),
        os.path.join(workspace_root, "Central AI Team", "Departments", "Archive Department.md"),
    ]
    archive_path = next((p for p in candidates if os.path.exists(p)), None)
    if not archive_path:
        import glob as _glob
        matches = _glob.glob(os.path.join(workspace_root, "**", "Archive Department.md"), recursive=True)
        archive_path = matches[0] if matches else None
    if not archive_path:
        print(f"[Error] Archive Department.md not found anywhere under: {workspace_root}")
        return False
        
    with open(archive_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    session_marker = f"<!-- SESSION_ID: {session_id} -->"
    session_end_marker = f"<!-- SESSION_END: {session_id} -->"
    
    entry_wrapped = f"{session_marker}\n{summary_entry}\n{session_end_marker}"
    
    # If the session already exists, overwrite it to prevent duplicates
    start_idx = content.find(session_marker)
    end_idx = content.find(session_end_marker)
    if start_idx != -1 and end_idx != -1:
        new_content = content[:start_idx] + entry_wrapped + content[end_idx + len(session_end_marker):]
        print(f"[Info] Idempotent rewrite: Updated session {session_id[:8]} entry in Archive Department.md")
    else:
        # We find the insertion point before the "## 🧾 არქივისტის მიღების დადასტურება" header
        marker = "## 🧾 არქივისტის მიღების დადასტურება"
        if marker in content:
            ledger_header = "## ⏱️ სესიების ავტომატური რეესტრი (Automated Session Ledger)"
            if ledger_header not in content:
                # Add the section header and the first entry
                insert_text = f"{ledger_header}\n\n{entry_wrapped}\n\n---\n\n"
                new_content = content.replace(marker, f"{insert_text}{marker}")
            else:
                # Append under the existing header
                new_content = content.replace(ledger_header, f"{ledger_header}\n\n{entry_wrapped}\n\n---\n")
            print(f"[Info] Appended new session {session_id[:8]} entry to Archive Department.md")
        else:
            new_content = content + "\n\n" + entry_wrapped
            print(f"[Info] Warning: Verification header not found; appended session to end of file.")
            
    with open(archive_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    return True

def main():
    print("[SessionEnd Hook] Starting auto-archiving...")
    
    # Get workspace root
    workspace_root = os.getcwd()
    print(f"[SessionEnd Hook] Workspace Root: {workspace_root}")
    
    # Find latest transcript
    transcript_path, session_id = find_latest_transcript()
    if not transcript_path:
        print("[Error] No transcript.jsonl log files found in AppData!")
        sys.exit(1)
        
    print(f"[SessionEnd Hook] Found active transcript: {transcript_path}")
    print(f"[SessionEnd Hook] Session ID: {session_id}")
    
    # Parse transcript
    data = parse_transcript(transcript_path)
    if not data:
        print("[Error] Failed to parse transcript.")
        sys.exit(1)
        
    # Format entry
    entry = format_summary_entry(session_id, data, workspace_root)
    
    # Update Archive Department
    success = update_archive_department(session_id, entry, workspace_root)
    if success:
        print("[SessionEnd Hook] Successfully archived session details to Archive Department.md!")
    else:
        print("[SessionEnd Hook] Failed to update Archive Department.md.")
        sys.exit(1)

if __name__ == "__main__":
    main()
