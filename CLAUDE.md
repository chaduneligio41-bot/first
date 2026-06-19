# 🏛️ AI Software House — Workspace Guide

ეს არის საერთო, მრავალაგენტიანი workspace. ამ folder-ზე **ერთდროულად მუშაობენ Claude Code და Antigravity** — იმავე ფაილებზე, დისკზე. მიზანი: მომხმარებელთან ერთად პროექტებზე მუშაობა, ერთმანეთის ნამუშევრის ხედვა და გადამოწმება.

---

## 👥 ვინ რას აკეთებს (როლები)

- **Claude Code (Anthropic):** Backend / API / OCR / FastAPI ინჟინერია, კოდის რევიუ.
- **Antigravity (Google):** UI/UX დიზაინი, სისტემური ოპტიმიზაცია, Supabase, ვერიფიკაცია.
- სრული რუკა: `Central AI Team/Central AI Team.md`

## 🤝 თანამშრომლობის წესები (ორივე AI-სთვის)

1. **ერთ ფაილს ერთდროულად ნუ შეცვლი** — ჯერ წაიკითხე (ბოლო ვერსია), მერე დაარედაქტირე. ბოლო ჩამწერი აწერს.
2. **მნიშვნელოვანი გადაწყვეტილება ჩაწერე shared დოკში** (`Council.md` ან `Departments/Archive Department.md`), რომ მეორე AI-მაც დაინახოს — საერთო მეხსიერება ფაილებშია, არა ცალკეულ სესიაში.
3. **სესიის ბოლოს გაუშვი არქივატორი:** `python scripts/session-end-archiver.py` → ანახლებს `Archive Department.md`-ის ჟურნალს.
4. **დაიცავი მრჩევლის წესები** (`AGENTS.md`): კრიტიკული აზროვნება, თავდაჯერებულობის მარკერები `[Certain] / [Likely] / [Guessing]`, არასოდეს მოიგონო ფაქტი ან შესრულებული ქმედება.

## 🧭 მთავარი ფაილები

- `Central AI Team/` — ბირთვი: `dispatcher.py` (იდეას აგენტზე ამისამართებს), `agent_runner.py` (Gemini/Claude ძრავი), `Council.md` (5 მრჩეველი).
- `Central AI Team/Departments/` — 10 სპეციალიზებული დეპარტამენტი.
- `.claude/agents/` — რევიუერები: `ui-ux-reviewer`, `supabase-reviewer`, `glossary-verifier`.
- `.claude/rules/common/` — `brand_rules.md`, `operations_rules.md`.

## 🛠️ Commands

```bash
# იდეის დარუტება
cd "Central AI Team"; python dispatcher.py "აღწერე იდეა"
# აგენტების გაშვება
cd "Central AI Team"; python agent_runner.py
# სესიის არქივი
python scripts/session-end-archiver.py
```

## ⚠️ გარემო (Admin მანქანა)

- ენა: ქართული მისაღებია.
- **git ამ მანქანაზე PATH-ზე არ არის** — სანამ git არ დაყენდება, კოორდინაცია ხდება shared ფაილებით, არა git commit-ებით.
- ეს folder Claude-ის ყველა სესიაშია ხელმისაწვდომი (`~/.claude/settings.json` → `permissions.additionalDirectories`).
