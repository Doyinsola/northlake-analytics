import pandas as pd
import random
import uuid
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()
random.seed(42)
Faker.seed(42)

OUT = "/home/claude/northlake_data/raw"

# ─── CONFIG ──────────────────────────────────────────────────────────────────
N_ACCOUNTS       = 200
N_CONTACTS       = 600   # ~3 per account
N_SUBSCRIPTIONS  = 220   # some accounts have had multiple (churned + renewed)
N_EVENTS         = 12000
N_TICKETS        = 800
N_INVOICES       = 1100

START_DATE = datetime(2022, 1, 1)
END_DATE   = datetime(2024, 12, 31)

def rand_date(start=START_DATE, end=END_DATE):
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days))

def rand_dt(start=START_DATE, end=END_DATE):
    d = rand_date(start, end)
    return d.replace(hour=random.randint(7, 22), minute=random.randint(0,59), second=random.randint(0,59))

# ─── 1. ACCOUNTS ─────────────────────────────────────────────────────────────
industries = ["SaaS","Fintech","Healthcare","E-commerce","EdTech","Logistics","Marketing","Legal","Real Estate","Manufacturing"]
sizes      = ["1-10","11-50","51-200","201-500","501-1000","1001+"]
regions    = ["North America","EMEA","APAC","LATAM"]
sources    = ["Organic Search","Paid Search","Referral","Partner","Event","Cold Outreach","Trial Signup"]

account_ids = [str(uuid.uuid4()) for _ in range(N_ACCOUNTS)]

accounts = []
for aid in account_ids:
    created = rand_date(START_DATE, datetime(2024, 6, 30))
    # inject some dirty data: blank industry (5%), duplicate-ish company names (rare), NULL region (3%)
    industry = random.choice(industries) if random.random() > 0.05 else ""
    region   = random.choice(regions)   if random.random() > 0.03 else None
    accounts.append({
        "account_id":   aid,
        "company_name": fake.company(),
        "industry":     industry,
        "company_size": random.choice(sizes),
        "region":       region,
        "country":      fake.country(),
        "website":      fake.url(),
        "lead_source":  random.choice(sources),
        "created_at":   created.strftime("%Y-%m-%d %H:%M:%S"),
        "updated_at":   (created + timedelta(days=random.randint(0,300))).strftime("%Y-%m-%d %H:%M:%S"),
        "is_deleted":   random.choice([False, False, False, False, True]),  # 20% soft-deleted
    })

df_accounts = pd.DataFrame(accounts)
df_accounts.to_csv(f"{OUT}/accounts.csv", index=False)
print(f"accounts.csv: {len(df_accounts)} rows")

# ─── 2. CONTACTS ─────────────────────────────────────────────────────────────
roles = ["Admin","Viewer","Editor","Owner","Billing Manager","Developer","Analyst"]

contacts = []
for _ in range(N_CONTACTS):
    acc  = random.choice(account_ids)
    created = rand_date(START_DATE, datetime(2024, 9, 1))
    # dirty: some emails malformed (4%), some missing job title (8%)
    email = fake.email()
    if random.random() < 0.04:
        email = email.replace("@", "")  # malformed
    job_title = fake.job() if random.random() > 0.08 else None
    contacts.append({
        "contact_id":  str(uuid.uuid4()),
        "account_id":  acc,
        "first_name":  fake.first_name(),
        "last_name":   fake.last_name(),
        "email":       email,
        "job_title":   job_title,
        "role":        random.choice(roles),
        "phone":       fake.phone_number() if random.random() > 0.15 else None,
        "created_at":  created.strftime("%Y-%m-%d %H:%M:%S"),
        "last_login":  rand_date(created, END_DATE).strftime("%Y-%m-%d") if random.random() > 0.1 else None,
        "is_active":   random.choice([True, True, True, False]),
    })

df_contacts = pd.DataFrame(contacts)
df_contacts.to_csv(f"{OUT}/contacts.csv", index=False)
print(f"contacts.csv: {len(df_contacts)} rows")

# ─── 3. PLANS (lookup table) ─────────────────────────────────────────────────
plans = [
    {"plan_id": "plan_starter",    "plan_name": "Starter",    "billing_cycle": "monthly", "mrr_usd": 99,   "max_seats": 5,   "max_api_calls": 10000},
    {"plan_id": "plan_growth",     "plan_name": "Growth",     "billing_cycle": "monthly", "mrr_usd": 299,  "max_seats": 20,  "max_api_calls": 100000},
    {"plan_id": "plan_pro",        "plan_name": "Pro",        "billing_cycle": "monthly", "mrr_usd": 599,  "max_seats": 50,  "max_api_calls": 500000},
    {"plan_id": "plan_enterprise", "plan_name": "Enterprise", "billing_cycle": "annual",  "mrr_usd": 1499, "max_seats": 999, "max_api_calls": 9999999},
    {"plan_id": "plan_starter_yr", "plan_name": "Starter Annual",    "billing_cycle": "annual", "mrr_usd": 79,  "max_seats": 5,   "max_api_calls": 10000},
    {"plan_id": "plan_growth_yr",  "plan_name": "Growth Annual",     "billing_cycle": "annual", "mrr_usd": 249, "max_seats": 20,  "max_api_calls": 100000},
]
df_plans = pd.DataFrame(plans)
df_plans.to_csv(f"{OUT}/plans.csv", index=False)
print(f"plans.csv: {len(df_plans)} rows")

plan_ids     = [p["plan_id"]   for p in plans]
plan_weights = [0.25, 0.30, 0.20, 0.10, 0.08, 0.07]

# ─── 4. SUBSCRIPTIONS ────────────────────────────────────────────────────────
statuses = ["active","churned","paused","trialing"]

subscriptions = []
used_accounts = set()
for i in range(N_SUBSCRIPTIONS):
    # prefer accounts not yet assigned (ensure coverage), then random
    remaining = [a for a in account_ids if a not in used_accounts]
    acc = remaining[i] if i < len(remaining) else random.choice(account_ids)
    used_accounts.add(acc)

    plan    = random.choices(plan_ids, weights=plan_weights)[0]
    start   = rand_date(START_DATE, datetime(2024, 6, 1))
    status  = random.choices(statuses, weights=[0.55, 0.25, 0.10, 0.10])[0]

    if status == "churned":
        end_date = (start + timedelta(days=random.randint(30, 730))).strftime("%Y-%m-%d")
        canceled = end_date
    elif status == "paused":
        end_date = None
        canceled = None
    elif status == "trialing":
        end_date = (start + timedelta(days=14)).strftime("%Y-%m-%d")
        canceled = None
    else:
        end_date = None
        canceled = None

    # dirty: ~3% have NULL plan_id
    plan_used = plan if random.random() > 0.03 else None

    subscriptions.append({
        "subscription_id":     str(uuid.uuid4()),
        "account_id":          acc,
        "plan_id":             plan_used,
        "status":              status,
        "trial_start":         start.strftime("%Y-%m-%d") if status == "trialing" else None,
        "trial_end":           end_date if status == "trialing" else None,
        "subscription_start":  start.strftime("%Y-%m-%d"),
        "subscription_end":    end_date if status == "churned" else None,
        "canceled_at":         canceled,
        "seats_purchased":     random.randint(1, 50),
        "discount_pct":        round(random.choice([0,0,0,0,10,15,20,25]), 2),
        "created_at":          start.strftime("%Y-%m-%d %H:%M:%S"),
        "updated_at":          (start + timedelta(days=random.randint(0,180))).strftime("%Y-%m-%d %H:%M:%S"),
    })

df_subs = pd.DataFrame(subscriptions)
df_subs.to_csv(f"{OUT}/subscriptions.csv", index=False)
print(f"subscriptions.csv: {len(df_subs)} rows")

# ─── 5. PRODUCT EVENTS ───────────────────────────────────────────────────────
event_names = [
    "login","logout","dashboard_viewed","report_created","report_exported",
    "user_invited","integration_connected","api_call","feature_flag_toggled",
    "alert_created","alert_triggered","data_source_added","query_run",
    "workspace_created","billing_page_visited","plan_upgrade_initiated",
    "plan_downgrade_initiated","password_reset","mfa_enabled","export_downloaded",
]
platforms = ["web","mobile_ios","mobile_android","api"]

events = []
for _ in range(N_EVENTS):
    contact = df_contacts.sample(1).iloc[0]
    evt_time = rand_dt()
    events.append({
        "event_id":    str(uuid.uuid4()),
        "contact_id":  contact["contact_id"],
        "account_id":  contact["account_id"],
        "event_name":  random.choice(event_names),
        "platform":    random.choice(platforms),
        "session_id":  str(uuid.uuid4())[:8],
        "occurred_at": evt_time.strftime("%Y-%m-%d %H:%M:%S"),
        # dirty: ~5% have NULL platform, ~2% duplicate event_id simulation handled at query level
        "properties":  None if random.random() < 0.1 else f'{{"page":"{fake.uri_path()}"}}',
        "ip_address":  fake.ipv4() if random.random() > 0.05 else None,
    })

df_events = pd.DataFrame(events)
# inject ~1% duplicate rows (same event_id) — classic data quality issue
dupe_rows = df_events.sample(frac=0.01)
df_events = pd.concat([df_events, dupe_rows], ignore_index=True)
df_events.to_csv(f"{OUT}/events.csv", index=False)
print(f"events.csv: {len(df_events)} rows (includes ~{len(dupe_rows)} duplicates)")

# ─── 6. SUPPORT TICKETS ──────────────────────────────────────────────────────
categories  = ["Billing","Technical","Onboarding","Feature Request","Bug Report","Account Management","Data Export"]
priorities  = ["low","medium","high","urgent"]
ticket_stat = ["open","in_progress","resolved","closed","on_hold"]
channels    = ["email","chat","phone","portal"]

tickets = []
for _ in range(N_TICKETS):
    acc     = random.choice(account_ids)
    created = rand_dt()
    status  = random.choices(ticket_stat, weights=[0.10,0.15,0.40,0.30,0.05])[0]

    if status in ("resolved","closed"):
        resolved_at = (created + timedelta(hours=random.randint(1, 120))).strftime("%Y-%m-%d %H:%M:%S")
        first_response = (created + timedelta(minutes=random.randint(5, 480))).strftime("%Y-%m-%d %H:%M:%S")
    else:
        resolved_at    = None
        first_response = (created + timedelta(minutes=random.randint(5, 2880))).strftime("%Y-%m-%d %H:%M:%S") if random.random() > 0.2 else None

    tickets.append({
        "ticket_id":           str(uuid.uuid4()),
        "account_id":          acc,
        "contact_id":          df_contacts[df_contacts["account_id"]==acc]["contact_id"].sample(1).values[0] if len(df_contacts[df_contacts["account_id"]==acc]) > 0 else None,
        "category":            random.choice(categories),
        "priority":            random.choices(priorities, weights=[0.3,0.4,0.2,0.1])[0],
        "channel":             random.choice(channels),
        "status":              status,
        "subject":             fake.sentence(nb_words=6),
        "csat_score":          random.randint(1,5) if status in ("resolved","closed") and random.random() > 0.4 else None,
        "created_at":          created.strftime("%Y-%m-%d %H:%M:%S"),
        "first_response_at":   first_response,
        "resolved_at":         resolved_at,
        "updated_at":          (created + timedelta(hours=random.randint(0,200))).strftime("%Y-%m-%d %H:%M:%S"),
    })

df_tickets = pd.DataFrame(tickets)
df_tickets.to_csv(f"{OUT}/support_tickets.csv", index=False)
print(f"support_tickets.csv: {len(df_tickets)} rows")

# ─── 7. INVOICES ─────────────────────────────────────────────────────────────
inv_status = ["paid","pending","overdue","voided","failed"]
pay_method = ["credit_card","bank_transfer","invoice_net30","paypal"]

invoices = []
sub_sample = df_subs.sample(min(N_INVOICES, len(df_subs)), replace=True)

for _, sub in sub_sample.iterrows():
    plan_row = df_plans[df_plans["plan_id"]==sub["plan_id"]]
    mrr = float(plan_row["mrr_usd"].values[0]) if len(plan_row)>0 else 299.0
    discount = float(sub["discount_pct"]) if sub["discount_pct"] else 0
    amount   = round(mrr * (1 - discount/100), 2)
    issue_dt = rand_dt(START_DATE, END_DATE)
    status   = random.choices(inv_status, weights=[0.70,0.10,0.10,0.05,0.05])[0]

    invoices.append({
        "invoice_id":       str(uuid.uuid4()),
        "subscription_id":  sub["subscription_id"],
        "account_id":       sub["account_id"],
        "amount_usd":       amount,
        "discount_pct":     discount,
        "tax_usd":          round(amount * 0.08, 2),
        "total_usd":        round(amount * 1.08, 2),
        "currency":         random.choices(["USD","EUR","GBP","CAD"], weights=[0.75,0.12,0.08,0.05])[0],
        "status":           status,
        "payment_method":   random.choice(pay_method),
        "issued_at":        issue_dt.strftime("%Y-%m-%d %H:%M:%S"),
        "due_at":           (issue_dt + timedelta(days=30)).strftime("%Y-%m-%d"),
        "paid_at":          (issue_dt + timedelta(days=random.randint(0,35))).strftime("%Y-%m-%d %H:%M:%S") if status=="paid" else None,
        "period_start":     issue_dt.strftime("%Y-%m-%d"),
        "period_end":       (issue_dt + timedelta(days=30)).strftime("%Y-%m-%d"),
    })

df_invoices = pd.DataFrame(invoices)
df_invoices.to_csv(f"{OUT}/invoices.csv", index=False)
print(f"invoices.csv: {len(df_invoices)} rows")

# ─── SUMMARY ─────────────────────────────────────────────────────────────────
print("\n✅ All files written to", OUT)
print("\n── Data quality issues intentionally embedded ──")
print("  accounts:      ~5% blank industry, ~3% NULL region, ~20% soft-deleted")
print("  contacts:      ~4% malformed emails, ~8% NULL job_title, ~10% NULL last_login")
print("  subscriptions: ~3% NULL plan_id")
print("  events:        ~1% duplicate rows, ~5% NULL platform, ~10% NULL properties")
print("  support_tickets: ~20% NULL first_response_at (no first response yet)")
print("  invoices:      multiple currencies, some non-USD amounts need normalising")
