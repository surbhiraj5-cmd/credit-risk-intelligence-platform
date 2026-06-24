import anthropic
import csv
import json
import time
from datetime import datetime

client = anthropic.Anthropic(api_key="ANTHROPIC_API_KEY")

# ============================================================
# SIMULATED LAST WEEK'S SCORES
# ============================================================
last_week_scores = {
    "U001": 78, "U002": 61, "U003": 34, "U004": 88,
    "U005": 52, "U006": 91, "U007": 65, "U008": 28,
    "U009": 83, "U010": 58
}


# ============================================================
# AGENT 1: CREDIT SCORING AGENT (with retry)
# ============================================================
def score_user(user, retries=3):
    for attempt in range(retries):
        try:
            message = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=500,
                messages=[
                    {
                        "role": "user",
                        "content": f"""You are a credit health analyst. Respond ONLY with a raw JSON object.
No markdown, no backticks, no explanation. Just the JSON.

User data:
- Monthly income: {user['monthly_income']}
- EMI amount: {user['emi_amount']}
- Missed payments last 6 months: {user['missed_payments']}
- Credit utilization: {user['credit_utilization']}%
- Payment streak: {user['payment_streak']} months

Return exactly this structure:
{{"credit_score": 72, "risk_level": "Medium", "emi_to_income_pct": 18.5, "top_issue": "High utilization", "recommendation": "Reduce credit card usage"}}"""
                    }
                ]
            )

            response_text = message.content[0].text.strip()
            if not response_text:
                return None
            if "```" in response_text:
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
            return json.loads(response_text.strip())

        except Exception as e:
            if "overloaded" in str(e).lower() or "529" in str(e):
                wait_time = (attempt + 1) * 10
                print(f"  ⏳ Server busy, retrying in {wait_time}s... (attempt {attempt + 1}/{retries})")
                time.sleep(wait_time)
            else:
                print(f"  ❌ Unexpected error in score_user: {e}")
                return None

    print(f"  ⚠️ Failed after {retries} attempts - skipping user")
    return None


# ============================================================
# AGENT 2: ANOMALY DETECTION AGENT (with retry)
# ============================================================
def detect_anomaly(user_id, current_score, previous_score, retries=3):
    score_change = current_score - previous_score

    if abs(score_change) <= 10:
        return {
            "anomaly_detected": False,
            "score_change": score_change,
            "alert_level": "None",
            "alert_message": "Score stable",
            "urgent_action": "No action needed"
        }

    for attempt in range(retries):
        try:
            message = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=400,
                messages=[
                    {
                        "role": "user",
                        "content": f"""You are a credit risk anomaly detection agent.

User {user_id} credit score changed from {previous_score} to {current_score} (change: {score_change:+d} points).

Respond ONLY with raw JSON, no markdown, no backticks:

{{"anomaly_detected": true, "score_change": {score_change}, "alert_level": "Critical/High/Medium", "alert_message": "one sentence explaining what happened", "urgent_action": "one sentence on what the risk team should do immediately"}}"""
                    }
                ]
            )

            response_text = message.content[0].text.strip()
            if "```" in response_text:
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
            return json.loads(response_text.strip())

        except Exception as e:
            if "overloaded" in str(e).lower() or "529" in str(e):
                wait_time = (attempt + 1) * 10
                print(f"  ⏳ Server busy, retrying in {wait_time}s... (attempt {attempt + 1}/{retries})")
                time.sleep(wait_time)
            else:
                print(f"  ❌ Unexpected error in detect_anomaly: {e}")
                break

    return {
        "anomaly_detected": True,
        "score_change": score_change,
        "alert_level": "High",
        "alert_message": f"Score changed by {score_change:+d} points",
        "urgent_action": "Manual review required"
    }


# ============================================================
# AGENT 3: PORTFOLIO SUMMARISER AGENT (with retry)
# ============================================================
def generate_portfolio_brief(results, anomalies, retries=3):
    print("\n🤖 Agent 3: Generating CFO-level Portfolio Brief...\n")

    portfolio_data = []
    for r in results:
        portfolio_data.append({
            "user_id": r["user_id"],
            "current_score": r["current_score"],
            "previous_score": r["previous_score"],
            "score_change": r["score_change"],
            "risk_level": r["risk_level"],
            "top_issue": r["top_issue"],
            "credit_utilization": r["credit_utilization"],
            "missed_payments": r["missed_payments"],
            "monthly_income": r["monthly_income"]
        })

    low_risk = sum(1 for r in results if r['risk_level'] == 'Low')
    medium_risk = sum(1 for r in results if r['risk_level'] == 'Medium')
    high_risk = sum(1 for r in results if r['risk_level'] == 'High')
    avg_score = round(sum(r['current_score'] for r in results) / len(results), 1)
    avg_last_week = round(sum(r['previous_score'] for r in results) / len(results), 1)
    critical_alerts = [a for a in anomalies if a['alert_level'] == 'Critical']

    for attempt in range(retries):
        try:
            message = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=1000,
                messages=[
                    {
                        "role": "user",
                        "content": f"""You are a senior credit risk analyst writing a weekly portfolio brief for the CFO and Head of Risk.

Portfolio data:
- Total users: {len(results)}
- Average score THIS week: {avg_score}/100
- Average score LAST week: {avg_last_week}/100
- Low Risk: {low_risk} | Medium Risk: {medium_risk} | High Risk: {high_risk}
- Critical anomalies: {len(critical_alerts)} | Total anomalies: {len(anomalies)}

Individual data:
{json.dumps(portfolio_data, indent=2)}

Write a sharp executive brief with these sections:

1. PORTFOLIO HEALTH SUMMARY (2-3 sentences)
2. KEY RISK SIGNALS (3 bullet points)
3. SEGMENT ANALYSIS (which users are driving risk)
4. ANOMALIES & URGENT ACTIONS (critical users and actions)
5. RECOMMENDED STRATEGIC ACTIONS (3 concrete actions for this week)

Be sharp, data-driven, no fluff. Use actual numbers."""
                    }
                ]
            )
            return message.content[0].text.strip()

        except Exception as e:
            if "overloaded" in str(e).lower() or "529" in str(e):
                wait_time = (attempt + 1) * 10
                print(f"  ⏳ Server busy, retrying in {wait_time}s... (attempt {attempt + 1}/{retries})")
                time.sleep(wait_time)
            else:
                print(f"  ❌ Unexpected error in portfolio brief: {e}")
                break

    return "Portfolio brief could not be generated due to server issues. Please retry."


# ============================================================
# AGENT 4: INTERACTIVE Q&A AGENT (with retry)
# ============================================================
def interactive_qa(results, anomalies, portfolio_brief):
    print("\n" + "=" * 60)
    print("   🤖 AGENT 4: INTERACTIVE PORTFOLIO Q&A")
    print("   Ask anything about your credit portfolio.")
    print("   Type 'exit' to quit.")
    print("=" * 60)

    portfolio_context = {
        "total_users": len(results),
        "avg_score_this_week": round(sum(r['current_score'] for r in results) / len(results), 1),
        "avg_score_last_week": round(sum(r['previous_score'] for r in results) / len(results), 1),
        "risk_breakdown": {
            "low": sum(1 for r in results if r['risk_level'] == 'Low'),
            "medium": sum(1 for r in results if r['risk_level'] == 'Medium'),
            "high": sum(1 for r in results if r['risk_level'] == 'High')
        },
        "anomalies_flagged": len(anomalies),
        "critical_anomalies": [a for a in anomalies if a['alert_level'] == 'Critical'],
        "all_users": results,
        "all_anomalies": anomalies
    }

    conversation_history = []

    system_prompt = f"""You are an expert credit risk analyst with access to a portfolio of {len(results)} users.

Here is the complete portfolio data:
{json.dumps(portfolio_context, indent=2)}

Here is the weekly portfolio brief already generated:
{portfolio_brief}

Answer questions clearly and concisely using actual numbers from the data.
When referencing users, always mention their user_id and key metrics.
If asked for recommendations, be specific and actionable.
Keep answers under 150 words unless the question needs more detail."""

    print("\n💡 Example questions you can ask:")
    print("   → Which users are most likely to default in 60 days?")
    print("   → What is the average score for high risk users?")
    print("   → Which user had the biggest score drop this week?")
    print("   → What percentage of my portfolio is high risk?")
    print("   → Which users should I prioritise for intervention?")
    print("   → What is the most common risk driver across all users?")
    print()

    while True:
        user_question = input("❓ Your question: ").strip()

        if user_question.lower() in ['exit', 'quit', 'q']:
            print("\n✅ Exiting Q&A. Goodbye!")
            break

        if not user_question:
            print("   Please type a question or 'exit' to quit.\n")
            continue

        conversation_history.append({
            "role": "user",
            "content": user_question
        })

        print("   🤔 Thinking...\n")

        for attempt in range(3):
            try:
                message = client.messages.create(
                    model="claude-sonnet-4-6",
                    max_tokens=400,
                    system=system_prompt,
                    messages=conversation_history
                )
                answer = message.content[0].text.strip()
                conversation_history.append({
                    "role": "assistant",
                    "content": answer
                })
                print(f"   💡 {answer}\n")
                print("-" * 60)
                break

            except Exception as e:
                if "overloaded" in str(e).lower() or "529" in str(e):
                    wait_time = (attempt + 1) * 10
                    print(f"  ⏳ Server busy, retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print(f"  ❌ Error: {e}")
                    break


# ============================================================
# MAIN PIPELINE
# ============================================================
users = []
with open('users.csv', 'r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        users.append(row)

print("=" * 60)
print("   CREDIT RISK INTELLIGENCE PLATFORM v3.0")
print("   4 Agents: Score | Anomaly | CFO Brief | Q&A")
print("=" * 60)
print(f"\nLoaded {len(users)} users. Starting analysis...\n")

results = []
anomalies = []

for user in users:
    user_id = user['user_id']
    print(f"🔍 Analysing {user_id}...")

    # AGENT 1
    analysis = score_user(user)
    if not analysis:
        print(f"  ⚠️ Skipping {user_id} - scoring failed")
        time.sleep(2)
        continue

    current_score = analysis['credit_score']
    previous_score = last_week_scores.get(user_id, current_score)
    print(f"  ✅ Score: {current_score}/100 | Risk: {analysis['risk_level']} | Prev: {previous_score}/100")

    # AGENT 2
    anomaly = detect_anomaly(user_id, current_score, previous_score)
    if anomaly['anomaly_detected']:
        alert_icon = "🚨" if anomaly['alert_level'] == "Critical" else "⚠️"
        print(f"  {alert_icon} ANOMALY | Level: {anomaly['alert_level']} | Change: {anomaly['score_change']:+d} pts")
        print(f"     → {anomaly['alert_message']}")
        print(f"     → Action: {anomaly['urgent_action']}")
        anomalies.append({**{"user_id": user_id}, **anomaly})
    else:
        print(f"  ✅ No anomaly | Change: {anomaly['score_change']:+d} pts")

    results.append({
        "user_id": user_id,
        "monthly_income": user['monthly_income'],
        "emi_amount": user['emi_amount'],
        "missed_payments": user['missed_payments'],
        "credit_utilization": user['credit_utilization'],
        "payment_streak": user['payment_streak'],
        "previous_score": previous_score,
        "current_score": current_score,
        "score_change": anomaly['score_change'],
        "risk_level": analysis['risk_level'],
        "emi_to_income_pct": analysis['emi_to_income_pct'],
        "top_issue": analysis['top_issue'],
        "recommendation": analysis['recommendation'],
        "anomaly_detected": anomaly['anomaly_detected'],
        "alert_level": anomaly['alert_level'],
        "alert_message": anomaly['alert_message'],
        "urgent_action": anomaly['urgent_action']
    })

    print()
    time.sleep(2)  # pause between users to avoid rate limits

# ============================================================
# AGENT 3: PORTFOLIO BRIEF
# ============================================================
if results:
    portfolio_brief = generate_portfolio_brief(results, anomalies)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M')

    # Save main CSV
    output_filename = f"credit_analysis_{timestamp}.csv"
    with open(output_filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    # Save anomalies CSV
    if anomalies:
        anomaly_filename = f"anomaly_alerts_{timestamp}.csv"
        with open(anomaly_filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=anomalies[0].keys())
            writer.writeheader()
            writer.writerows(anomalies)

    # Save CFO brief
    brief_filename = f"cfo_portfolio_brief_{timestamp}.txt"
    with open(brief_filename, 'w') as f:
        f.write("CREDIT RISK INTELLIGENCE PLATFORM\n")
        f.write(f"Weekly Portfolio Brief — {datetime.now().strftime('%d %B %Y')}\n")
        f.write("=" * 60 + "\n\n")
        f.write(portfolio_brief)

    # Print brief to screen
    print("=" * 60)
    print("   CFO PORTFOLIO BRIEF")
    print("=" * 60)
    print(portfolio_brief)

    print(f"\n📁 Files saved:")
    print(f"   → {output_filename}")
    if anomalies:
        print(f"   → {anomaly_filename}")
    print(f"   → {brief_filename}")

    # AGENT 4
    interactive_qa(results, anomalies, portfolio_brief)

else:
    print("\n⚠️ No results — check errors above")
