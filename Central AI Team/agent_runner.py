#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🏛️ AI Software House Agent Runner & Executor
Parses the active Obsidian dispatch card, runs tasks sequentially via LLM API,
implements interactive code writing, updates task statuses, and triggers the archiver.
"""

import os
import sys
import re
from pathlib import Path

# Configure console encoding to UTF-8
sys.stdout.reconfigure(encoding='utf-8')

# ANSI Colors for premium themed terminal styling
CLR_RESET = "\033[0m"
CLR_BOLD = "\033[1m"
CLR_RED = "\033[38;2;213;0;28m"       # Guards Red
CLR_GREEN = "\033[38;2;136;212;19m"   # Acid Green
CLR_BLUE = "\033[38;2;0;150;255m"     # Carbon Blue
CLR_AMBER = "\033[38;2;255;153;0m"    # Chrono Orange
CLR_GREY = "\033[90m"

def load_dotenv():
    """Simple helper to load .env files if present in workspace root."""
    for p in [Path("."), Path(".."), Path(__file__).parent.parent]:
        env_path = p / ".env"
        if env_path.exists():
            print(f"{CLR_GREY}ჩაიტვირთა გარემოს ცვლადები: {env_path.resolve()}{CLR_RESET}")
            with open(env_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, val = line.split("=", 1)
                    os.environ[key.strip()] = val.strip().strip('"\'')
            break

def call_gemini(system_prompt: str, user_prompt: str, api_key: str) -> str:
    """Calls Gemini API using the official google-generativeai package."""
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=system_prompt)
        response = model.generate_content(user_prompt)
        return response.text
    except ImportError:
        print(f"{CLR_RED}შეცდომა: google-generativeai ბიბლიოთეკა არ არის დაყენებული.{CLR_RESET}")
        print(f"{CLR_GREY}გთხოვთ გაუშვათ: pip install google-generativeai{CLR_RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"{CLR_RED}Gemini API შეცდომა: {e}{CLR_RESET}")
        sys.exit(1)

def call_claude(system_prompt: str, user_prompt: str, api_key: str) -> str:
    """Calls Anthropic Claude API using the anthropic package."""
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )
        return message.content[0].text
    except ImportError:
        print(f"{CLR_RED}შეცდომა: anthropic ბიბლიოთეკა არ არის დაყენებული.{CLR_RESET}")
        print(f"{CLR_GREY}გთხოვთ გაუშვათ: pip install anthropic{CLR_RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"{CLR_RED}Claude API შეცდომა: {e}{CLR_RESET}")
        sys.exit(1)

def main():
    load_dotenv()
    
    vault_dir = Path(__file__).parent.resolve()
    dispatch_card_path = vault_dir / "Idea Dispatcher Output.md"
    
    print(f"{CLR_BOLD}{CLR_RED}======================================================================{CLR_RESET}")
    print(f"{CLR_BOLD}🏛️ AI SOFTWARE HOUSE AGENT RUNNER & EXECUTOR{CLR_RESET}")
    print(f"{CLR_BOLD}{CLR_RED}======================================================================{CLR_RESET}\n")
    
    # 1. Verify dispatch card exists
    if not dispatch_card_path.exists():
        print(f"{CLR_RED}შეცდომა: აქტიური სადისპეტჩერო ბარათი (Idea Dispatcher Output.md) ვერ მოიძებნა!{CLR_RESET}")
        print(f"{CLR_GREY}გთხოვთ ჯერ გაუშვათ dispatcher.py ახალი იდეის დასარუტებლად.{CLR_RESET}")
        sys.exit(1)
        
    # 2. Parse dispatch card
    with open(dispatch_card_path, "r", encoding="utf-8") as f:
        card_content = f.read()
        
    # Extract agent name
    agent_match = re.search(r'# 🎯 Active Dispatch Card:\s*(.+)', card_content)
    agent_name = agent_match.group(1).strip() if agent_match else "Unknown Agent"
    
    # Extract department
    dept_match = re.search(r'\*\*დეპარტამენტი:\*\*.*?(\w[\w\s&]+)', card_content)
    department = dept_match.group(1).strip() if dept_match else "Unknown Department"
    
    # Extract system prompt
    prompt_match = re.search(r'## 🤖 სუბაგენტის სისტემური პრომპტი \(Subagent System Prompt\)\s*```markdown\n([\s\S]+?)\n```', card_content)
    system_prompt = prompt_match.group(1).strip() if prompt_match else ""
    
    if not system_prompt:
        print(f"{CLR_RED}შეცდომა: სუბაგენტის სისტემური პრომპტი ვერ ამოიკითხა!{CLR_RESET}")
        sys.exit(1)
        
    print(f"{CLR_BOLD}აქტიური აგენტი:{CLR_RESET} {CLR_GREEN}{agent_name}{CLR_RESET}")
    print(f"{CLR_BOLD}დეპარტამენტი:{CLR_RESET} {CLR_BLUE}{department}{CLR_RESET}")
    print(f"----------------------------------------------------------------------")
    
    # 3. Configure API Clients
    gemini_key = os.environ.get("GEMINI_API_KEY")
    claude_key = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("CLAUDE_API_KEY")
    
    if not gemini_key and not claude_key:
        print(f"{CLR_RED}შეცდომა: API გასაღებები (GEMINI_API_KEY ან ANTHROPIC_API_KEY) ვერ მოიძებნა!{CLR_RESET}")
        print("გთხოვთ დაამატოთ ისინი .env ფაილში ან სისტემის გარემოს ცვლადებში.")
        sys.exit(1)
        
    client_type = "gemini" if gemini_key else "claude"
    api_key = gemini_key if gemini_key else claude_key
    print(f"{CLR_GREY}აქტიური API კავშირი: {client_type.upper()}{CLR_RESET}\n")
    
    # 4. Parse Checklist tasks
    tasks = []
    # Find all lines like "- [ ] task text" or "- [x] task text"
    lines = card_content.split("\n")
    for idx, line in enumerate(lines):
        match = re.match(r'^\s*-\s*\[\s*([ xX])\s*\]\s*(.+)', line)
        if match:
            status = match.group(1).strip().lower()
            task_text = match.group(2).strip()
            tasks.append({
                "line_idx": idx,
                "status": "done" if status == "x" else "pending",
                "text": task_text
            })
            
    if not tasks:
        print(f"{CLR_RED}შეცდომა: სამოქმედო გეგმა (Checklist) ცარიელია ან ვერ ამოიკითხა!{CLR_RESET}")
        sys.exit(1)
        
    # Execute pending tasks sequentially
    workspace_root = vault_dir.parent
    
    completed_any = False
    for task in tasks:
        if task["status"] == "done":
            print(f"{CLR_GREY}[x] {task['text']} (უკვე შესრულებულია){CLR_RESET}")
            continue
            
        print(f"\n{CLR_BOLD}{CLR_AMBER}⏳ სრულდება: {task['text']}{CLR_RESET}")
        
        user_prompt = f"""დავალება: შეასრულე შემდეგი ეტაპი სამოქმედო გეგმიდან:
"{task['text']}"

თუ დავალება მოითხოვს ფაილების შექმნას ან კოდის მოდიფიკაციას, კოდის გარშემო გამოიყენე შემდეგი მკაფიო მარკერი, რათა ავტომატურად ჩავწერო დისკზე:
[FILE: <ფაილის_ფარდობითი_გზა_პროექტის_root-იდან>]
ფაილის სრული შიგთავსი
[FILE_END]

მაგალითად:
[FILE: src/index.css]
body {{ background-color: #0f0f12; }}
[FILE_END]

სხვა შემთხვევაში უბრალოდ მოამზადე რეპორტი/ანალიზი დახვეწილ ფორმატში.
"""
        
        print(f"{CLR_GREY}API მოთხოვნის გაგზავნა...{CLR_RESET}")
        if client_type == "gemini":
            response_text = call_gemini(system_prompt, user_prompt, api_key)
        else:
            response_text = call_claude(system_prompt, user_prompt, api_key)
            
        print(f"\n{CLR_BOLD}🤖 აგენტის პასუხი:{CLR_RESET}")
        print(response_text)
        print(f"----------------------------------------------------------------------")
        
        # Parse potential file writes from response
        file_blocks = re.findall(r'\[FILE:\s*(.+?)\]([\s\S]*?)\[FILE_END\]', response_text)
        for rel_path, code_content in file_blocks:
            rel_path = rel_path.strip()
            code_content = code_content.strip()
            
            # Target path resolve
            target_path = (workspace_root / rel_path).resolve()
            
            print(f"\n{CLR_BOLD}{CLR_AMBER}📂 აგენტი ითხოვს ფაილის ჩაწერას/განახლებას:{CLR_RESET} {rel_path}")
            print(f"{CLR_GREY}სამიზნე გზა: {target_path}{CLR_RESET}")
            
            confirm = input(f"{CLR_BOLD}გსურთ ამ ფაილის ჩაწერა? (Y/N): {CLR_RESET}").strip().lower()
            if confirm in ['y', 'yes', 'ჰო', 'კი']:
                # Ensure parent dirs exist
                target_path.parent.mkdir(parents=True, exist_ok=True)
                with open(target_path, "w", encoding="utf-8") as tf:
                    tf.write(code_content)
                print(f"{CLR_GREEN}✔ ფაილი წარმატებით ჩაიწერა: {rel_path}{CLR_RESET}")
            else:
                print(f"{CLR_RED}✖ ჩაწერა გაუქმებულია მომხმარებლის მიერ.{CLR_RESET}")
                
        # Update Obsidian Checklist status to done
        lines[task["line_idx"]] = lines[task["line_idx"]].replace("[ ]", "[x]").replace("[  ]", "[x]")
        completed_any = True
        
        # Write back to Obsidian immediately
        with open(dispatch_card_path, "w", encoding="utf-8") as of:
            of.write("\n".join(lines))
            
        print(f"{CLR_GREEN}✔ Obsidian-ის Checklist განახლდა: {task['text']}{CLR_RESET}")
        
        input(f"\n{CLR_BOLD}დააჭირეთ Enter-ს შემდეგ ნაბიჯზე გადასასვლელად...{CLR_RESET}")
        
    if completed_any:
        print(f"\n{CLR_GREEN}✔ ყველა დაგეგმილი ნაბიჯი შესრულებულია!{CLR_RESET}")
        print(f"{CLR_GREY}ავტომატური არქივატორი გაეშვება...{CLR_RESET}")
        
        # Run session end archiver
        archiver_script = workspace_root / "scripts" / "session-end-archiver.py"
        if archiver_script.exists():
            os.system(f"python \"{archiver_script}\"")
        else:
            print(f"{CLR_RED}არქივატორი {archiver_script} ვერ მოიძებნა.{CLR_RESET}")
    else:
        print(f"\n{CLR_AMBER}ყველა ამოცანა უკვე შესრულებული იყო.{CLR_RESET}")
        
    print(f"\n{CLR_BOLD}{CLR_RED}======================================================================{CLR_RESET}\n")

if __name__ == "__main__":
    main()
