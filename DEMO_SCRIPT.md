# MeetingMind — Demo Script & Sales Walkthrough

**Duration:** 5-7 minutes
**Audience:** Solo doctors, small law firms, financial advisors, school administrators
**Goal:** Show the product, demonstrate the privacy moat, close with a trial signup

---

## Pre-Demo Setup

1. Have MeetingMind running (`python3 -m streamlit run app.py`)
2. Have Ollama running (`ollama serve`)
3. Prepare a sample audio file (or use live recording)
4. Have the landing page open in another tab
5. Know your audience's vertical (healthcare, legal, financial, education)

---

## The Script

### Opening (30 seconds)

> "Let me show you something. Every AI meeting tool on the market — Otter, Gong, Fireflies — they all do the same thing: record your meeting and send it to their cloud servers for processing.
>
> For most people, that's fine. But for you — [a doctor handling patient data / a lawyer with privileged communications / a financial advisor under SEC oversight / a teacher with student records] — that's a compliance nightmare.
>
> MeetingMind is different. Everything happens right here, on your device. Nothing ever leaves."

---

### Demo Flow

#### Step 1: Show the Dashboard (30 seconds)

**[Screen: Dashboard page]**

> "This is MeetingMind. You can see it's tracking meetings, duration, words transcribed, and time saved. Notice the privacy badge in the sidebar — '100% ON-DEVICE'. That's not marketing. That's the architecture."

**Action:** Point to the sidebar showing "AI Engine Online" and "100% ON-DEVICE" badge.

---

#### Step 2: Select the Vertical (30 seconds)

**[Screen: Click "Industry Verticals" in sidebar]**

> "MeetingMind isn't one-size-fits-all. We have 13 industry verticals, each with templates designed for your specific workflow."

**Action:** Click on the relevant vertical for your audience:

| Audience | Click | Say |
|----------|-------|-----|
| Doctors | Healthcare | "SOAP notes, H&P, progress notes, discharge summaries — the formats you already use" |
| Lawyers | Legal | "Client intake, deposition summaries, case briefs — all privilege-preserving" |
| Financial | Financial | "Client meeting notes, trade rationale, compliance logs — SEC 17a-4 ready" |
| Teachers | Education | "IEP meeting notes, parent-teacher conferences — FERPA compliant by design" |

**Action:** Click "Select" on the vertical, then select the primary template.

---

#### Step 3: Record or Upload (60 seconds)

**[Screen: Record/Upload page]**

> "Now let's process a meeting. You have two options: record live right here in the browser, or upload a file you've already recorded."

**Option A — Live Recording Demo:**
> "I'll record a quick sample right now."

**Action:** Click the microphone, speak for 20-30 seconds simulating a relevant scenario:

- **Doctor:** "Patient presents with persistent lower back pain for three weeks. No history of trauma. Pain radiates to the left leg. Reports numbness in the toes. Currently taking ibuprofen 400mg three times daily with minimal relief. Vitals: BP 130/85, heart rate 72, temperature 98.6. Physical exam reveals limited range of motion in lumbar spine, positive straight leg raise on the left."

- **Lawyer:** "Client John Smith, referred by attorney Jane Doe. Potential personal injury case. Client was rear-ended at a stoplight on January 15th. Other driver was texting. Client has medical bills of approximately forty thousand dollars. Lost six weeks of work. Looking at negligence claim. Need to check statute of limitations — we have two years from date of accident."

- **Financial Advisor:** "Meeting with client regarding portfolio rebalancing. Current allocation is 70% equities, 30% fixed income. Client's risk tolerance has shifted following retirement. Recommending shift to 50/50 allocation. Discussed moving from growth funds to dividend-paying ETFs. Client agreed to proceed with rebalancing. Next review in Q3."

**Action:** Stop recording.

**Option B — Upload Demo:**
> "Or you can upload any audio or video file."

**Action:** Upload a pre-prepared sample file.

---

#### Step 4: AI Processing (60 seconds)

**[Screen: Processing with progress bar]**

> "Watch what happens. Whisper — that's OpenAI's speech recognition model — is running right here on this machine. It's transcribing every word. Then our local AI model analyzes the transcript and generates structured notes."

**Action:** Point out the progress bar and status messages.

> "Notice: no loading spinner waiting for a cloud server. No data being uploaded anywhere. This is pure local processing."

**Wait for processing to complete.**

---

#### Step 5: Show the Results (90 seconds)

**[Screen: Results page with AI Notes tab]**

**For Healthcare (SOAP):**
> "Look at this. It automatically generated SOAP notes from that conversation:
> - **Subjective:** Chief complaint, history of present illness, all extracted
> - **Objective:** Vitals, physical exam findings, organized properly
> - **Assessment:** Working diagnoses identified
> - **Plan:** Medications, follow-up, everything structured
>
> This would have taken you 15 minutes to type. MeetingMind did it in 30 seconds. And your patient's data never left this room."

**For Legal:**
> "It generated a structured client intake:
> - Client info, matter type, key facts
> - Legal issues identified, potential claims
> - Statute of limitations flagged
> - Next steps with action items
>
> And here's the critical part: this entire conversation was processed on your device. Attorney-client privilege is preserved. The Heppner ruling that waived privilege for cloud AI? Doesn't apply here."

**For Financial:**
> "Structured compliance notes:
> - Client meeting purpose, portfolio discussion
> - Investment recommendations with risk levels
> - Suitability notes — exactly what SEC examiners want to see
> - Full audit trail, locally stored
>
> If the SEC audits you, these records are on your device, properly retained."

**Action:** Click through the Transcript tab and Export tab.

---

#### Step 6: Show Compliance Center (30 seconds)

**[Screen: Click "Compliance" in sidebar]**

> "This is the Compliance Center. It shows you exactly which frameworks apply to your industry and how MeetingMind satisfies them."

**Action:** Point to the compliance badges and the architecture diagram.

> "See this? Audio captured on-device. AI processing on-device. Storage on-device. Zero cloud contact. This isn't a feature — it's the entire architecture."

---

#### Step 7: Export (20 seconds)

**[Screen: Back to results, Export tab]**

> "When you're done, export in any format — PDF for your records, Markdown for your documentation system, JSON for integrations."

**Action:** Download a PDF. Open it briefly to show the branded format.

---

### Closing (30 seconds)

> "So here's the question: Are you going to keep spending [2 hours a day on documentation / risking privilege with cloud tools / hoping the SEC doesn't audit your meeting records] — or do you want a tool that solves this in 30 seconds, with zero compliance risk?
>
> MeetingMind is free to try. Five meetings per month, no credit card. When you're ready, Pro is $29 a month. For [HIPAA templates / privilege-preserving templates / SEC compliance templates], it's $199 a month — which is a fraction of what a single [HIPAA violation / malpractice claim / SEC fine] would cost."

---

## Objection Handling

| Objection | Response |
|-----------|----------|
| "I already use Otter/Gong" | "Otter is being sued for privacy violations (Brewer v. Otter, 2025). Fireflies has BIPA litigation. Every one of those tools sends your [patient data / privileged communications / financial records] to their cloud. One breach, one lawsuit, and the cost dwarfs any subscription." |
| "Is the AI quality good enough?" | "We use the same Whisper model that powers ChatGPT's voice features. For the AI notes, we use Llama 3.2 — the latest open-source model. Run it on a test meeting and compare the output." |
| "Can it integrate with my EHR/CRM/system?" | "We export to JSON, which integrates with any system. We're building direct integrations with [Epic/Cerner for healthcare / Clio/MyCase for legal / Wealthbox/Redtail for financial]. What system do you use?" |
| "What if my computer is slow?" | "Whisper's 'base' model runs on any modern laptop. For older machines, the 'tiny' model is even faster. If you have Apple Silicon (M1/M2/M3/M4), it's exceptionally fast." |
| "I need it on my phone" | "We're building a mobile app. In the meantime, the web interface works on any device with a browser and microphone." |
| "Is it really secure?" | "More secure than any cloud solution. Your data literally cannot be breached remotely because it's never on a remote server. The attack surface is your own device — which you already trust with everything else." |

---

## Follow-Up Sequence

### Day 0 (After Demo)
- Send them the installer link
- "Try it on your next 3 meetings. Free tier, no credit card."

### Day 3
- "How did MeetingMind work on your meetings? Any questions?"

### Day 7
- "You've used [X] of your 5 free meetings this month. Ready to upgrade to unlimited?"

### Day 14
- Share a case study from another user in their vertical

### Day 30
- "Your free month is ending. Pro is $29/month — that's less than one hour of your billing rate."

---

## Key Stats to Cite

- Physicians spend **2 hours on documentation for every 1 hour with patients** (Annals of Internal Medicine)
- **49% of physicians** report burnout, documentation is the #1 cause
- **84% of lawyers** still use paper/manual notes for client meetings
- SEC has levied **$770M+ in fines** for recordkeeping failures
- Otter.ai faces **class-action lawsuit** (Brewer v. Otter.ai, Aug 2025)
- Fireflies faces **BIPA litigation** (Dec 2025)
- **Heppner ruling (2026):** Cloud AI waives attorney-client privilege
- Special ed teachers spend **65% of their time on paperwork**
- Construction loses **$177B annually** to change orders from poor communication

---

## Vertical-Specific Demo Customizations

### Healthcare Demo
- Use medical terminology in the sample recording
- Show SOAP note output — they'll immediately recognize the format
- Emphasize: "No BAA needed. No HIPAA audit. The data never leaves."
- Compare: "Nuance DAX costs $900/month. MeetingMind is $149-299."

### Legal Demo
- Use legal terminology (client intake scenario)
- Show privilege preservation
- Cite the Heppner ruling
- Compare: "There is literally no other tool that preserves privilege."

### Financial Demo
- Use financial advisory language
- Show the compliance log format
- Cite SEC fines
- Compare: "Jump AI costs $800-1,440/year and it's cloud-based."

### Education Demo
- Use IEP meeting scenario
- Show accommodations and goals extraction
- Emphasize FERPA compliance
- Compare: "Teachers spend 65% of time on paperwork. This takes 30 seconds."
