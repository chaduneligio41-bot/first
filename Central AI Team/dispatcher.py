#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🏛️ AI Software House Agentic Dispatcher & Router
Determines the optimal department and agent for a project idea,
prepares a customized prompt with domain-specific rules, and writes an Obsidian dispatch card.
"""

import os
import sys
import re
import json
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
CLR_PURPLE = "\033[38;2;153;51;255m"  # R&D Purple
CLR_GOLD = "\033[38;2;255;204;0m"     # Innovation Gold
CLR_GREY = "\033[90m"

DEPT_THEMES = {
    "Cockpit UI UX Studio": {"color": CLR_RED, "hex": "#d5001c", "icon": "🖲️"},
    "Data Tech Architecture": {"color": CLR_BLUE, "hex": "#0096ff", "icon": "📊"},
    "Cybersecurity Compliance": {"color": CLR_GREEN, "hex": "#88d413", "icon": "🛡️"},
    "Aftersales CX Analytics": {"color": CLR_AMBER, "hex": "#ff9900", "icon": "📈"},
    "RD Lab": {"color": CLR_PURPLE, "hex": "#9933ff", "icon": "🔬"},
    "Innovation Department": {"color": CLR_GOLD, "hex": "#ffcc00", "icon": "💡"},
    "Archive Department": {"color": CLR_GREY, "hex": "#7f8c8d", "icon": "📂"},
    "Translation Department": {"color": CLR_BLUE, "hex": "#1abc9c", "icon": "🔀"},
    "Marketing Department": {"color": CLR_RED, "hex": "#e84393", "icon": "📢"},
    "Web Reach Department": {"color": CLR_BLUE, "hex": "#00d2ff", "icon": "🌐"}
}

def detect_domain(idea: str) -> dict:
    """Detects the domain of the idea and returns the rules and theme colors."""
    idea_lower = idea.lower()
    
    porsche_kws = ["porsche", "obd", "piwis", "tegeta", "car", "aftersales", "პორშე", "სარემონტო", "მანქანა", "ავტო"]
    fitness_kws = ["fitness", "workout", "gym", "health", "calories", "tracker", "exercise", "ფიტნეს", "ვარჯიშ", "კალორი", "ჯანმრთელობ"]
    
    if any(kw in idea_lower for kw in porsche_kws):
        return {
            "name": "Porsche Aftersales",
            "styling_rules": (
                "**DOMAIN CONTEXT: Porsche Aftersales Brand Rules**\n"
                "- Colors: Guards Red (#d5001c), Matte Black (#0d0d0f), Acid Green (#88d413), and titanium accents.\n"
                "- Design System: Dark Cockpit UI, Glassmorphism, speedometer dials, circular chronometers.\n"
                "- Usability: Glove-friendly touchscreen buttons (min 48px), high contrast for 2-meter workshop reading."
            ),
            "extra_checklist": [
                "დაიცავით Porsche-ს ბრენდბუქის ფერები (Guards Red, Matte Black, Acid Green)",
                "უზრუნველყავით სახელოსნოს რეალურ პირობებზე მორგებული ერგონომიული UI (დიდი ღილაკები)"
            ]
        }
    elif any(kw in idea_lower for kw in fitness_kws):
        return {
            "name": "Fitness & Health Application",
            "styling_rules": (
                "**DOMAIN CONTEXT: Fitness & Health App Rules**\n"
                "- Colors: Neon Orange (#FF6B35) for active states, Electric Blue (#0077B6) for metrics, dark background.\n"
                "- Design System: Dashboard with progress rings, workout schedules, health graphs, active/inactive indicator glows.\n"
                "- Usability: Quick tap logging, smooth micro-interactions, mobile-first design."
            ),
            "extra_checklist": [
                "გამოიყენეთ ფიტნეს-აპლიკაციის აქტიური ფერები (Neon Orange და Electric Blue)",
                "დააპროექტეთ პროგრესის წრეები (Progress Rings) და ვარჯიშის დინამიური სქემები"
            ]
        }
    else:
        return {
            "name": "Generic Domain",
            "styling_rules": (
                "**DOMAIN CONTEXT: General Styling Rules**\n"
                "- Colors: HSL-tailored premium palette. Avoid generic primary red/blue/green.\n"
                "- Design System: Modern minimalist dashboard cards, clean typography (Outfit/Inter).\n"
                "- Usability: Clear navigation structure, smooth keyframe micro-animations."
            ),
            "extra_checklist": [
                "გამოიყენეთ HSL-ზე დაფუძნებული პრემიუმ ფერთა პალიტრა",
                "უზრუნველყავით სუფთა, მინიმალისტური სტრუქტურა და გლუვი მიკრო-ანიმაციები"
            ]
        }

def parse_vault_departments(vault_dir: Path):
    """Parses individual markdown files to extract department structures and agent system prompts."""
    departments = {}
    dep_files = [
        "Cockpit UI UX Studio.md",
        "Data Tech Architecture.md",
        "Cybersecurity Compliance.md",
        "Aftersales CX Analytics.md",
        "RD Lab.md",
        "Innovation Department.md",
        "Archive Department.md",
        "Translation Department.md",
        "Marketing Department.md",
        "Web Reach Department.md"
    ]
    
    for filename in dep_files:
        filepath = vault_dir / "Departments" / filename
        if not filepath.exists():
            continue
            
        dep_name = filename.replace(".md", "")
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            continue
            
        agent_sections = content.split("###")
        agents = []
        for sec in agent_sections[1:]:
            lines = sec.strip().split("\n")
            if not lines:
                continue
            header = lines[0].strip()
            
            # Identify active agents (leading number or contains 'აგენტი'/'agent')
            if not re.search(r'^\d+\.|\bაგენტი\b|\bagent\b', header, re.IGNORECASE):
                continue
                
            # Extract name and English label
            name_match = re.search(r'(?:\d+\s*\.\s*)?(?:[^(\n]+)(?:\((.*?)\))?$', header)
            english_name = name_match.group(1) if name_match and name_match.group(1) else header
            clean_name = re.sub(r'^(?:\d+\s*\.\s*|👤\s*აგენტი:\s*|⚖️\s*აგენტი:\s*|\s*აგენტი:\s*)', '', header).strip()
            
            # Extract system prompt
            code_blocks = re.findall(r'```(?:markdown)?\n([\w\W]*?)```', sec)
            system_prompt = code_blocks[0].strip() if code_blocks else ""
            
            if not system_prompt:
                bq_lines = []
                for line in lines[1:]:
                    if line.strip().startswith(">"):
                        bq_lines.append(line.strip().lstrip(">").strip())
                system_prompt = "\n".join(bq_lines)
                
            # Extract work focus
            focus_match = re.search(r'\*\*\s*სამუშაო ფოკუსი\s*:\s*\*\*(.*)', sec, re.IGNORECASE)
            focus = focus_match.group(1).strip() if focus_match else ""
            if not focus:
                role_match = re.search(r'\*\*\s*роლი\s*:\s*\*\*(.*)', sec, re.IGNORECASE)
                if role_match:
                    focus = role_match.group(1).strip()
            if not focus:
                for l in lines[1:]:
                    if l.strip() and not l.strip().startswith("```") and not l.strip().startswith(">"):
                        focus = l.strip()
                        break
            
            # Fallback if no prompt found
            if not system_prompt:
                system_prompt = f"შენ ხარ Porsche-ს {clean_name}. შენი ფოკუსია: {focus}."
                
            agents.append({
                "name": clean_name,
                "english_name": english_name,
                "focus": focus,
                "system_prompt": system_prompt
            })
            
        departments[dep_name] = {
            "name": dep_name,
            "theme": DEPT_THEMES.get(dep_name, {"color": CLR_GOLD, "hex": "#ffcc00", "icon": "💡"}),
            "agents": agents
        }
    return departments

def keyword_matching_route(idea: str, departments: dict) -> dict:
    """Matches the idea dynamically using pre-mapped keywords."""
    idea_lower = idea.lower()
    best_dep = "Cockpit UI UX Studio"
    best_agent_idx = 0
    max_score = -1
    
    keywords = {
        "Cockpit UI UX Studio": ["ui", "ux", "design", "css", "html", "style", "animation", "visual", "theme", "color", "guards red", "acid green", "gwen", "button", "layout", "დოკუმენტი", "ანიმაცია", "ღილაკი", "დიზაინი", "ფერები"],
        "Data Tech Architecture": ["database", "db", "sql", "supabase", "schema", "table", "backend", "fastapi", "server", "docker", "dockerfile", "hugging face", "space", "porting", "migration", "ბაზა", "სქემა", "api"],
        "Cybersecurity Compliance": ["security", "encryption", "compliance", "key", "token", "auth", "audit", "validation", "safeguard", "hacking", "უსაფრთხოება", "შიფრი", "აუდიტი"],
        "Aftersales CX Analytics": ["analytics", "cx", "experience", "metric", "dashboard", "report", "customer", "feedback", "labor", "time", "rate", "ანალიტიკა", "მომხმარებელი"],
        "RD Lab": ["iot", "telemetry", "obd-ii", "obd", "can-bus", "sensor", "hardware", "ar", "vr", "vision", "camera", "yolo", "კამერა", "ტელემეტრია", "სენსორი", "ობიექტი"],
        "Innovation Department": ["innovation", "optimization", "failover", "rotation", "hosting", "scouting", "next-gen", "ინოვაცია", "ოპტიმიზაცია"],
        "Archive Department": ["archive", "backup", "restore", "ledger", "inactive", "shelved", "tegeta", "piwis", "არქივი", "შენახვა"],
        "Translation Department": ["translation", "georgian", "english", "german", "dictionary", "glossary", "term", "terminology", "თარგმანი", "ქართული", "ენობრივი"],
        "Marketing Department": ["marketing", "brand", "guardian", "identity", "social", "logo", "customer base", "მარკეტინგი", "ბრენდი"],
        "Web Reach Department": ["internet", "web", "scrape", "search", "youtube", "bilibili", "rss", "jina", "crawler", "read-page", "social", "twitter", "reddit", "linkedin", "ინტერნეტ", "ვებ", "ძებნ", "მოიძი", "გაიგე", "ლინკ", "საიტ", "ვიდეო"]
    }
    
    for dep_name, dep_data in departments.items():
        score = 0
        dep_kw = keywords.get(dep_name, [])
        for kw in dep_kw:
            if kw in idea_lower:
                score += 3
        
        for idx, agent in enumerate(dep_data.get("agents", [])):
            agent_score = score
            agent_words = agent["name"].lower() + " " + agent["focus"].lower() + " " + agent["system_prompt"].lower()
            for kw in dep_kw + idea_lower.split():
                if len(kw) >= 3 and kw in agent_words:
                    agent_score += 1
            
            if agent_score > max_score:
                max_score = agent_score
                best_dep = dep_name
                best_agent_idx = idx
                
    dep_info = departments.get(best_dep, departments["Cockpit UI UX Studio"])
    agent_info = dep_info["agents"][best_agent_idx]
    
    # Domain Detection & Customization
    domain_data = detect_domain(idea)
    
    standard_checklist = [
        f"შეისწავლეთ იდეის მოთხოვნები: '{idea[:60]}...'",
        f"გაეცანით {best_dep} დეპარტამენტის და აგენტის ({agent_info['name']}) ოპერაციულ SOP წესებს",
        "მოამზადეთ ტექნიკური გადაწყვეტილების დეტალური გეგმა (Implementation Plan)"
    ]
    
    # Inject domain specific checklist items
    checklist = standard_checklist + domain_data["extra_checklist"] + [
        "განახორციელეთ კოდის მოდიფიკაცია და ლოკალური ტესტირება",
        "წარუდგინეთ Walkthrough რეპორტი მომხმარებელს და ატვირთეთ არქივში"
    ]
    
    # Merge styling rules into system prompt
    enriched_prompt = f"{domain_data['styling_rules']}\n\n{agent_info['system_prompt']}"
    
    return {
        "department": best_dep,
        "agent": agent_info["name"],
        "theme_color": dep_info["theme"]["hex"],
        "system_prompt": f"დავალება: {idea}\n\n{enriched_prompt}",
        "task_checklist": checklist,
        "domain_name": domain_data["name"]
    }

def main():
    vault_dir = Path(__file__).parent.resolve()
    
    print(f"{CLR_BOLD}{CLR_BLUE}======================================================================{CLR_RESET}")
    print(f"{CLR_BOLD}🏛️ AI SOFTWARE HOUSE AGENTIC DISPATCHER & ROUTER{CLR_RESET}")
    print(f"{CLR_BOLD}{CLR_BLUE}======================================================================{CLR_RESET}\n")
    
    # 1. Read idea input
    idea = ""
    if len(sys.argv) > 1:
        idea = " ".join(sys.argv[1:])
    else:
        print(f"{CLR_BOLD}გთხოვთ, აღწეროთ თქვენი იდეა ან ახალი ფუნქციონალი:{CLR_RESET}")
        try:
            idea = input("> ").strip()
        except KeyboardInterrupt:
            print("\nოპერაცია გაუქმებულია.")
            sys.exit(0)
            
    if not idea:
        print(f"{CLR_RED}შეცდომა: იდეის აღწერა ცარიელია!{CLR_RESET}")
        sys.exit(1)
        
    # 2. Parse departments from vault md files
    print(f"{CLR_GREY}ობსიდიანის ვოლტის სკანირება მიმდინარეობს...{CLR_RESET}")
    departments = parse_vault_departments(vault_dir)
    if not departments:
        print(f"{CLR_RED}შეცდომა: დეპარტამენტის ფაილები ვერ მოიძებნა vault root-ში!{CLR_RESET}")
        sys.exit(1)
        
    # 3. Route idea (with dynamic local keyword classifier)
    print(f"{CLR_GREY}კლასიფიკაცია და ოპტიმალური აგენტის შერჩევა...{CLR_RESET}")
    routed = keyword_matching_route(idea, departments)
    
    dep_name = routed["department"]
    agent_name = routed["agent"]
    theme = DEPT_THEMES.get(dep_name, {"color": CLR_GOLD, "hex": "#ffcc00", "icon": "💡"})
    color = theme["color"]
    icon = theme["icon"]
    
    # 4. Print beautiful terminal report
    print(f"\n{color}----------------------------------------------------------------------{CLR_RESET}")
    print(f"{color}{CLR_BOLD}🎯 ROUTING BLUEPRINT / აგენტური გადანაწილების ბარათი{CLR_RESET}")
    print(f"{color}----------------------------------------------------------------------{CLR_RESET}")
    print(f"{CLR_BOLD}პროექტის დომენი (Domain):{CLR_RESET} {CLR_BOLD}{CLR_GREEN}{routed['domain_name']}{CLR_RESET}")
    print(f"{CLR_BOLD}დეპარტამენტი (Department):{CLR_RESET} {color}{icon} {dep_name}{CLR_RESET}")
    print(f"{CLR_BOLD}შემსრულებელი აგენტი (Agent):{CLR_RESET} {color}{agent_name}{CLR_RESET}")
    print(f"{CLR_BOLD}თემის ფერი (Theme Color):{CLR_RESET} {color}{theme['hex']}{CLR_RESET}")
    print(f"----------------------------------------------------------------------")
    print(f"{CLR_BOLD}📋 სამოქმედო გეგმა (SOP task.md Checklist):{CLR_RESET}")
    for idx, task in enumerate(routed["task_checklist"], 1):
        print(f"  {color}[ ]{CLR_RESET} {task}")
    print(f"----------------------------------------------------------------------")
    
    # 5. Write active routing note in Obsidian Vault
    output_filename = "Idea Dispatcher Output.md"
    output_path = vault_dir / output_filename
    
    markdown_content = f"""# 🎯 Active Dispatch Card: {agent_name}
 
> [!NOTE]
> **დეპარტამენტი:** {icon} **{dep_name}**
> **პასუხისმგებელი აგენტი:** `{agent_name}`
> **პროექტის დომენი:** `{routed['domain_name']}`
> **მიზანი:** მომხმარებლის ახალი იდეის განხორციელება უმაღლეს დონეზე.

---

## 💡 იდეის აღწერა (Feature Request)
> "{idea}"

---

## 🤖 სუბაგენტის სისტემური პრომპტი (Subagent System Prompt)
```markdown
{routed["system_prompt"]}
```

---

## 📋 სამოქმედო გეგმა (`task.md` Checklist)
ამ იდეის წარმატებით განსახორციელებლად სუბაგენტმა უნდა შეასრულოს შემდეგი ნაბიჯები:
"""
    for task in routed["task_checklist"]:
        markdown_content += f"- [ ] {task}\n"
        
    markdown_content += f"""
---
*ბარათი მომზადდა ავტომატურად: AI Software House Agentic Dispatcher*
"""
    
    try:
        with open(output_path, 'w', encoding='utf-8') as of:
            of.write(markdown_content)
        print(f"{CLR_GREEN}✔ Obsidian ბარათი წარმატებით ჩაიწერა: {CLR_BOLD}{output_filename}{CLR_RESET}")
    except Exception as we:
        print(f"{CLR_RED}შეცდომა ბარათის ჩაწერისას: {we}{CLR_RESET}")
        
    print(f"{color}======================================================================{CLR_RESET}\n")

if __name__ == "__main__":
    main()
