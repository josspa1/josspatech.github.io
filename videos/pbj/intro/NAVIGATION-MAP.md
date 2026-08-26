# PocketBudJet — Navigation Map (for Maestro crawl / QA)

Saved 2026-07-10 for later device navigation testing.  
Source: `PBJ/SourceCode` — run `npm run audit:navigation` before ship.

**Maestro root:** `PBJ/SourceCode/.maestro/`  
**Mirror:** this file is copied to `.maestro/NAVIGATION-MAP.md` when building flows.

---

## Scale

| Surface | Count |
|---------|------:|
| Stack screens (`screenRegistry.tsx`) | ~140 |
| SCREENS constants | ~149 |
| Toolbox tools | 29 |
| ContextualActions screens | 24 |
| UniversalSearchBar features | 20 |
| navConfig footer/cross-links | 80 screens |
| Press targets in screens (approx.) | ~3,500 |

## What Maestro covers today

| Preset | Flow file | Touches |
|--------|-----------|---------|
| `test:e2e:sample` | `sample-import-home.yaml` | Import Center → sample import → Home |
| `test:e2e:tour` | `screen-tour.yaml` | 5 tabs, Toolbox → Import Center search |
| `test:e2e:preship` | preship preset | sample + home + paywall dismiss |
| `test:e2e:nav-crawl` | `navigation-toolbox-crawl.yaml` (generated) | All 29 Toolbox tools open + back |

**Not covered:** in-screen tabs, row actions, modals, ContextualActions chips, UniversalSearch results, ~110 stack screens never opened.

---

## Conventions for future flows

| Item | Rule |
|------|------|
| **Prerequisite** | Most flows assume `sample-import-home.yaml` has run (sample data on device). Tag `activated`. |
| **Cold / onboarding** | Separate tag `cold` — use `clearState` only on sacrificial device (`PBJ_CAPTURE_PM_CLEAR=1`). |
| **Tab taps** | Samsung-safe points: Home `10%,93%` · Activity `30%,93%` · Budget `50%,93%` · Goals `72%,93%` · Coach `93%,93%` |
| **Subflows** | Always start with `launch-app` → `dismiss-notification-prompt` → `dismiss-quick-tour` → `wait-home` → `dismiss-unlock` |
| **Back** | Prefer `Navigate up` then tab-point fallback |
| **Deep links** | `openLink: pocketbudjet://{path}` — fallback to Toolbox search if link fails |
| **Premium gates** | Use Settings → 7-tap tester unlock → Simulate Premium before gated screens |
| **File layout** | One YAML per major area under `.maestro/flows/` (see plan below) |

### Planned `.maestro/flows/` layout

```
.maestro/
  config.yaml
  subflows/                    # shared setup (existing)
  sample-import-home.yaml      # prerequisite runner
  navigation-toolbox-crawl.yaml
  flows/
    01-onboarding-cold.yaml
    02-home-dashboard.yaml
    03-activity-transactions.yaml
    04-budget-planning.yaml
    05-goals-debt.yaml
    06-coach-insights.yaml
    07-import-center.yaml
    08-subscriptions-bills.yaml
    09-bank-connections.yaml
    10-settings-account.yaml
    11-reports-tax.yaml
    12-household-sync.yaml
    13-search-discovery.yaml
    14-contextual-chips.yaml
```

Run all (future): `npm run test:e2e:flows` → runs `flows/*.yaml` after sample import.

---

## Tab bar (MainTabs)

| Label | Route | Deep link | Tab point |
|-------|-------|-----------|-----------|
| Home | Dashboard | `home` | `10%,93%` |
| Activity | Transactions | `money` | `30%,93%` |
| Budget | Budget | `plan` | `50%,93%` |
| Goals | Debt (GoalsTabScreen) | `goals` | `72%,93%` |
| Coach | Reports (CoachTabScreen) | `insights` | `93%,93%` |

Header: Search, Coach, Toolbox (non-Home tabs), Settings (Activity+).

---

## Maestro flow plan — per major screen

Each block = one future flow file. **Navigate** = how to open; **Assert** = must-see text; **Tap audit** = in-screen controls that must respond (regression targets).

---

### `flows/01-onboarding-cold.yaml`

**Tag:** `cold` · **Prerequisite:** sacrificial device, `launchApp` with `clearState: true`

| Step | Action | Assert |
|------|--------|--------|
| Splash | auto | PocketBudJet or splash |
| Feature showcase | swipe / Continue | Terms or showcase copy |
| Terms | scroll, Accept | Security setup or wizard |
| Security setup | skip or set PIN | Setup wizard or MainTabs |
| Skip tour | `dismiss-quick-tour` | Home visible |

**Tap audit:** Accept, Continue, Skip, Maybe later on every gate. Do not tap Allow on notifications.

---

### `flows/02-home-dashboard.yaml`

**Tag:** `activated` · **Prerequisite:** sample import  
**Navigate:** `wait-home` or `openLink: pocketbudjet://home`

| Area | Assert | Tap audit |
|------|--------|-----------|
| Hero / concierge | PocketBudJet title | Search icon → Universal Search; Coach sparkle → CoachChat |
| Home carousel | Swipe or wait | Each panel: hero, Sankey, donut, **weekly patterns**, monthly health, bills calendar — verify panel title visible |
| Weekly patterns card | "Weekly patterns" or day-of-week bars | Carousel dot advances; bar chart visible |
| FAB | pencil FAB | Transaction hub or contextual action opens |
| Glance cards | Weekly Recap, subscription burn, etc. | Each card CTA navigates (tap → new screen → back) |
| Set default checkbox | "Set default" on carousel | Toggle responds |

**Deep link smoke:** `pocketbudjet://home`

---

### `flows/03-activity-transactions.yaml`

**Navigate:** tab `30%,93%` or `openLink: pocketbudjet://money`

| Screen | How to open | Assert | Tap audit |
|--------|-------------|--------|-----------|
| Transactions list | tab | Activity / transaction rows | Row → TransactionDetail; filter chips; search |
| TransactionDetail | tap first row | amount, category | ContextualActions chips: Categories, Merchant, Rules |
| TransactionHub | FAB or header add | Add / hub options | Each hub entry opens |
| AddTransaction | hub or search | form fields | Save / cancel |
| CalendarView | header or menu | calendar grid | Day tap → list |
| NaturalSearch | search bar | search UI | Submit query |
| ApproveTransactions | badge or menu if shown | pending list | Approve / reject |
| ScanReceipt | Toolbox | camera / scan UI | Back without crash |
| Settings entry | header Settings | Settings title | (hands off to flow 10) |

**Deep links:** `money`, `add`, `calendar`, `search`, `scan`

---

### `flows/04-budget-planning.yaml`

**Navigate:** tab `50%,93%` or `openLink: pocketbudjet://plan`

| Screen | How to open | Assert | Tap audit |
|--------|-------------|--------|-----------|
| Budget tab root | tab | Budget / envelopes | Category row drill-down |
| BudgetLimits | Budget → limits or Toolbox | limits list | Adjust limit modal |
| BudgetTargets | FAB on Budget tab | targets UI | Add target |
| BudgetHealth | ContextualActions or Reports | health score | Footer chips navigate |
| SpendingPlan | nav footer / ContextualActions | plan view | Links work |
| CategoryManager | Toolbox "Categories" | category list | Edit category |
| BudgetTemplates | Toolbox | template list | Apply template (optional) |
| SinkingFunds | Toolbox "Savings Pots" | pots list | Add pot modal |
| Goals (stack) | Toolbox or Goals chip | goals list | Goal detail |
| GoalDetail | tap goal | progress chart | Edit / contribute |
| AnnualBudget | search or ReportHub | annual view | Footer links |
| PaycheckAllocationRules | Settings or Budget | rules list | Toggle rule |
| OtherBucketCleanup | deep link or menu | cleanup UI | Dismiss / act |

**Deep links:** `plan`, `budget-limits`, `categories`, `savings-pots`, `annual-budget`

---

### `flows/05-goals-debt.yaml`

**Navigate:** tab `72%,93%` or `openLink: pocketbudjet://goals`

| Screen | How to open | Assert | Tap audit |
|--------|-------------|--------|-----------|
| Goals tab root | tab | Goals / debt summary | Empty-state CTA opens modal |
| DebtAccounts | tab section or Toolbox | debt list | Row → CreditCardDetail |
| AddDebt | + or empty CTA | add form | Save |
| DebtStrategy | debt menu | strategy UI | Switch snowball/avalanche |
| DebtPayoffComparison | ContextualActions | comparison chart | Footer chips |
| WhatIf | Toolbox | scenario UI | Add scenario |
| LoanCalculator | Toolbox | calculator fields | Calculate |
| DebtProgressReport | Coach or Reports | progress chart | Footer chips |
| CreditCardDetail | tap card debt | card detail | Payoff CTA |

**Deep links:** `goals`, `debts`, `debt-strategy`, `what-if`, `loan-calc`

---

### `flows/06-coach-insights.yaml`

**Navigate:** tab `93%,93%` or `openLink: pocketbudjet://insights`

| Screen | How to open | Assert | Tap audit |
|--------|-------------|--------|-----------|
| Coach tab root | tab | Coach / insights segments | Segment tabs switch |
| Coach (stack) | Toolbox "AI Coach" | tips / segments | ContextualActions: Budget, Goals, Debt |
| CoachChat / Ask PBJ | header sparkle or Toolbox "Ask PBJ" | chat composer | Suggested chip **sends** message (not draft-only) |
| WeeklyRecap | Toolbox | recap card | Footer: Coach, Debt |
| MoneyTwin | Toolbox | twin UI | Back |
| FinancialLiteracy | Toolbox | lesson list | Open lesson |
| PeerBenchmark | Toolbox | benchmark UI | Back |
| ReportHub | search "Reports" | report tiles | Each tile opens report |
| MerchantAnalysis | TransactionDetail chip | merchant chart | Back |
| MarginBreakdown | search "Margin" | margin view | Back |
| CustomReport | Toolbox | builder UI | Save / preview |

**Deep links:** `insights`, `coach`, `assistant`, `recap`, `report-hub`, `margin`

---

### `flows/07-import-center.yaml`

**Navigate:** `openLink: pocketbudjet://import` or Toolbox → Import Center  
**Extends:** existing `sample-import-home.yaml`

| Step | Assert | Tap audit |
|------|--------|-----------|
| Import Center idle | Try sample statement | Sample card tap |
| Map columns | Map Columns | Continue |
| Import confirm | Import N transactions | Import button |
| Complete | Import complete | See Home CTA |
| ImportHistory | menu / link | history list | Row detail |
| EmailForwarding | Toolbox or Tax hub | forwarding instructions | Back |
| ScannerImport | Toolbox scan paths | scanner UI | Back |
| NotificationCapture | Toolbox | capture UI | Back |

**Deep links:** `import`, `import-history`, `email-forwarding`

---

### `flows/08-subscriptions-bills.yaml`

**Priority:** regression for Subscription Tracker tab bug (2026-07-10)

| Screen | Navigate | Assert | Tap audit |
|--------|----------|--------|-----------|
| SubscriptionTracker | Toolbox or `subscriptions` | Subscription Tracker title | **Subscriptions tab** → **Bank fees tab** → **Subscriptions tab again** (both must respond) |
| Subscriptions tab | default | Smart Scan, Netflix/sub rows | Confirm / Not a subscription; **Find how to cancel** link |
| Bank fees tab | tap Bank fees | "No bank fees" or fee list | **Subscriptions tab** must work after empty fees state |
| RecurringTransactions | ContextualActions on Sub Tracker | recurring list | Back |
| Bills | Toolbox or `bills` | bills calendar | Add bill modal; empty-state CTA |
| BillsAndRecurringHub | deep link `bills-recurring` | hub tabs | Switch tabs |
| Recurring forecast | Bills footer chip | forecast screen | Back |

**Deep links:** `subscriptions`, `bills`, `bills-recurring`

---

### `flows/09-bank-connections.yaml`

**Navigate:** Settings → Bank Sync, or `openLink: pocketbudjet://connect-bank-quiltt`  
**Note:** paywall may appear — use `onboarding-trial-paywall.yaml` dismiss pattern

| Screen | Assert | Tap audit |
|--------|--------|-----------|
| ConnectBank (Quiltt) | connect UI | Maybe later / dismiss paywall |
| BankConnections | connections list | Done button; row expand |
| ConnectBankTeller | alternate path | WebView loads / back |
| FinancialSources | Settings accounts | account list | Add source |
| GlassPaywall | gated feature | Dismiss without purchase |

**Deep links:** `connect-bank-quiltt`, `connect-bank`, `connections`, `accounts`

---

### `flows/10-settings-account.yaml`

**Navigate:** Activity tab → Settings, or `openLink: pocketbudjet://settings`

| Screen | How to open | Assert | Tap audit |
|--------|-------------|--------|-----------|
| Settings root | header | Settings | Each row navigates |
| Profile | Settings | profile fields | Save |
| Subscription | Settings | plan / restore | Back |
| BackupRestore | Settings or Toolbox | backup UI | Export trigger (optional) |
| NotificationPreferences | Settings | toggles | Toggle responds |
| HelpSupport | Settings / drawer | help list | Show me around → tour |
| WhatsNew | Settings | changelog | Back |
| HowPBJLearns | Settings | explainer | Back |
| TransactionRules | Toolbox / Settings | rules list | Add rule |
| Labels | drawer MANAGE | labels list | Add label |
| Achievements | Toolbox | badges | Back |
| LegalDoc | Settings legal row | legal text | Back |
| WidgetSmartWatch | Toolbox | widget config | Back |
| DataManagement | Settings | data tools | Back |
| Simulate Premium | 7-tap version unlock | tester toggles | Enable for gated flows |

**Deep links:** `settings`, `profile`, `subscription`, `backup`, `help`, `rules`, `labels`

---

### `flows/11-reports-tax.yaml`

**Navigate:** Coach tab, ReportHub, or Toolbox exports

| Screen | Navigate | Assert | Tap audit |
|--------|----------|--------|-----------|
| TaxHub | search / hub | tax tiles | Each sub-screen opens |
| TaxExport | Toolbox | export options | Export button (dry run) |
| TaxMileage | Tax hub | mileage log | Add trip |
| Export | Toolbox "Export Data" | export formats | Cancel |
| NetWorthHub | search | net worth | Assets link |
| NetWorthAssets | footer chip | assets list | Add asset |
| ProjectedBalance | reports | balance chart | Footer: Bills, BudgetLimits |
| FinancialHealthScore | reports / credit | score gauge | Footer chips |
| SpendingForecast | reports / bills chip | forecast chart | Footer chips |
| YearOverYear | report hub | YoY chart | Back |
| AnomalyDashboard | hub | anomalies | Back |
| CarbonFootprint | Toolbox | carbon UI | Back |
| InvestmentPortfolio | Toolbox | portfolio | Back |

**Deep links:** `tax`, `tax-export`, `mileage`, `export`, `net-worth`, `projected`, `score`

---

### `flows/12-household-sync.yaml`

| Screen | Navigate | Assert | Tap audit |
|--------|----------|--------|-----------|
| Household | Settings | household intro | Couples Dashboard chip |
| CouplesDashboard | chip | dashboard | Back |
| PartnerSync | household flow | sync UI | Back |
| CouplesPairKey | `pair-key` | pairing code | Back |
| HouseholdHub | deep link | hub tiles | Back |

**Deep links:** `household`, `pair-key`

---

### `flows/13-search-discovery.yaml`

**Navigate:** header Search on any tab

| Step | Assert | Tap audit |
|------|--------|-----------|
| Open search | UniversalSearch modal | input visible |
| Each FEATURE_INDEX row | type keyword from map | result tap → correct screen → back |
| No-match fallback | type `zzzznotfound` | routes to CoachChat with prompt |
| UniversalSearchBar (Home inline) | Home search widget | top feature chips navigate |
| Toolbox search | Toolbox → Search tools | filter tools list |

Keywords to script (from UniversalSearchBar): income, goals, transactions, budget, subscriptions, bills, forecast, debt, reports, import, net worth, settings, backup.

---

### `flows/14-contextual-chips.yaml`

**Prerequisite:** sample import + navigate to host screen first  
**Purpose:** every ContextualActions footer chip — see list in § ContextualActions below

| Host screen | Chips to tap | Expect navigation |
|-------------|--------------|-------------------|
| ProjectedBalance | View Bills, Adjust Budget | Bills, BudgetLimits |
| FinancialHealthScore | Budget, Debt Payoff, Set Goals | tab or stack |
| SubscriptionTracker | Recurring | RecurringTransactions |
| TransactionDetail | Categories, Merchant View, Rules | each opens |
| … | (full list below) | assert `Navigate up` then next chip |

Run as one flow per host screen or single marathon with back between each.

---

## Toolbox tools (Maestro crawl list)

**Earn:** Investment Portfolio, Equity Tracking, Loan Calculator, Direct Deposit Advisor  
**Save:** Savings Pots, Carbon Footprint  
**Spend:** Subscription Tracker, Import Center, Scan Receipt, Scan Document, Notification Capture, Categories, Smart Rules, Voice Shortcuts  
**Plan:** Budget Templates, What-If, Money Twin, Insurance Policies, Credit Score, Tax Export, Widget & Smartwatch  
**Reflect:** Coach, Custom Reports, AI Coach, Weekly Recap, Financial Literacy, Achievements, Peer Benchmark, Export  

Covered by `navigation-toolbox-crawl.yaml` (open only). Future: merge tap-audit columns from flows above into each toolbox stop.

---

## ContextualActions (footer chips)

ProjectedBalance → Bills, BudgetLimits  
FinancialHealthScore → Budget, DebtAccounts, Goals  
SpendingForecast → BudgetLimits, Coach  
TaxReturn → TaxExport  
AnnualBudget → BudgetLimits, BudgetHealth  
BudgetHealth → BudgetLimits, Goals  
NetWorthHistory → NetWorthAssets  
DebtProgressReport → DebtAccounts, DebtPayoffComparison, WhatIf  
DebtPayoffComparison → DebtAccounts, DebtStrategy, WhatIf  
PaycheckDetail / PayStubReview → RecurringIncome  
Coach → Budget, Goals, Debt  
WeeklyRecap → Coach, Debt  
Household → CouplesDashboard  
CategoryManager → Reports (Coach tab)  
BudgetLimits → BudgetHealth, SpendingPlan  
BudgetTemplates → BudgetLimits  
SubscriptionTracker → RecurringTransactions  
Bills → SpendingForecast  
CalendarView → Transactions  
FinancialSources → ImportCenter  
TransactionDetail → CategoryManager, MerchantAnalysis, TransactionRules  
CreditScore → FinancialHealthScore, Subscription  

---

## UniversalSearchBar routes

Income, Goals, Transactions, Add Transaction, Budget, Categories, Subscriptions, Bills, Forecast, Find Your Margin, Debt, Reports, Custom Reports, AI Coach, Spending patterns, Import, Net worth, Toolbox, Settings, Privacy, Backup & restore.

---

## Static CI checks

```bash
cd PBJ/SourceCode
npm run audit:navigation   # dead routes, GlassHeader overlay warnings, wiring
npm run focus:check        # includes audit:navigation
```

---

## Device crawl (when ready)

```bash
cd PBJ/SourceCode
npm run test:e2e:sample      # activate sample data first
npm run test:e2e:nav-crawl   # all Toolbox entries (open + back)
# Future:
npm run test:e2e:flows       # all flows/*.yaml after sample import
```

---

## Build order (suggested)

1. **`08-subscriptions-bills.yaml`** — Subscription Tracker tab regression (known bug class)
2. **`02-home-dashboard.yaml`** — carousel / weekly patterns visible
3. **`07-import-center.yaml`** — already partially covered; extract from sample-import
4. **`14-contextual-chips.yaml`** — high-value dead-link detection
5. **`13-search-discovery.yaml`** — 20 keyword routes
6. Remaining flows by tab (03–06, 10–12, 11)
7. **`01-onboarding-cold.yaml`** — sacrificial device only

---

## Known bug class (2026-07-10)

**GlassHeader overlay stealing taps** on pinned tab bars when `topOffset` drops to 0 — fixed Subscription Tracker; `audit:navigation` warns on similar patterns. **Maestro flow 08** must assert Subscriptions ↔ Bank fees tab round-trip.

---

## Partner showcase (this folder)

Separate from app QA — English Quiltt deck only. Do not confuse with how-to videos or 8-locale work.
