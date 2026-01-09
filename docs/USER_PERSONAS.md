# User Personas - Azure Security Platform V2

## Overview

This document outlines five key personas representing the primary audience for the Azure Security Platform V2 dashboard. Each persona has distinct objectives, needs, pain points, and usage patterns.

---

## Persona 1: Marcus Chen — Chief Information Security Officer (CISO)

### Demographics
- **Age:** 48
- **Role:** CISO at a mid-market financial services firm (800 employees)
- **Reports to:** CEO and Board of Directors
- **Experience:** 20+ years in IT, 12 years in security leadership
- **Technical Level:** Strategically technical; understands concepts but delegates implementation

### Background
Marcus transitioned from IT Director to CISO five years ago after his company experienced a minor ransomware incident. He's responsible for the organization's entire security posture and reports quarterly to the board. He manages a team of 4 security staff and coordinates with IT operations.

### Objectives
1. **Board Communication:** Translate technical security metrics into business risk language
2. **Budget Justification:** Demonstrate ROI on security investments to secure continued funding
3. **Risk Reduction:** Systematically lower organizational risk exposure year-over-year
4. **Compliance Maintenance:** Ensure SOC 2 and PCI-DSS compliance for client trust
5. **Incident Prevention:** Avoid becoming the next breach headline

### Needs
| Need | Priority | Current Pain |
|------|----------|--------------|
| Single-pane security view | Critical | Currently pulls from 6+ tools manually |
| Board-ready metrics | Critical | Spends 2 days/quarter creating reports |
| Trend visualization | High | Can't easily show improvement over time |
| Peer benchmarking | High | No way to compare against industry |
| Executive summary PDF | Medium | Creates PowerPoints from scratch |

### Pain Points
- "I spend more time gathering data than analyzing it"
- "The board asks 'are we secure?' and I don't have a simple answer"
- "I can't prove our security investments are working"
- "After the ransomware scare, leadership wants constant reassurance on backups"

### Dashboard Usage
- **Primary View:** Executive Dashboard
- **Frequency:** Weekly review, deep-dive before board meetings
- **Key Metrics:** Security Score, Compliance %, Backup Health, Top Risks
- **Actions:** Export PDF reports, track trend lines, compare to targets
- **Time Spent:** 30 min/week, 2-3 hours before quarterly board meeting

### Success Metrics for Marcus
- Board presentation prep time reduced from 2 days to 2 hours
- Confidence score when answering board questions: 4/5 → 5/5
- Able to show 6-month improvement trend in single chart
- Zero "I don't know" responses in board meetings

### Quote
> "I need to walk into the board room with confidence. When they ask if we're protected against ransomware, I need a clear answer backed by data—not a 45-minute technical explanation."

---

## Persona 2: Sarah Mitchell — IT Security Analyst

### Demographics
- **Age:** 31
- **Role:** Senior Security Analyst at a healthcare organization (2,000 employees)
- **Reports to:** IT Security Manager
- **Experience:** 7 years in IT, 4 years in security
- **Technical Level:** Highly technical; hands-on daily

### Background
Sarah is the go-to person for security operations. She monitors alerts, investigates incidents, runs vulnerability scans, and handles the day-to-day security work. She's studying for her CISSP and often feels overwhelmed by the volume of alerts across multiple tools.

### Objectives
1. **Alert Triage:** Quickly identify and prioritize real threats vs. noise
2. **Vulnerability Remediation:** Track and close vulnerabilities within SLA
3. **Compliance Evidence:** Gather evidence for HIPAA audits efficiently
4. **MFA Enforcement:** Get the last 15% of users enrolled in MFA
5. **Career Growth:** Demonstrate measurable impact for promotion

### Needs
| Need | Priority | Current Pain |
|------|----------|--------------|
| Unified alert queue | Critical | Switches between 4 consoles constantly |
| Vulnerability tracking | Critical | Spreadsheet with 500+ rows |
| MFA gap identification | High | Manual AD queries weekly |
| Audit trail access | High | Digs through logs for auditors |
| Remediation time tracking | Medium | No way to measure MTTR |

### Pain Points
- "I have alert fatigue—too many tools, too many false positives"
- "I can never find who DOESN'T have MFA when executives ask"
- "Auditors ask for evidence and I spend days pulling logs"
- "I know which devices are non-compliant, but fixing them is someone else's job"

### Dashboard Usage
- **Primary View:** IT Staff Dashboard
- **Frequency:** Multiple times daily
- **Key Sections:** Alert Queue, Vulnerabilities, MFA Gaps, Non-Compliant Devices
- **Actions:** Filter/sort alerts, export CVE lists, identify MFA gaps by department
- **Time Spent:** 2-3 hours/day

### Success Metrics for Sarah
- Alert triage time reduced by 50%
- Single source for all security alerts
- Audit evidence gathering: days → hours
- Clear accountability metrics for her annual review

### Quote
> "I don't need another dashboard—I need THE dashboard. One place where I can see what's on fire, what's smoldering, and what I fixed last week."

---

## Persona 3: David Okonkwo — MSP Security Practice Lead

### Demographics
- **Age:** 39
- **Role:** Director of Security Services at a regional MSP
- **Reports to:** CEO
- **Experience:** 15 years in IT services, 6 years building security practice
- **Technical Level:** Business-technical hybrid; sells and oversees delivery

### Background
David built the security practice at his MSP from scratch. They now manage security for 35 SMB clients across manufacturing, legal, and professional services. Each client has different maturity levels and compliance requirements. He's responsible for both selling security services and ensuring delivery quality.

### Objectives
1. **Client Visibility:** See all 35 clients' security posture at a glance
2. **Service Differentiation:** Prove value vs. competitors with better reporting
3. **Upsell Identification:** Find clients who need additional services
4. **SLA Compliance:** Meet contracted response times across all clients
5. **Team Efficiency:** Help his 6-person team manage 35 clients effectively

### Needs
| Need | Priority | Current Pain |
|------|----------|--------------|
| Multi-tenant dashboard | Critical | Logs into 35 separate portals |
| Client comparison view | Critical | No way to rank clients by risk |
| Branded reports | High | Manual report creation per client |
| Batch alerting | High | Misses critical alerts in the noise |
| Revenue opportunity flags | Medium | Reactive to client requests |

### Pain Points
- "I spend Monday mornings logging into 35 different portals"
- "A client calls angry because they found a vulnerability before we did"
- "I can't easily show clients their security improved since hiring us"
- "My team is stretched thin and we're missing things"

### Dashboard Usage
- **Primary View:** Multi-tenant overview → drill into specific tenant
- **Frequency:** Daily aggregate view, per-client for QBRs
- **Key Features:** Cross-tenant comparison, batch export, white-label reports
- **Actions:** Generate monthly client reports, identify at-risk clients, prioritize team work
- **Time Spent:** 1 hour/day aggregate, 30 min/client for monthly reports

### Success Metrics for David
- Monday portal marathon: 3 hours → 30 minutes
- Client report generation: 2 hours/client → 15 minutes
- Zero missed critical alerts
- Upsell revenue from identified gaps: +25%

### Quote
> "My clients trust me to watch their backs. If I can't see all 35 of them in one place, something will slip through—and that something could be ransomware."

---

## Persona 4: Jennifer Walsh — Compliance & Risk Manager

### Demographics
- **Age:** 44
- **Role:** Director of Compliance at a SaaS company (400 employees)
- **Reports to:** General Counsel
- **Experience:** 18 years in audit/compliance, CPA background
- **Technical Level:** Low-moderate; understands concepts, not implementation

### Background
Jennifer joined from Big 4 accounting to build the compliance program. The company is SOC 2 Type II certified and pursuing ISO 27001. She manages the relationship with external auditors and coordinates evidence collection across IT, HR, and Legal. She's methodical, deadline-driven, and allergic to last-minute surprises.

### Objectives
1. **Audit Readiness:** Maintain continuous compliance, not annual fire drills
2. **Control Mapping:** Map technical controls to framework requirements
3. **Evidence Collection:** Automate evidence gathering for auditors
4. **Risk Register:** Maintain living risk register tied to actual findings
5. **Vendor Assessment:** Evaluate third-party security as part of vendor management

### Needs
| Need | Priority | Current Pain |
|------|----------|--------------|
| Framework mapping | Critical | Manual crosswalk spreadsheets |
| Automated evidence | Critical | Chases IT for screenshots |
| Control status view | High | Doesn't know what's actually implemented |
| Historical compliance | High | Can't show compliance over time |
| Exception tracking | Medium | Email threads for exceptions |

### Pain Points
- "I ask IT for MFA evidence and get different answers every time"
- "Auditors want proof, not promises"
- "I don't speak technical, and IT doesn't speak compliance"
- "Last year's SOC 2 prep nearly killed me—there has to be a better way"

### Dashboard Usage
- **Primary View:** Compliance-focused Executive view + Audit Trail
- **Frequency:** Weekly review, daily during audit periods
- **Key Features:** Framework mapping, control status, audit log export
- **Actions:** Export compliance evidence, track control gaps, monitor access changes
- **Time Spent:** 2-3 hours/week, 4+ hours/day during audits

### Success Metrics for Jennifer
- SOC 2 evidence collection: 3 weeks → 3 days
- Control gap identification: reactive → proactive
- Auditor questions answered same-day vs. "I'll get back to you"
- Zero audit findings related to evidence gaps

### Quote
> "When the auditor asks 'show me all admin access changes in the last 90 days,' I need to click a button, not send an email to IT and wait three days."

---

## Persona 5: Rachel Torres — HR Business Partner & Internal Communications Lead

### Demographics
- **Age:** 36
- **Role:** Senior HR Business Partner / Internal Comms at a tech company (600 employees)
- **Reports to:** VP of People
- **Experience:** 12 years in HR, 3 years in tech industry
- **Technical Level:** Non-technical; user of business applications

### Background
Rachel wears multiple hats: HR business partner for Engineering and Sales, plus she leads internal communications. After a phishing incident last year where an employee clicked a malicious link, she's been pulled into security awareness. She coordinates with IT on employee offboarding, badge access, and security training completion. Leadership now expects her to help "make security part of the culture."

### Objectives
1. **Security Culture:** Drive employee engagement with security practices
2. **Training Compliance:** Ensure 100% security awareness training completion
3. **Offboarding Security:** Confirm access is revoked for departing employees
4. **Incident Communication:** Craft clear, non-alarming security communications
5. **Leadership Reporting:** Report security training/compliance to executives

### Needs
| Need | Priority | Current Pain |
|------|----------|--------------|
| Training completion data | Critical | IT sends Excel; she reformats for slides |
| MFA adoption by department | High | Can't identify which teams need nudging |
| Offboarding verification | High | Manual checklist, no confirmation |
| Security metrics for all-hands | Medium | Gets technical dumps, needs simple stats |
| Guest user context | Medium | Legal asks about contractors; she can't answer |

### Pain Points
- "IT gives me data I don't understand and can't present"
- "I'm responsible for security culture but don't have visibility"
- "When someone leaves, I need to KNOW their access is gone—for legal reasons"
- "The CEO wants security stats in the all-hands; I'm not a security expert"

### Dashboard Usage
- **Primary View:** Curated view of Executive Dashboard metrics
- **Frequency:** Weekly, monthly for all-hands prep
- **Key Metrics:** MFA Coverage by department, Security Training %, Guest Users
- **Actions:** Export department-level reports, track training completion, verify offboarding
- **Time Spent:** 1-2 hours/week, more during all-hands prep

### Success Metrics for Rachel
- All-hands security slide prep: 4 hours → 30 minutes
- Department-level MFA data: days to obtain → instant
- Offboarding access verification: "I think so" → "confirmed revoked"
- Security comms sent with confidence, not IT scripts

### Quote
> "I'm not a security person, but I AM responsible for our people following security practices. I need simple metrics I can act on—not a technical deep-dive that makes my eyes glaze over."

---

## Persona Comparison Matrix

| Attribute | Marcus (CISO) | Sarah (Analyst) | David (MSP) | Jennifer (Compliance) | Rachel (HR) |
|-----------|---------------|-----------------|-------------|----------------------|-------------|
| **Primary Dashboard** | Executive | IT Staff | Multi-tenant | Executive + Audit | Executive (simplified) |
| **Technical Level** | Strategic | Expert | Hybrid | Low-Moderate | Non-technical |
| **Usage Frequency** | Weekly | Daily (hours) | Daily | Weekly/Daily in audit | Weekly |
| **Key Concern** | Board reporting | Alert triage | Client coverage | Audit evidence | Culture metrics |
| **Success = ** | Confident board meetings | Faster remediation | No missed alerts | Smooth audits | Engaged employees |
| **Export Needs** | PDF executive report | CSV for ticketing | Branded client PDFs | Audit evidence packs | Simple charts |
| **Top Metric** | Security Score Trend | Open Critical Alerts | Cross-tenant comparison | Control compliance % | MFA by department |

---

## Design Implications

### For Marcus (CISO)
- Large, scannable KPIs at top of Executive Dashboard
- 6-month trend charts for board presentations
- One-click PDF export with branding
- "Board Ready" report template

### For Sarah (Analyst)
- Filterable, sortable alert queue with keyboard shortcuts
- Bulk actions (assign, resolve, export)
- Direct links to remediation resources
- MTTR tracking visible on dashboard

### For David (MSP)
- Tenant switcher always accessible
- Cross-tenant risk ranking view
- Batch report generation
- White-label/branding options

### For Jennifer (Compliance)
- Framework mapping overlay on metrics
- One-click evidence export by control
- Audit trail with advanced filters
- Historical compliance snapshots

### For Rachel (HR)
- Simplified view option (less technical jargon)
- Department-level breakdowns
- Guest user inventory with business context
- Export to PowerPoint-friendly format

---

## Appendix: Jobs to Be Done

| Persona | Job to Be Done |
|---------|----------------|
| Marcus | "Help me confidently report our security posture to non-technical leadership" |
| Sarah | "Help me see all security issues in one place so I can fix what matters first" |
| David | "Help me manage 35 clients without something falling through the cracks" |
| Jennifer | "Help me prove to auditors that our controls are working" |
| Rachel | "Help me drive security behavior change without needing to be a security expert" |
