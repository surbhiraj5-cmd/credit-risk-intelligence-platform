# Credit Risk Intelligence Platform
### Autonomous multi-agent AI system for credit portfolio risk analysis

Built with Claude API (Anthropic) · Python 3.12 · Multi-agent orchestration · RAG

---

## What this does

This platform replaces what a 4-person credit risk analytics team does manually every week — scoring users, detecting anomalies, writing executive briefs, and answering portfolio questions — with a fully autonomous 4-agent AI pipeline.

One command. One CSV. Full portfolio intelligence in minutes.

---

## Agent architecture

```
users.csv
    │
    ▼
┌─────────────────────┐
│  Agent 1            │  Scores each user out of 100 using income,
│  Credit Scorer      │  EMI ratio, missed payments, utilization
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Agent 2            │  Compares scores vs last week, flags changes
│  Anomaly Detector   │  >10pts as Critical / High / Medium alerts
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Agent 3            │  Reads entire portfolio output and writes a
│  Portfolio          │  CFO-level weekly brief with risk signals,
│  Summariser         │  segment analysis and strategic actions
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Agent 4            │  Interactive Q&A — ask any question about
│  Q&A Analyst        │  your portfolio in plain English (RAG-based)
└─────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  Outputs                                │
│  · credit_analysis_YYYYMMDD_HHMM.csv   │
│  · anomaly_alerts_YYYYMMDD_HHMM.csv    │
│  · cfo_portfolio_brief_YYYYMMDD_HHMM.txt│
└─────────────────────────────────────────┘
```

---

## Sample output

**Agent 1 — Credit scoring**
```
🔍 Analysing U001...
  ✅ Score: 72/100 | Risk: Low | Prev: 78/100

🔍 Analysing U008...
  ✅ Score: 19/100 | Risk: High | Prev: 28/100
  🚨 ANOMALY | Level: Critical | Change: -9 pts
     → Severe score deterioration driven by 4 missed payments and 94% credit utilization
     → Action: Freeze credit line immediately and escalate to risk committee
```

**Agent 3 — CFO portfolio brief (excerpt)**
```
PORTFOLIO HEALTH SUMMARY
Portfolio average score declined 4.2 pts week-on-week to 68/100,
driven by utilization spikes in the lower-income segment (₹32k–55k/month).

KEY RISK SIGNALS
• 30% of users are now high risk — up from 20% last week
• U008 is critical: 4 missed payments + 94% utilization signal imminent default
• U005 and U010 trending high risk — intervention window closing

RECOMMENDED STRATEGIC ACTIONS
1. Freeze credit line for U008 immediately
2. Trigger auto-debit nudges for U005 and U010
3. Tighten acquisition criteria for income band ₹32k–45k
```

**Agent 4 — Interactive Q&A**
```
❓ Your question: Which users are most likely to default in 60 days?

💡 Based on current scores and trends, U008 (score 19, 4 missed payments,
   94% utilization) is at highest default risk. U003 (score 28, 3 missed
   payments, 88% utilization) follows closely. Both require immediate
   intervention — combined they represent 20% of the portfolio.
```

---

## Tech stack

| Layer | Technology |
|-------|-----------|
| LLM | Claude claude-sonnet-4-6 (Anthropic API) |
| Language | Python 3.12 |
| Agent pattern | Sequential multi-agent orchestration |
| Q&A pattern | RAG (context injection into model) |
| Output format | Structured JSON extraction + narrative generation |
| Data layer | CSV → Python → structured pipeline |
| Error handling | Retry logic with exponential backoff (529/overload) |
| Output | CSV (Tableau-ready) + TXT executive brief |

---

## Prerequisites

- Python 3.10 or higher
- Anthropic API key ([get one here](https://console.anthropic.com))
- ~$0.05–0.10 in API credits per full portfolio run

---

## Setup

**1. Clone the repo**
```bash
git clone https://github.com/YOUR_USERNAME/credit-risk-intelligence-platform.git
cd credit-risk-intelligence-platform
```

**2. Install dependencies**
```bash
pip install anthropic
```

**3. Add your API key**

Open `credit_risk_platform.py` and replace:
```python
client = anthropic.Anthropic(api_key="YOUR_API_KEY_HERE")
```

**4. Prepare your data**

Create a `users.csv` file in the project root with this structure:

```csv
user_id,monthly_income,emi_amount,missed_payments,credit_utilization,payment_streak
U001,45000,8500,0,28,18
U002,72000,15000,1,52,10
U003,38000,12000,3,88,2
```

Column definitions:
- `monthly_income` — user's monthly income in ₹
- `emi_amount` — total monthly EMI obligations in ₹
- `missed_payments` — number of missed payments in last 6 months
- `credit_utilization` — current credit utilization as a percentage
- `payment_streak` — consecutive months of on-time payments

**5. Run**
```bash
python credit_risk_platform.py
```

---

## Output files

Each run generates timestamped files in the project root:

| File | Contents |
|------|----------|
| `credit_analysis_YYYYMMDD_HHMM.csv` | Full scoring results for all users — import into Tableau |
| `anomaly_alerts_YYYYMMDD_HHMM.csv` | Flagged users only, with alert level and recommended actions |
| `cfo_portfolio_brief_YYYYMMDD_HHMM.txt` | Executive brief ready to share with leadership |

---

## Customising the platform

**Change the anomaly threshold**

In `detect_anomaly()`, adjust the sensitivity:
```python
if abs(score_change) <= 10:  # change to 5 for more sensitive, 15 for less
```

**Add more users**

The platform scales to any number of users. Add rows to `users.csv` and re-run. For large portfolios (500+ users), consider Anthropic's Batch API for async processing.

**Update last week's scores**

Replace the `last_week_scores` dictionary with your previous week's output CSV data to track real week-on-week changes:
```python
last_week_scores = {
    "U001": 78,
    "U002": 61,
    ...
}
```

---

## Project structure

```
credit-risk-intelligence-platform/
│
├── credit_risk_platform.py   # Main pipeline — all 4 agents
├── users.csv                 # Input data (add your own)
├── README.md                 # This file
│
└── outputs/                  # Generated on each run
    ├── credit_analysis_*.csv
    ├── anomaly_alerts_*.csv
    └── cfo_portfolio_brief_*.txt
```

---

## Key concepts demonstrated

**Multi-agent orchestration** — Four specialised agents with distinct roles, each passing structured output to the next agent in the pipeline.

**Prompt engineering** — Strict JSON schema enforcement, role-based prompting, output constraint design for production reliability.

**RAG (Retrieval Augmented Generation)** — Agent 4 injects the full portfolio dataset into Claude's context window to enable grounded, data-specific answers rather than generalised responses.

**Structured output extraction** — JSON parsing from LLM responses with error handling and graceful fallbacks.

**Production reliability** — Retry logic with exponential backoff handles API rate limits and overload errors (HTTP 529).

---

## Business impact

This platform automates the weekly workflow of a credit risk analytics team:

| Task | Manual effort | This platform |
|------|--------------|---------------|
| Scoring 10 users | ~2 hours | ~3 minutes |
| Anomaly detection | ~1 hour | Automatic |
| Executive brief | ~2 hours | ~30 seconds |
| Ad-hoc questions | ~30 min per query | Instant |
| **Total** | **~5 hours/week** | **~4 minutes/week** |

## Author
Surbhi Raj Bahadur
Analytics Manager · 9+ years in fintech, product analytics and BI
[LinkedIn](https://linkedin.com/in/surbhiraj) · Bengaluru, India
