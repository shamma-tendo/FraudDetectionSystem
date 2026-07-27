# Real-Time Fraud Detection System — Manual

**Project category:** Real-Time Fraud Detection System (Django)
**Group:** K

## 1. What this application does

The system watches financial transactions (transfers, payments, withdrawals,
deposits) as they come in, screens each one against a set of configurable
rules, and raises an alert when a transaction looks suspicious — for
example, an unusually large amount, a burst of transactions in a short
window, an out-of-place location, or activity at odd hours. Staff review
flagged transactions and alerts from a live dashboard.

Since a class project has no real bank feed to connect to, a management
command (`simulate_transactions`) generates realistic-looking transactions
on a timer so the dashboard has something to react to during your
supervision session and presentation.

## 2. How to run it

```
cd pimis_fraud
python -m venv venv
venv\Scripts\activate            # Windows
source venv/bin/activate         # Mac/Linux
pip install -r requirements.txt
python manage.py runserver
```

The project ships with the database already migrated and seeded, so this
is all that's needed to see it working immediately:

- Visit **http://127.0.0.1:8000/** — redirects to the dashboard login
- Log in with **username `admin`, password `Admin@Fraud2026`**
- Or visit **/admin/** with the same credentials for the Django admin panel

To watch it react in real time, open a second terminal:

```
python manage.py simulate_transactions --interval 3
```

This creates one random transaction every 3 seconds (about a quarter of
them deliberately suspicious) so the "Live alerts" panel on the dashboard
updates on its own without you refreshing the page.

If you ever want to start from a clean database instead of the seeded
demo data:

```
rm db.sqlite3
python manage.py migrate
python manage.py loaddata default_rules
python manage.py createsuperuser
```

## 3. Project structure

```
pimis_fraud/
├── manage.py
├── requirements.txt
├── db.sqlite3                  # pre-seeded demo database
├── fraud_detection/            # project settings & root URLs
│   ├── settings.py
│   └── urls.py
├── transactions/               # Account + Transaction models
│   ├── models.py
│   ├── admin.py
│   └── management/commands/simulate_transactions.py
├── detection/                  # the anomaly detection engine
│   ├── models.py               # DetectionRule, RuleMatch
│   ├── services.py             # rule-checking logic
│   ├── signals.py              # runs the engine on every new transaction
│   └── fixtures/default_rules.json
├── alerts/                     # Alert model, raised automatically
│   ├── models.py
│   └── signals.py
├── dashboard/                  # the staff-facing web UI
│   ├── views.py
│   └── urls.py
├── templates/
│   ├── dashboard/              # dashboard pages
│   └── registration/login.html
└── static/dashboard/css/style.css
```

## 4. Architecture — how a transaction flows through the system

1. A `Transaction` row is created (by the simulator, or later in the future however
   we decide for example wiring in a real source later — a form, an API, a CSV import).
2. Saving the transaction fires a Django **signal** (`detection/signals.py`),
   which immediately runs `detection/services.py::evaluate_transaction`.
3. That function checks the transaction against every **active**
   `DetectionRule` row. Each rule that fires adds its `weight` to a running
   score, and a `RuleMatch` record is saved explaining *why* it fired.
4. If the total score reaches 60 or more, the transaction's `status`
   becomes `FLAGGED`; otherwise `CLEARED`.
5. A second signal (`alerts/signals.py`) checks the just-saved status. If
   it's `FLAGGED`, it creates an `Alert` with a severity (`HIGH` / `MEDIUM`
   / `LOW`) based on the score.
6. The dashboard reads `Transaction` and `Alert` data to render stats, the
   recent-transactions table, and the live alert feed. The alert feed also
   polls a small JSON endpoint (`/dashboard/poll-alerts/`) every 4 seconds
   so newly created alerts appear without a manual page refresh.

This satisfies all four features asked for in the assignment brief:

| Requirement | Where it's implemented |
|---|---|
| Data monitoring | `transactions` app — every transaction is logged and screened the instant it's created |
| Anomaly detection | `detection` app — configurable, weighted rule engine |
| Alerts & notifications | `alerts` app — auto-created on flagged transactions, shown live on the dashboard |
| Dashboard | `dashboard` app — stats, chart, transaction table, alert feed, all built with Bootstrap 5 |

## 5. Data model reference

### `transactions.Account`
Represents a bank account/customer being monitored.
| Field | Type | Notes |
|---|---|---|
| `account_number` | CharField, unique | e.g. `ACC1001` |
| `holder_name` | CharField | |
| `usual_location` | CharField | Baseline location used by the "unusual location" rule |
| `created_at` | DateTimeField | auto |

### `transactions.Transaction`
A single financial event.
| Field | Type | Notes |
|---|---|---|
| `id` | UUIDField, primary key | |
| `account` | ForeignKey → Account | |
| `transaction_type` | choice: TRANSFER / PAYMENT / WITHDRAWAL / DEPOSIT | |
| `amount` | DecimalField | UGX |
| `location` | CharField | Where this specific transaction occurred |
| `counterparty` | CharField, optional | Recipient/merchant |
| `timestamp` | DateTimeField | auto, when the row was created |
| `status` | choice: PENDING / CLEARED / FLAGGED | set by the detection engine |
| `risk_score` | PositiveSmallInteger, 0–100 | set by the detection engine |

### `detection.DetectionRule`
A configurable rule. **Editable live from `/admin/detection/detectionrule/`** —
no code changes or restart needed to tune thresholds.
| Field | Notes |
|---|---|
| `code` | HIGH_AMOUNT / VELOCITY / UNUSUAL_LOCATION / ODD_HOURS |
| `is_active` | toggle a rule on/off |
| `weight` | points added to `risk_score` when it fires |
| `amount_threshold` | used by HIGH_AMOUNT |
| `velocity_window_minutes` / `velocity_max_count` | used by VELOCITY |
| `odd_hours_start` / `odd_hours_end` | used by ODD_HOURS |

Seeded defaults (from `detection/fixtures/default_rules.json`):
- **High amount**: ≥ 5,000,000 UGX → +40
- **Velocity**: more than 3 transactions in 10 minutes on the same account → +30
- **Unusual location**: transaction location differs from the account's usual location → +35
- **Odd hours**: transaction between 1am–4am → +15

A transaction reaches `FLAGGED` at a combined score of 60+ (defined as
`FLAG_THRESHOLD` in `detection/services.py`).

### `detection.RuleMatch`
Audit trail: which rule fired on which transaction, and why (human-readable
note, e.g. "Amount 18392425 >= threshold 5000000.00"). This is what powers
the "why it was scored this way" breakdown on the transaction detail page.

### `alerts.Alert`
| Field | Notes |
|---|---|
| `transaction` | OneToOne → Transaction |
| `severity` | HIGH (score ≥ 85) / MEDIUM (≥ 60) / LOW |
| `message` | auto-generated summary |
| `is_resolved`, `resolved_by`, `resolved_at` | set when staff click "Mark resolved" |

## 6. Dashboard pages

- **Overview** (`/dashboard/`) — stat cards (transactions today, flagged
  today, volume, open alerts), a risk-distribution doughnut chart, a
  live-polling alert feed, and a table of recent transactions.
- **Transactions** (`/dashboard/transactions/`) — full list with combined
  filters: status, transaction type, and free-text search across account
  number, holder name, and location.
- **Transaction detail** (`/dashboard/transactions/<id>/`) — full
  transaction info plus the exact list of rules that fired and their
  point contributions.
- **Alerts** (`/dashboard/alerts/`) — open alerts by default, with a
  toggle to include resolved ones, and a "Mark resolved" action per alert.
- **Detection rules** (`/dashboard/rules/`) — read-only view of current
  rule configuration, with a link to the admin page where they're edited.
- **Accounts** (`/dashboard/accounts/`) — monitored accounts and their
  transaction counts.
- **Admin panel** (`/admin/`) — full CRUD on every model, useful for
  demoing rule changes live or adding accounts.

## 7. Login credentials (demo data)

| Username | Password | Role |
|---|---|---|
| `admin` | `Admin@Fraud2026` | Superuser — works for both `/admin/` and the dashboard |

Demo accounts seeded in the database: `ACC1001`–`ACC1005`, based in
Kampala, Gulu, Mbarara, Jinja, and Entebbe respectively.
