"""
MeetingMind — Vertical Templates Engine
13 industries × 45+ specialized AI prompt templates.
"""

import json
import re

# ─────────────────────────────────────────────────────────────────────────────
# VERTICALS REGISTRY
# ─────────────────────────────────────────────────────────────────────────────

VERTICALS = {
    # ═══════════════════════════════════════════════════════════════════════════
    # TIER 1 — LAUNCH VERTICALS
    # ═══════════════════════════════════════════════════════════════════════════
    "healthcare": {
        "id": "healthcare",
        "name": "Healthcare",
        "icon": "\U0001f3e5",
        "description": "SOAP, H&P, progress notes, discharge summaries",
        "color": "#EF4444",
        "compliance_tags": ["hipaa", "bipa"],
        "templates": {
            "soap_notes": {
                "id": "soap_notes",
                "name": "SOAP Notes",
                "description": "Subjective, Objective, Assessment, Plan — standard clinical documentation",
                "prompt_template": """You are an expert medical scribe. Analyze the following clinical encounter transcript and generate structured SOAP notes.

Meeting Title: {meeting_title}

TRANSCRIPT:
{transcript}

Return ONLY valid JSON in this EXACT format:

{{
  "subjective": {{
    "chief_complaint": "Primary reason for visit in patient's own words",
    "history_of_present_illness": "Detailed HPI including onset, location, duration, character, aggravating/alleviating factors, radiation, timing, severity (OLDCARTS)",
    "review_of_systems": {{
      "constitutional": "Findings or 'Not reviewed'",
      "cardiovascular": "Findings or 'Not reviewed'",
      "respiratory": "Findings or 'Not reviewed'",
      "gastrointestinal": "Findings or 'Not reviewed'",
      "musculoskeletal": "Findings or 'Not reviewed'",
      "neurological": "Findings or 'Not reviewed'",
      "psychiatric": "Findings or 'Not reviewed'"
    }},
    "past_medical_history": ["Listed conditions"],
    "medications": ["Current medications mentioned"],
    "allergies": ["Known allergies mentioned"],
    "social_history": "Relevant social factors discussed"
  }},
  "objective": {{
    "vitals": "Any vitals mentioned (BP, HR, Temp, RR, SpO2, Weight)",
    "physical_exam": ["Physical exam findings discussed"],
    "labs_imaging": ["Any lab results or imaging discussed"]
  }},
  "assessment": {{
    "diagnoses": ["Primary and secondary diagnoses"],
    "differential": ["Differential diagnoses considered"],
    "clinical_reasoning": "Summary of clinical decision-making"
  }},
  "plan": {{
    "medications": ["Medications prescribed, changed, or continued"],
    "procedures": ["Procedures ordered or performed"],
    "follow_up": "Follow-up instructions and timeline",
    "patient_education": ["Education topics discussed with patient"],
    "referrals": ["Any referrals made"]
  }},
  "meeting_type": "Clinical Encounter",
  "sentiment": "Productive"
}}

IMPORTANT: Extract REAL information from the transcript. Use 'Not mentioned' for absent data. Never fabricate clinical information.""",
                "output_schema": {
                    "subjective": "dict — Chief complaint, HPI, ROS, PMH, medications, allergies",
                    "objective": "dict — Vitals, physical exam, labs/imaging",
                    "assessment": "dict — Diagnoses, differential, reasoning",
                    "plan": "dict — Medications, procedures, follow-up, education, referrals",
                },
                "required_fields": ["subjective", "objective", "assessment", "plan"],
                "export_sections": ["Subjective", "Objective", "Assessment", "Plan"],
            },
            "hp_notes": {
                "id": "hp_notes",
                "name": "H&P Notes",
                "description": "History and Physical examination documentation",
                "prompt_template": """You are an expert medical scribe. Generate a History & Physical (H&P) note from this transcript.

Meeting Title: {meeting_title}

TRANSCRIPT:
{transcript}

Return ONLY valid JSON:
{{
  "patient_info": "Patient demographics mentioned",
  "chief_complaint": "Primary reason for visit",
  "history_of_present_illness": "Detailed narrative HPI",
  "past_medical_history": ["Conditions"],
  "past_surgical_history": ["Surgeries"],
  "family_history": ["Relevant family history"],
  "social_history": "Tobacco, alcohol, drugs, occupation, living situation",
  "medications": ["Current medications"],
  "allergies": ["Allergies and reactions"],
  "review_of_systems": {{"system": "findings"}},
  "physical_examination": {{"system": "findings"}},
  "labs_and_imaging": ["Results discussed"],
  "assessment": "Clinical assessment and diagnoses",
  "plan": ["Plan items"],
  "meeting_type": "H&P Encounter",
  "sentiment": "Productive"
}}""",
                "output_schema": {"chief_complaint": "str", "history_of_present_illness": "str", "assessment": "str", "plan": "list"},
                "required_fields": ["chief_complaint", "history_of_present_illness", "assessment", "plan"],
                "export_sections": ["Patient Info", "Chief Complaint", "HPI", "PMH", "Physical Exam", "Assessment", "Plan"],
            },
            "progress_notes": {
                "id": "progress_notes",
                "name": "Progress Notes",
                "description": "Follow-up visit documentation",
                "prompt_template": """Analyze this follow-up clinical encounter and generate progress notes.

Meeting Title: {meeting_title}

TRANSCRIPT:
{transcript}

Return ONLY valid JSON:
{{
  "patient_info": "Patient demographics",
  "visit_reason": "Reason for follow-up",
  "interval_history": "Changes since last visit",
  "current_symptoms": ["Current symptoms reported"],
  "medication_review": [{{"medication": "name", "status": "continued/changed/discontinued", "notes": "details"}}],
  "examination_findings": ["Relevant exam findings"],
  "lab_results": ["Any new lab results"],
  "assessment": "Clinical assessment of progress",
  "plan_changes": ["Changes to treatment plan"],
  "next_follow_up": "Recommended follow-up timeline",
  "meeting_type": "Follow-up Visit",
  "sentiment": "Productive"
}}""",
                "output_schema": {"visit_reason": "str", "assessment": "str", "plan_changes": "list"},
                "required_fields": ["visit_reason", "assessment", "plan_changes"],
                "export_sections": ["Visit Reason", "Interval History", "Exam", "Assessment", "Plan Changes"],
            },
            "discharge_summary": {
                "id": "discharge_summary",
                "name": "Discharge Summary",
                "description": "Hospital discharge documentation",
                "prompt_template": """Generate a discharge summary from this clinical discussion.

Meeting Title: {meeting_title}

TRANSCRIPT:
{transcript}

Return ONLY valid JSON:
{{
  "patient_info": "Patient demographics",
  "admission_date": "Date if mentioned",
  "discharge_date": "Date if mentioned",
  "admitting_diagnosis": "Reason for admission",
  "discharge_diagnosis": ["Final diagnoses"],
  "hospital_course": "Narrative of hospital stay and treatment",
  "procedures_performed": ["Procedures during stay"],
  "discharge_medications": [{{"medication": "name", "dose": "dosing", "instructions": "how to take"}}],
  "discharge_instructions": ["Patient instructions"],
  "follow_up_appointments": ["Scheduled follow-ups"],
  "pending_results": ["Any pending labs/imaging"],
  "meeting_type": "Discharge Planning",
  "sentiment": "Productive"
}}""",
                "output_schema": {"admitting_diagnosis": "str", "hospital_course": "str", "discharge_medications": "list"},
                "required_fields": ["admitting_diagnosis", "hospital_course", "discharge_medications"],
                "export_sections": ["Admission", "Hospital Course", "Discharge Meds", "Instructions", "Follow-up"],
            },
        },
    },

    "legal": {
        "id": "legal",
        "name": "Legal",
        "icon": "\u2696\ufe0f",
        "description": "Client intake, depositions, case briefs, contract review",
        "color": "#3B82F6",
        "compliance_tags": ["attorney_client"],
        "templates": {
            "client_intake": {
                "id": "client_intake",
                "name": "Client Intake Notes",
                "description": "New client consultation and matter intake",
                "prompt_template": """You are an experienced legal secretary. Analyze this client intake meeting and extract structured notes.

Meeting Title: {meeting_title}

TRANSCRIPT:
{transcript}

Return ONLY valid JSON:
{{
  "client_info": {{
    "name": "Client name",
    "contact": "Contact information mentioned",
    "referred_by": "Referral source if mentioned"
  }},
  "matter_type": "Type of legal matter (e.g., personal injury, contract dispute, family law)",
  "facts_summary": "Narrative summary of key facts presented by the client",
  "key_dates": ["Important dates and deadlines mentioned"],
  "legal_issues": ["Identified legal issues and questions"],
  "potential_claims": ["Potential claims or causes of action"],
  "potential_defenses": ["Anticipated defenses or challenges"],
  "evidence_discussed": ["Documents, witnesses, or evidence mentioned"],
  "conflicts_check": "Any conflicts of interest noted",
  "engagement_terms": "Fee arrangement, retainer, scope of representation discussed",
  "next_steps": ["Immediate action items"],
  "statute_of_limitations": "Any SOL concerns noted",
  "meeting_type": "Client Intake",
  "sentiment": "Productive"
}}

IMPORTANT: This is attorney-client privileged communication. Extract only what was discussed. Do not fabricate facts.""",
                "output_schema": {"matter_type": "str", "facts_summary": "str", "legal_issues": "list", "next_steps": "list"},
                "required_fields": ["matter_type", "facts_summary", "legal_issues", "next_steps"],
                "export_sections": ["Client Info", "Matter Type", "Facts", "Legal Issues", "Claims/Defenses", "Next Steps"],
            },
            "deposition_summary": {
                "id": "deposition_summary",
                "name": "Deposition Summary",
                "description": "Deposition transcript analysis and key testimony",
                "prompt_template": """Analyze this deposition transcript and create a structured summary.

Meeting Title: {meeting_title}

TRANSCRIPT:
{transcript}

Return ONLY valid JSON:
{{
  "deponent_info": "Name and role of the person being deposed",
  "case_reference": "Case name/number if mentioned",
  "key_testimony": ["Critical statements and admissions"],
  "contradictions": ["Any contradictions or inconsistencies noted"],
  "objections": ["Objections raised and their basis"],
  "exhibits_referenced": ["Documents or exhibits discussed"],
  "credibility_notes": "Assessment of deponent demeanor and credibility",
  "follow_up_questions": ["Questions to pursue in future depositions or at trial"],
  "impeachment_opportunities": ["Potential impeachment material identified"],
  "summary": "Narrative summary of the deposition",
  "meeting_type": "Deposition",
  "sentiment": "Neutral"
}}""",
                "output_schema": {"key_testimony": "list", "summary": "str"},
                "required_fields": ["key_testimony", "summary"],
                "export_sections": ["Deponent", "Key Testimony", "Contradictions", "Exhibits", "Follow-up"],
            },
            "case_brief": {
                "id": "case_brief",
                "name": "Case Brief",
                "description": "Case strategy discussion and legal analysis",
                "prompt_template": """Analyze this legal strategy meeting and create a case brief.

Meeting Title: {meeting_title}

TRANSCRIPT:
{transcript}

Return ONLY valid JSON:
{{
  "case_caption": "Case name and number",
  "parties": {{"plaintiff": "name", "defendant": "name"}},
  "facts": "Statement of relevant facts",
  "procedural_history": "Procedural posture of the case",
  "issues": ["Legal issues to be decided"],
  "applicable_law": ["Statutes, regulations, case law cited"],
  "arguments_for": ["Arguments in favor of our position"],
  "arguments_against": ["Arguments opposing our position"],
  "strategy": "Recommended legal strategy",
  "discovery_needs": ["Outstanding discovery items"],
  "deadlines": ["Upcoming deadlines"],
  "settlement_considerations": "Settlement value and considerations",
  "meeting_type": "Case Strategy",
  "sentiment": "Productive"
}}""",
                "output_schema": {"facts": "str", "issues": "list", "strategy": "str"},
                "required_fields": ["facts", "issues", "strategy"],
                "export_sections": ["Case Caption", "Facts", "Issues", "Arguments", "Strategy", "Deadlines"],
            },
            "contract_review": {
                "id": "contract_review",
                "name": "Contract Review Notes",
                "description": "Contract negotiation and review discussion",
                "prompt_template": """Analyze this contract review meeting and extract structured notes.

Meeting Title: {meeting_title}

TRANSCRIPT:
{transcript}

Return ONLY valid JSON:
{{
  "contract_type": "Type of contract being reviewed",
  "parties": ["Parties to the contract"],
  "key_terms": [{{"term": "description", "status": "agreed/disputed/pending"}}],
  "red_flags": ["Problematic clauses or terms identified"],
  "negotiation_points": ["Terms to negotiate or push back on"],
  "missing_provisions": ["Important provisions not in the draft"],
  "liability_concerns": ["Liability and indemnification issues"],
  "intellectual_property": "IP-related terms discussed",
  "termination_provisions": "Termination and exit terms",
  "recommended_changes": ["Specific changes recommended"],
  "next_steps": ["Action items for contract finalization"],
  "meeting_type": "Contract Review",
  "sentiment": "Productive"
}}""",
                "output_schema": {"contract_type": "str", "key_terms": "list", "recommended_changes": "list"},
                "required_fields": ["contract_type", "key_terms", "recommended_changes"],
                "export_sections": ["Contract Type", "Key Terms", "Red Flags", "Recommendations", "Next Steps"],
            },
        },
    },

    "financial": {
        "id": "financial",
        "name": "Financial Services",
        "icon": "\U0001f3e6",
        "description": "Compliance logs, KYC records, trade rationale, client meetings",
        "color": "#10B981",
        "compliance_tags": ["sec_17a4", "finra_3110"],
        "templates": {
            "client_meeting": {
                "id": "client_meeting",
                "name": "Client Meeting Notes",
                "description": "Financial advisor client consultation notes",
                "prompt_template": """You are a financial compliance officer. Analyze this client meeting and generate structured notes suitable for regulatory retention.

Meeting Title: {meeting_title}

TRANSCRIPT:
{transcript}

Return ONLY valid JSON:
{{
  "client_info": "Client name and account references",
  "meeting_purpose": "Purpose of the meeting",
  "portfolio_discussion": "Portfolio performance and allocation discussed",
  "investment_recommendations": [{{"recommendation": "description", "rationale": "reason", "risk_level": "Low/Medium/High"}}],
  "risk_tolerance_discussed": "Client's risk tolerance and any changes",
  "suitability_notes": "Suitability analysis for recommendations made",
  "client_objectives": ["Stated client goals and objectives"],
  "compliance_disclosures": ["Disclosures made during meeting"],
  "next_steps": ["Action items with responsible party"],
  "follow_up_date": "Scheduled follow-up",
  "meeting_type": "Client Consultation",
  "sentiment": "Productive"
}}""",
                "output_schema": {"meeting_purpose": "str", "investment_recommendations": "list", "next_steps": "list"},
                "required_fields": ["meeting_purpose", "investment_recommendations", "next_steps"],
                "export_sections": ["Client", "Purpose", "Recommendations", "Suitability", "Compliance", "Next Steps"],
            },
            "trade_rationale": {
                "id": "trade_rationale",
                "name": "Trade Rationale",
                "description": "Investment decision documentation for compliance",
                "prompt_template": """Document the trade rationale from this investment discussion for SEC/FINRA compliance.

Meeting Title: {meeting_title}

TRANSCRIPT:
{transcript}

Return ONLY valid JSON:
{{
  "trade_date": "Date discussed",
  "security": "Security or instrument discussed",
  "action": "Buy/Sell/Hold recommendation",
  "quantity_value": "Amount or value discussed",
  "rationale": "Detailed investment rationale",
  "research_cited": ["Research reports or data cited"],
  "risk_factors": ["Identified risk factors"],
  "client_suitability": "Suitability for client profile",
  "regulatory_considerations": ["Relevant regulatory factors"],
  "approval_chain": "Approval process discussed",
  "meeting_type": "Trade Discussion",
  "sentiment": "Productive"
}}""",
                "output_schema": {"security": "str", "action": "str", "rationale": "str"},
                "required_fields": ["security", "action", "rationale"],
                "export_sections": ["Security", "Action", "Rationale", "Risk Factors", "Suitability"],
            },
            "compliance_log": {
                "id": "compliance_log",
                "name": "Compliance Log",
                "description": "Regulatory compliance meeting documentation",
                "prompt_template": """Document this compliance meeting for regulatory records.

Meeting Title: {meeting_title}

TRANSCRIPT:
{transcript}

Return ONLY valid JSON:
{{
  "meeting_date": "Date of meeting",
  "attendees": ["Meeting attendees"],
  "compliance_topics": ["Topics reviewed"],
  "regulatory_updates": ["New regulations or guidance discussed"],
  "findings": ["Compliance findings or concerns"],
  "remediation_actions": [{{"finding": "issue", "action": "remediation", "responsible": "person", "deadline": "date"}}],
  "policy_changes": ["Policy changes discussed or approved"],
  "training_needs": ["Identified training requirements"],
  "audit_items": ["Items for internal audit follow-up"],
  "meeting_type": "Compliance Review",
  "sentiment": "Productive"
}}""",
                "output_schema": {"compliance_topics": "list", "findings": "list", "remediation_actions": "list"},
                "required_fields": ["compliance_topics", "findings"],
                "export_sections": ["Topics", "Regulatory Updates", "Findings", "Remediation", "Action Items"],
            },
            "kyc_meeting": {
                "id": "kyc_meeting",
                "name": "KYC Meeting Record",
                "description": "Know Your Customer verification meeting notes",
                "prompt_template": """Document this KYC/AML meeting for compliance records.

Meeting Title: {meeting_title}

TRANSCRIPT:
{transcript}

Return ONLY valid JSON:
{{
  "client_name": "Client or entity name",
  "account_type": "Type of account",
  "verification_status": "Current KYC verification status",
  "identity_documents": ["Documents reviewed or requested"],
  "beneficial_owners": ["Beneficial owners identified"],
  "source_of_funds": "Source of funds/wealth discussed",
  "risk_rating": "AML risk rating assigned (Low/Medium/High)",
  "pep_status": "Politically Exposed Person check result",
  "sanctions_screening": "Sanctions screening result",
  "red_flags": ["Any suspicious activity indicators"],
  "enhanced_due_diligence": "EDD requirements if applicable",
  "next_steps": ["Follow-up items"],
  "meeting_type": "KYC Review",
  "sentiment": "Productive"
}}""",
                "output_schema": {"client_name": "str", "risk_rating": "str", "next_steps": "list"},
                "required_fields": ["client_name", "risk_rating"],
                "export_sections": ["Client", "Verification", "Risk Rating", "Due Diligence", "Next Steps"],
            },
        },
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # TIER 2 — GROWTH VERTICALS
    # ═══════════════════════════════════════════════════════════════════════════
    "veterinary": {
        "id": "veterinary",
        "name": "Veterinary",
        "icon": "\U0001f43e",
        "description": "Vet SOAP notes, treatment plans, client communication",
        "color": "#F59E0B",
        "compliance_tags": [],
        "templates": {
            "vet_soap": {
                "id": "vet_soap",
                "name": "Veterinary SOAP Notes",
                "description": "Clinical notes for animal patients",
                "prompt_template": """You are a veterinary medical scribe. Generate SOAP notes from this veterinary consultation.

Meeting Title: {meeting_title}

TRANSCRIPT:
{transcript}

Return ONLY valid JSON:
{{
  "patient_info": {{"animal_name": "name", "species": "species", "breed": "breed", "age": "age", "weight": "weight", "owner": "owner name"}},
  "subjective": {{
    "presenting_complaint": "Reason for visit as described by owner",
    "history": "Relevant medical history",
    "diet": "Current diet if discussed",
    "behavior_changes": "Any behavioral changes noted"
  }},
  "objective": {{
    "vitals": "Temperature, HR, RR, weight",
    "physical_exam": ["Physical examination findings"],
    "body_condition_score": "BCS if assessed",
    "diagnostics": ["Lab results, imaging, tests discussed"]
  }},
  "assessment": {{
    "diagnoses": ["Working diagnoses"],
    "differential": ["Differential diagnoses"],
    "prognosis": "Prognosis discussed"
  }},
  "plan": {{
    "medications": [{{"medication": "name", "dose": "dosing", "duration": "how long"}}],
    "procedures": ["Procedures performed or recommended"],
    "diet_changes": "Dietary recommendations",
    "follow_up": "Recheck timeline",
    "client_education": ["Topics discussed with pet owner"]
  }},
  "meeting_type": "Veterinary Consultation",
  "sentiment": "Productive"
}}""",
                "output_schema": {"patient_info": "dict", "subjective": "dict", "objective": "dict", "assessment": "dict", "plan": "dict"},
                "required_fields": ["patient_info", "subjective", "assessment", "plan"],
                "export_sections": ["Patient", "Subjective", "Objective", "Assessment", "Plan"],
            },
            "treatment_plan": {
                "id": "treatment_plan",
                "name": "Treatment Plan",
                "description": "Detailed treatment plan with cost estimates",
                "prompt_template": """Generate a treatment plan from this veterinary discussion.

Meeting Title: {meeting_title}
TRANSCRIPT:
{transcript}

Return ONLY valid JSON:
{{
  "patient": "Animal name and species",
  "condition": "Condition being treated",
  "treatment_options": [{{"option": "description", "estimated_cost": "cost range", "pros": ["benefits"], "cons": ["risks"]}}],
  "recommended_treatment": "Recommended option and rationale",
  "medications": [{{"name": "drug", "dose": "dosing", "duration": "length"}}],
  "monitoring_plan": ["Follow-up monitoring steps"],
  "owner_consent": "Consent discussion notes",
  "prognosis": "Expected outcome",
  "meeting_type": "Treatment Planning",
  "sentiment": "Productive"
}}""",
                "output_schema": {"condition": "str", "treatment_options": "list", "recommended_treatment": "str"},
                "required_fields": ["condition", "recommended_treatment"],
                "export_sections": ["Patient", "Condition", "Treatment Options", "Recommended Plan", "Prognosis"],
            },
            "client_communication": {
                "id": "client_communication",
                "name": "Client Communication Summary",
                "description": "Summary of communication with pet owner",
                "prompt_template": """Summarize this veterinary client communication.

Meeting Title: {meeting_title}
TRANSCRIPT:
{transcript}

Return ONLY valid JSON:
{{
  "pet_owner": "Owner name",
  "patient": "Animal name and species",
  "communication_type": "Phone call / In-person / Follow-up",
  "topics_discussed": ["Topics covered"],
  "owner_concerns": ["Concerns raised by owner"],
  "veterinary_advice": ["Advice given"],
  "instructions_given": ["Care instructions provided"],
  "compliance_notes": "Owner compliance with treatment plan",
  "next_contact": "Scheduled follow-up",
  "meeting_type": "Client Communication",
  "sentiment": "Productive"
}}""",
                "output_schema": {"topics_discussed": "list", "veterinary_advice": "list"},
                "required_fields": ["topics_discussed"],
                "export_sections": ["Owner", "Patient", "Discussion", "Advice", "Instructions"],
            },
        },
    },

    "hr": {
        "id": "hr",
        "name": "HR & Recruiting",
        "icon": "\U0001f465",
        "description": "Interview scorecards, performance reviews, exit interviews",
        "color": "#8B5CF6",
        "compliance_tags": ["bipa", "gdpr"],
        "templates": {
            "interview_scorecard": {
                "id": "interview_scorecard",
                "name": "Interview Scorecard",
                "description": "Structured candidate evaluation from interview",
                "prompt_template": """You are an HR professional. Analyze this job interview and create a structured scorecard.

Meeting Title: {meeting_title}
TRANSCRIPT:
{transcript}

Return ONLY valid JSON:
{{
  "candidate_name": "Candidate name",
  "position": "Role being interviewed for",
  "interviewer": "Interviewer name(s)",
  "interview_type": "Phone screen / Technical / Behavioral / Panel / Final",
  "competency_scores": [
    {{"competency": "skill area", "score": "1-5", "evidence": "Specific examples from interview"}}
  ],
  "strengths": ["Candidate strengths observed"],
  "concerns": ["Areas of concern or gaps"],
  "cultural_fit": "Assessment of cultural alignment",
  "technical_assessment": "Technical skills evaluation",
  "communication_skills": "Communication quality assessment",
  "questions_asked_by_candidate": ["Questions the candidate asked"],
  "recommendation": "Strong Hire / Hire / Maybe / No Hire",
  "notes": "Additional observations",
  "next_steps": ["Follow-up actions"],
  "meeting_type": "Interview",
  "sentiment": "Neutral"
}}

IMPORTANT: Be objective. Base assessments only on what was discussed. Do not make assumptions about protected characteristics.""",
                "output_schema": {"candidate_name": "str", "competency_scores": "list", "recommendation": "str"},
                "required_fields": ["candidate_name", "competency_scores", "recommendation"],
                "export_sections": ["Candidate", "Position", "Scores", "Strengths", "Concerns", "Recommendation"],
            },
            "performance_review": {
                "id": "performance_review",
                "name": "Performance Review Notes",
                "description": "Employee performance review documentation",
                "prompt_template": """Document this performance review meeting.

Meeting Title: {meeting_title}
TRANSCRIPT:
{transcript}

Return ONLY valid JSON:
{{
  "employee_name": "Employee name",
  "review_period": "Period being reviewed",
  "reviewer": "Manager/reviewer name",
  "overall_rating": "Exceeds / Meets / Below Expectations",
  "accomplishments": ["Key accomplishments discussed"],
  "goals_met": [{{"goal": "description", "status": "Met / Partially Met / Not Met", "notes": "details"}}],
  "areas_for_improvement": ["Development areas identified"],
  "new_goals": [{{"goal": "description", "timeline": "deadline", "metrics": "success criteria"}}],
  "career_development": "Career path discussion",
  "compensation_discussed": "Any comp changes discussed (yes/no/details)",
  "employee_feedback": "Feedback provided by employee",
  "action_items": ["Follow-up actions"],
  "meeting_type": "Performance Review",
  "sentiment": "Productive"
}}""",
                "output_schema": {"employee_name": "str", "overall_rating": "str", "accomplishments": "list", "new_goals": "list"},
                "required_fields": ["employee_name", "overall_rating"],
                "export_sections": ["Employee", "Rating", "Accomplishments", "Goals", "Development", "Action Items"],
            },
            "exit_interview": {
                "id": "exit_interview",
                "name": "Exit Interview Summary",
                "description": "Departing employee exit interview documentation",
                "prompt_template": """Document this exit interview for HR records.

Meeting Title: {meeting_title}
TRANSCRIPT:
{transcript}

Return ONLY valid JSON:
{{
  "employee_name": "Departing employee name",
  "department": "Department",
  "tenure": "Length of employment",
  "reason_for_leaving": "Primary reason for departure",
  "destination": "Where they are going (if shared)",
  "job_satisfaction": "Overall satisfaction assessment",
  "management_feedback": "Feedback about management",
  "culture_feedback": "Feedback about company culture",
  "compensation_feedback": "Feedback about pay and benefits",
  "what_would_change": ["Things they would change"],
  "what_worked_well": ["Things they valued"],
  "would_recommend": "Would they recommend the company (Yes/No/Maybe)",
  "retention_insights": ["Key insights for retention strategy"],
  "knowledge_transfer": ["Critical knowledge to transfer"],
  "meeting_type": "Exit Interview",
  "sentiment": "Neutral"
}}""",
                "output_schema": {"employee_name": "str", "reason_for_leaving": "str", "retention_insights": "list"},
                "required_fields": ["employee_name", "reason_for_leaving"],
                "export_sections": ["Employee", "Reason", "Feedback", "Retention Insights", "Knowledge Transfer"],
            },
        },
    },

    "education": {
        "id": "education",
        "name": "Education",
        "icon": "\U0001f393",
        "description": "IEP notes, parent-teacher conferences, faculty meetings",
        "color": "#06B6D4",
        "compliance_tags": ["ferpa", "coppa"],
        "templates": {
            "iep_meeting": {
                "id": "iep_meeting",
                "name": "IEP Meeting Notes",
                "description": "Individualized Education Program meeting documentation",
                "prompt_template": """You are a special education coordinator. Document this IEP meeting.

Meeting Title: {meeting_title}
TRANSCRIPT:
{transcript}

Return ONLY valid JSON:
{{
  "student_info": "Student name/identifier (use initials for privacy)",
  "meeting_date": "Date of meeting",
  "attendees": [{{"name": "person", "role": "Parent/Teacher/Specialist/Administrator"}}],
  "current_performance": "Present levels of academic achievement and functional performance",
  "goals_review": [{{"goal": "description", "progress": "Met/Progressing/Not Met", "evidence": "data cited"}}],
  "new_goals": [{{"goal": "new IEP goal", "measurable_criteria": "how progress will be measured", "timeline": "target date"}}],
  "accommodations": ["Accommodations discussed or modified"],
  "modifications": ["Curriculum modifications discussed"],
  "related_services": ["Speech, OT, PT, counseling, etc."],
  "placement": "Least restrictive environment discussion",
  "parent_concerns": ["Concerns raised by parents/guardians"],
  "assessment_results": ["Any assessment results reviewed"],
  "transition_planning": "Post-secondary transition if applicable",
  "next_review_date": "Scheduled next IEP review",
  "meeting_type": "IEP Meeting",
  "sentiment": "Productive"
}}

IMPORTANT: Protect student privacy. Use initials if full names are mentioned. This is FERPA-protected information.""",
                "output_schema": {"current_performance": "str", "new_goals": "list", "accommodations": "list"},
                "required_fields": ["current_performance", "new_goals", "accommodations"],
                "export_sections": ["Student", "Attendees", "Current Performance", "Goals Review", "New Goals", "Accommodations", "Services"],
            },
            "parent_teacher": {
                "id": "parent_teacher",
                "name": "Parent-Teacher Conference",
                "description": "Parent-teacher meeting documentation",
                "prompt_template": """Document this parent-teacher conference.

Meeting Title: {meeting_title}
TRANSCRIPT:
{transcript}

Return ONLY valid JSON:
{{
  "student": "Student name/initials",
  "grade_level": "Grade",
  "teacher": "Teacher name",
  "academic_performance": {{"subject": "assessment"}},
  "behavioral_observations": "Classroom behavior notes",
  "social_emotional": "Social-emotional development",
  "strengths": ["Student strengths identified"],
  "areas_for_growth": ["Areas needing improvement"],
  "parent_concerns": ["Concerns raised by parents"],
  "parent_insights": ["Home observations shared by parents"],
  "strategies": ["Strategies discussed for support"],
  "homework_study": "Homework and study habits discussed",
  "next_steps": ["Action items for teacher and parents"],
  "meeting_type": "Parent-Teacher Conference",
  "sentiment": "Productive"
}}""",
                "output_schema": {"academic_performance": "dict", "strengths": "list", "next_steps": "list"},
                "required_fields": ["academic_performance", "next_steps"],
                "export_sections": ["Student", "Academic Performance", "Strengths", "Growth Areas", "Strategies", "Next Steps"],
            },
            "faculty_meeting": {
                "id": "faculty_meeting",
                "name": "Faculty Meeting Minutes",
                "description": "School or department faculty meeting documentation",
                "prompt_template": """Document this faculty/staff meeting.

Meeting Title: {meeting_title}
TRANSCRIPT:
{transcript}

Return ONLY valid JSON:
{{
  "meeting_date": "Date",
  "attendees": ["Faculty/staff present"],
  "agenda_items": [{{"topic": "description", "discussion": "key points", "decision": "outcome"}}],
  "announcements": ["Administrative announcements"],
  "curriculum_updates": ["Curriculum changes or updates discussed"],
  "student_concerns": ["Student-related issues discussed (no names)"],
  "professional_development": ["PD opportunities or requirements"],
  "policy_changes": ["Policy updates"],
  "resource_requests": ["Resources or budget requests"],
  "action_items": [{{"task": "description", "responsible": "person", "deadline": "date"}}],
  "next_meeting": "Date of next meeting",
  "meeting_type": "Faculty Meeting",
  "sentiment": "Productive"
}}""",
                "output_schema": {"agenda_items": "list", "action_items": "list"},
                "required_fields": ["agenda_items", "action_items"],
                "export_sections": ["Attendees", "Agenda Items", "Announcements", "Action Items", "Next Meeting"],
            },
        },
    },

    "sales": {
        "id": "sales",
        "name": "Sales & Consulting",
        "icon": "\U0001f4c8",
        "description": "Call summaries, discovery notes, QBRs",
        "color": "#F97316",
        "compliance_tags": [],
        "templates": {
            "sales_call": {
                "id": "sales_call",
                "name": "Sales Call Summary",
                "description": "Sales conversation analysis with next steps",
                "prompt_template": """Analyze this sales call and create a structured summary.

Meeting Title: {meeting_title}
TRANSCRIPT:
{transcript}

Return ONLY valid JSON:
{{
  "prospect_company": "Company name",
  "contact_name": "Person spoken to",
  "contact_role": "Their title/role",
  "call_type": "Cold call / Discovery / Demo / Follow-up / Negotiation / Closing",
  "pain_points": ["Problems or challenges identified"],
  "needs_identified": ["Specific needs expressed"],
  "budget_signals": "Budget information or signals",
  "timeline": "Decision timeline discussed",
  "decision_makers": ["Key stakeholders and decision makers"],
  "competition": ["Competitors mentioned"],
  "objections": [{{"objection": "concern raised", "response": "how it was addressed"}}],
  "interest_level": "Hot / Warm / Cold",
  "next_steps": [{{"action": "task", "owner": "person", "deadline": "date"}}],
  "deal_size": "Estimated deal value if discussed",
  "meeting_type": "Sales Call",
  "sentiment": "Positive"
}}""",
                "output_schema": {"prospect_company": "str", "pain_points": "list", "next_steps": "list", "interest_level": "str"},
                "required_fields": ["prospect_company", "pain_points", "next_steps"],
                "export_sections": ["Prospect", "Pain Points", "Needs", "Objections", "Interest Level", "Next Steps"],
            },
            "discovery_notes": {
                "id": "discovery_notes",
                "name": "Discovery Notes",
                "description": "Prospect discovery call documentation",
                "prompt_template": """Document this discovery call using MEDDPICC methodology.

Meeting Title: {meeting_title}
TRANSCRIPT:
{transcript}

Return ONLY valid JSON:
{{
  "prospect": "Company name",
  "metrics": "Quantifiable measures of success the prospect cares about",
  "economic_buyer": "Who has budget authority",
  "decision_criteria": ["How they will evaluate solutions"],
  "decision_process": "Steps in their buying process",
  "paper_process": "Legal/procurement process",
  "implications_of_pain": "Business impact of not solving the problem",
  "champion": "Internal advocate identified",
  "competition": "Competitive landscape",
  "current_state": "Current tools and processes",
  "desired_state": "What success looks like",
  "gaps": ["Gaps between current and desired state"],
  "next_steps": ["Follow-up actions"],
  "meeting_type": "Discovery Call",
  "sentiment": "Productive"
}}""",
                "output_schema": {"prospect": "str", "implications_of_pain": "str", "next_steps": "list"},
                "required_fields": ["prospect", "next_steps"],
                "export_sections": ["Prospect", "MEDDPICC Analysis", "Current vs Desired State", "Next Steps"],
            },
            "qbr_notes": {
                "id": "qbr_notes",
                "name": "QBR Notes",
                "description": "Quarterly Business Review documentation",
                "prompt_template": """Document this Quarterly Business Review.

Meeting Title: {meeting_title}
TRANSCRIPT:
{transcript}

Return ONLY valid JSON:
{{
  "account": "Customer/account name",
  "quarter": "Quarter being reviewed",
  "attendees": ["Meeting attendees and roles"],
  "performance_summary": "Overall account health and performance",
  "kpis_reviewed": [{{"metric": "name", "target": "goal", "actual": "result", "status": "On Track/Behind/Exceeded"}}],
  "wins": ["Successes this quarter"],
  "challenges": ["Challenges or issues faced"],
  "product_feedback": ["Feature requests or product feedback"],
  "expansion_opportunities": ["Upsell/cross-sell opportunities"],
  "risk_factors": ["Churn risk indicators"],
  "strategic_initiatives": ["Planned initiatives for next quarter"],
  "action_items": [{{"task": "description", "owner": "person", "deadline": "date"}}],
  "meeting_type": "QBR",
  "sentiment": "Productive"
}}""",
                "output_schema": {"account": "str", "kpis_reviewed": "list", "action_items": "list"},
                "required_fields": ["account", "action_items"],
                "export_sections": ["Account", "Performance", "KPIs", "Wins", "Challenges", "Opportunities", "Action Items"],
            },
        },
    },

    "construction": {
        "id": "construction",
        "name": "Construction",
        "icon": "\U0001f3d7\ufe0f",
        "description": "Site minutes, safety briefings, change orders, daily logs",
        "color": "#EAB308",
        "compliance_tags": [],
        "templates": {
            "site_meeting": {
                "id": "site_meeting",
                "name": "Site Meeting Minutes",
                "description": "Construction site meeting documentation",
                "prompt_template": """Document this construction site meeting.

Meeting Title: {meeting_title}
TRANSCRIPT:
{transcript}

Return ONLY valid JSON:
{{
  "project_name": "Project name",
  "meeting_date": "Date",
  "location": "Site location",
  "attendees": [{{"name": "person", "company": "firm", "role": "title"}}],
  "project_status": "Overall project status update",
  "schedule_update": "Schedule status and any delays",
  "budget_update": "Budget status and any variances",
  "work_completed": ["Work completed since last meeting"],
  "work_in_progress": ["Current active work items"],
  "upcoming_work": ["Planned work for next period"],
  "issues": [{{"issue": "description", "impact": "schedule/budget/safety", "resolution": "proposed fix"}}],
  "rfi_submittals": ["RFIs or submittals discussed"],
  "change_orders": ["Change orders discussed or pending"],
  "safety_items": ["Safety concerns or incidents"],
  "action_items": [{{"task": "description", "responsible": "person/company", "deadline": "date"}}],
  "next_meeting": "Next meeting date",
  "meeting_type": "Site Meeting",
  "sentiment": "Productive"
}}""",
                "output_schema": {"project_name": "str", "project_status": "str", "action_items": "list"},
                "required_fields": ["project_name", "project_status", "action_items"],
                "export_sections": ["Project", "Status", "Work Progress", "Issues", "Change Orders", "Safety", "Action Items"],
            },
            "safety_briefing": {
                "id": "safety_briefing",
                "name": "Safety Briefing Notes",
                "description": "Toolbox talk and safety meeting documentation",
                "prompt_template": """Document this construction safety briefing/toolbox talk.

Meeting Title: {meeting_title}
TRANSCRIPT:
{transcript}

Return ONLY valid JSON:
{{
  "project": "Project name",
  "date": "Date",
  "conducted_by": "Safety officer/foreman name",
  "attendees": ["Workers present"],
  "topic": "Primary safety topic",
  "hazards_identified": ["Hazards discussed"],
  "ppe_requirements": ["Required PPE discussed"],
  "safety_procedures": ["Procedures reviewed"],
  "incidents_reported": ["Any incidents or near-misses reported"],
  "corrective_actions": ["Corrective actions discussed"],
  "emergency_procedures": "Emergency procedures reviewed",
  "weather_conditions": "Weather impact on safety",
  "questions_raised": ["Questions from workers"],
  "meeting_type": "Safety Briefing",
  "sentiment": "Productive"
}}""",
                "output_schema": {"topic": "str", "hazards_identified": "list", "safety_procedures": "list"},
                "required_fields": ["topic", "hazards_identified"],
                "export_sections": ["Topic", "Hazards", "PPE", "Procedures", "Incidents", "Corrective Actions"],
            },
            "daily_log": {
                "id": "daily_log",
                "name": "Daily Log",
                "description": "End-of-day construction site log",
                "prompt_template": """Generate a construction daily log from this discussion.

Meeting Title: {meeting_title}
TRANSCRIPT:
{transcript}

Return ONLY valid JSON:
{{
  "project": "Project name",
  "date": "Date",
  "weather": "Weather conditions",
  "workforce": {{"total_workers": "count", "trades": ["trade types on site"]}},
  "equipment_on_site": ["Equipment used today"],
  "work_performed": ["Detailed work activities"],
  "materials_received": ["Deliveries received"],
  "visitors": ["Visitors and inspectors on site"],
  "delays": ["Any delays and causes"],
  "safety_incidents": ["Safety incidents or near-misses"],
  "quality_issues": ["Quality concerns noted"],
  "tomorrow_plan": ["Planned work for tomorrow"],
  "meeting_type": "Daily Log",
  "sentiment": "Productive"
}}""",
                "output_schema": {"work_performed": "list", "delays": "list"},
                "required_fields": ["work_performed"],
                "export_sections": ["Project", "Weather", "Workforce", "Work Performed", "Delays", "Safety", "Tomorrow"],
            },
        },
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # TIER 3 — EXPANSION VERTICALS
    # ═══════════════════════════════════════════════════════════════════════════
    "government": {
        "id": "government",
        "name": "Government",
        "icon": "\U0001f3db\ufe0f",
        "description": "Council minutes, police interviews, social worker notes",
        "color": "#6366F1",
        "compliance_tags": ["cjis", "fedramp"],
        "templates": {
            "council_minutes": {
                "id": "council_minutes",
                "name": "City Council Minutes",
                "description": "Official government meeting minutes",
                "prompt_template": """Generate official meeting minutes from this government meeting.

Meeting Title: {meeting_title}
TRANSCRIPT:
{transcript}

Return ONLY valid JSON:
{{
  "body": "Name of the government body",
  "meeting_type_gov": "Regular / Special / Emergency",
  "date": "Meeting date",
  "location": "Meeting location",
  "called_to_order": "Time called to order",
  "presiding_officer": "Chair/Mayor/President",
  "members_present": ["Members present"],
  "members_absent": ["Members absent"],
  "quorum": "Quorum present (Yes/No)",
  "approval_of_minutes": "Prior minutes approved (Yes/No, any corrections)",
  "public_comment": ["Public comments received"],
  "agenda_items": [{{"item": "description", "discussion": "summary of discussion", "motion": "motion made", "vote": "result (Passed/Failed/Tabled)", "vote_count": "for-against"}}],
  "ordinances": ["Ordinances introduced or voted on"],
  "resolutions": ["Resolutions considered"],
  "reports": ["Committee and staff reports"],
  "announcements": ["Administrative announcements"],
  "adjournment": "Time adjourned",
  "next_meeting": "Next scheduled meeting",
  "meeting_type": "Government Meeting",
  "sentiment": "Neutral"
}}""",
                "output_schema": {"body": "str", "agenda_items": "list", "members_present": "list"},
                "required_fields": ["body", "agenda_items"],
                "export_sections": ["Call to Order", "Roll Call", "Public Comment", "Agenda Items", "Votes", "Adjournment"],
            },
            "social_worker_notes": {
                "id": "social_worker_notes",
                "name": "Social Worker Case Notes",
                "description": "Case management and client visit documentation",
                "prompt_template": """Document this social work client interaction. Protect client privacy.

Meeting Title: {meeting_title}
TRANSCRIPT:
{transcript}

Return ONLY valid JSON:
{{
  "client_id": "Use initials only for privacy",
  "case_type": "Type of case (child welfare, adult services, mental health, etc.)",
  "visit_type": "Home visit / Office visit / Phone / Virtual",
  "date": "Date of contact",
  "presenting_issues": ["Current issues or concerns"],
  "client_status": "Overall client/family status assessment",
  "safety_assessment": "Safety concerns identified (immediate/potential/none)",
  "services_discussed": ["Services discussed or referred"],
  "interventions": ["Interventions provided during visit"],
  "progress_toward_goals": [{{"goal": "description", "progress": "status"}}],
  "barriers": ["Barriers to progress identified"],
  "strengths": ["Client/family strengths observed"],
  "next_steps": ["Planned follow-up actions"],
  "supervisor_consultation_needed": "Yes/No and topic if yes",
  "meeting_type": "Case Contact",
  "sentiment": "Neutral"
}}""",
                "output_schema": {"case_type": "str", "presenting_issues": "list", "safety_assessment": "str", "next_steps": "list"},
                "required_fields": ["presenting_issues", "safety_assessment", "next_steps"],
                "export_sections": ["Client", "Case Type", "Issues", "Safety", "Interventions", "Progress", "Next Steps"],
            },
        },
    },

    "religious": {
        "id": "religious",
        "name": "Religious & Nonprofit",
        "icon": "\U0001f54a\ufe0f",
        "description": "Board minutes, pastoral notes, donor meetings, HOA minutes",
        "color": "#EC4899",
        "compliance_tags": [],
        "templates": {
            "board_minutes": {
                "id": "board_minutes",
                "name": "Board Meeting Minutes",
                "description": "Nonprofit or church board meeting documentation",
                "prompt_template": """Document this board meeting for the organization's records.

Meeting Title: {meeting_title}
TRANSCRIPT:
{transcript}

Return ONLY valid JSON:
{{
  "organization": "Organization name",
  "meeting_date": "Date",
  "board_members_present": ["Members present"],
  "board_members_absent": ["Members absent"],
  "quorum": "Quorum achieved (Yes/No)",
  "opening": "Opening prayer/invocation if applicable",
  "minutes_approval": "Prior minutes approved",
  "financial_report": "Treasury/financial report summary",
  "committee_reports": [{{"committee": "name", "report": "summary"}}],
  "old_business": [{{"item": "description", "discussion": "summary", "action": "decision"}}],
  "new_business": [{{"item": "description", "discussion": "summary", "action": "decision"}}],
  "motions": [{{"motion": "description", "moved_by": "name", "seconded_by": "name", "result": "Passed/Failed"}}],
  "action_items": [{{"task": "description", "responsible": "person", "deadline": "date"}}],
  "next_meeting": "Date of next meeting",
  "adjournment": "Time adjourned",
  "meeting_type": "Board Meeting",
  "sentiment": "Productive"
}}""",
                "output_schema": {"organization": "str", "motions": "list", "action_items": "list"},
                "required_fields": ["organization", "action_items"],
                "export_sections": ["Organization", "Attendance", "Financial Report", "Old Business", "New Business", "Motions", "Action Items"],
            },
            "pastoral_notes": {
                "id": "pastoral_notes",
                "name": "Pastoral Counseling Notes",
                "description": "Confidential pastoral care documentation",
                "prompt_template": """Document this pastoral counseling session. This is clergy-penitent privileged communication.

Meeting Title: {meeting_title}
TRANSCRIPT:
{transcript}

Return ONLY valid JSON:
{{
  "session_date": "Date",
  "session_type": "Individual / Couple / Family / Pre-marital / Grief / Crisis",
  "presenting_concern": "General category of concern (do NOT include specific confessional content)",
  "spiritual_themes": ["Spiritual themes discussed"],
  "scripture_references": ["Scripture passages referenced"],
  "pastoral_observations": "General pastoral observations",
  "support_provided": ["Types of support offered"],
  "referrals": ["Professional referrals made (counselor, therapist, etc.)",],
  "prayer_requests": ["Prayer needs identified"],
  "follow_up": "Planned follow-up",
  "meeting_type": "Pastoral Counseling",
  "sentiment": "Neutral"
}}

CRITICAL: This is CLERGY-PENITENT PRIVILEGED communication. Do NOT include specific confessional details. Document themes and categories only.""",
                "output_schema": {"session_type": "str", "presenting_concern": "str", "follow_up": "str"},
                "required_fields": ["session_type", "presenting_concern"],
                "export_sections": ["Session Type", "Concern", "Spiritual Themes", "Support", "Referrals", "Follow-up"],
            },
            "donor_meeting": {
                "id": "donor_meeting",
                "name": "Donor Meeting Notes",
                "description": "Major donor cultivation and stewardship notes",
                "prompt_template": """Document this donor meeting for stewardship records.

Meeting Title: {meeting_title}
TRANSCRIPT:
{transcript}

Return ONLY valid JSON:
{{
  "donor_name": "Donor name",
  "relationship_stage": "Prospect / Cultivated / Solicited / Donor / Major Donor",
  "meeting_purpose": "Purpose of the meeting",
  "interests_discussed": ["Programs and causes of interest"],
  "giving_history": "Known giving history discussed",
  "capacity_signals": "Capacity indicators",
  "ask_amount": "Ask amount if solicitation was made",
  "response": "Donor response to ask",
  "stewardship_notes": "Stewardship and recognition preferences",
  "personal_notes": "Personal interests, family, milestones",
  "next_steps": ["Follow-up actions"],
  "meeting_type": "Donor Meeting",
  "sentiment": "Positive"
}}""",
                "output_schema": {"donor_name": "str", "meeting_purpose": "str", "next_steps": "list"},
                "required_fields": ["donor_name", "meeting_purpose", "next_steps"],
                "export_sections": ["Donor", "Purpose", "Interests", "Response", "Stewardship", "Next Steps"],
            },
        },
    },

    "insurance": {
        "id": "insurance",
        "name": "Insurance",
        "icon": "\U0001f6e1\ufe0f",
        "description": "Claims meetings, underwriting reviews, policy reviews",
        "color": "#14B8A6",
        "compliance_tags": ["sec_17a4"],
        "templates": {
            "claims_meeting": {
                "id": "claims_meeting",
                "name": "Claims Meeting Notes",
                "description": "Insurance claims review and discussion",
                "prompt_template": """Document this insurance claims meeting.

Meeting Title: {meeting_title}
TRANSCRIPT:
{transcript}

Return ONLY valid JSON:
{{
  "claim_number": "Claim reference number",
  "policyholder": "Policyholder name",
  "claim_type": "Type of claim (auto, property, liability, health, etc.)",
  "date_of_loss": "Date of incident",
  "claim_description": "Description of the claim",
  "coverage_analysis": "Coverage determination discussion",
  "damages_assessed": "Damage assessment and valuation",
  "investigation_findings": ["Investigation findings"],
  "liability_assessment": "Liability determination",
  "reserve_amount": "Reserve amount discussed",
  "settlement_discussion": "Settlement considerations",
  "fraud_indicators": ["Any fraud indicators noted"],
  "next_steps": ["Action items"],
  "meeting_type": "Claims Review",
  "sentiment": "Neutral"
}}""",
                "output_schema": {"claim_type": "str", "coverage_analysis": "str", "next_steps": "list"},
                "required_fields": ["claim_type", "coverage_analysis", "next_steps"],
                "export_sections": ["Claim", "Coverage", "Damages", "Investigation", "Settlement", "Next Steps"],
            },
            "underwriting_review": {
                "id": "underwriting_review",
                "name": "Underwriting Review",
                "description": "Risk assessment and underwriting decision documentation",
                "prompt_template": """Document this underwriting review meeting.

Meeting Title: {meeting_title}
TRANSCRIPT:
{transcript}

Return ONLY valid JSON:
{{
  "applicant": "Applicant name/entity",
  "policy_type": "Type of coverage",
  "risk_assessment": "Overall risk assessment",
  "risk_factors": [{{"factor": "description", "severity": "Low/Medium/High"}}],
  "loss_history": "Loss history reviewed",
  "pricing_discussion": "Premium and pricing considerations",
  "terms_conditions": ["Special terms or conditions proposed"],
  "exclusions": ["Exclusions discussed"],
  "reinsurance_needs": "Reinsurance considerations",
  "decision": "Accept / Decline / Modify / Refer",
  "rationale": "Decision rationale",
  "next_steps": ["Follow-up actions"],
  "meeting_type": "Underwriting Review",
  "sentiment": "Neutral"
}}""",
                "output_schema": {"applicant": "str", "risk_assessment": "str", "decision": "str"},
                "required_fields": ["applicant", "risk_assessment", "decision"],
                "export_sections": ["Applicant", "Risk Assessment", "Risk Factors", "Pricing", "Decision", "Next Steps"],
            },
        },
    },

    "realestate": {
        "id": "realestate",
        "name": "Real Estate",
        "icon": "\U0001f3e0",
        "description": "Showings, closings, inspection reviews",
        "color": "#84CC16",
        "compliance_tags": [],
        "templates": {
            "property_showing": {
                "id": "property_showing",
                "name": "Property Showing Notes",
                "description": "Client property showing and feedback",
                "prompt_template": """Document this property showing.

Meeting Title: {meeting_title}
TRANSCRIPT:
{transcript}

Return ONLY valid JSON:
{{
  "property_address": "Property address",
  "listing_price": "Listing price",
  "client_name": "Buyer/tenant name",
  "property_type": "Type (SFR, condo, commercial, etc.)",
  "client_reaction": "Overall client reaction",
  "liked": ["Features client liked"],
  "concerns": ["Concerns or dislikes expressed"],
  "questions": ["Questions asked about the property"],
  "comparable_mentions": ["Other properties compared to"],
  "price_discussion": "Any price or offer discussion",
  "interest_level": "High / Medium / Low / Not interested",
  "next_steps": ["Follow-up actions"],
  "meeting_type": "Property Showing",
  "sentiment": "Neutral"
}}""",
                "output_schema": {"property_address": "str", "client_reaction": "str", "interest_level": "str"},
                "required_fields": ["property_address", "client_reaction", "interest_level"],
                "export_sections": ["Property", "Client Reaction", "Liked", "Concerns", "Interest Level", "Next Steps"],
            },
            "closing_meeting": {
                "id": "closing_meeting",
                "name": "Closing Meeting Notes",
                "description": "Real estate closing/settlement documentation",
                "prompt_template": """Document this real estate closing meeting.

Meeting Title: {meeting_title}
TRANSCRIPT:
{transcript}

Return ONLY valid JSON:
{{
  "property_address": "Property address",
  "buyer": "Buyer name",
  "seller": "Seller name",
  "sale_price": "Final sale price",
  "closing_date": "Closing date",
  "documents_signed": ["Documents executed"],
  "contingencies_cleared": ["Contingencies satisfied"],
  "outstanding_items": ["Items not yet resolved"],
  "financial_summary": "Closing costs and proceeds discussion",
  "title_issues": "Any title issues discussed",
  "inspection_items": "Inspection-related items addressed",
  "possession_date": "Possession/move-in date",
  "next_steps": ["Post-closing action items"],
  "meeting_type": "Closing",
  "sentiment": "Positive"
}}""",
                "output_schema": {"property_address": "str", "sale_price": "str", "documents_signed": "list"},
                "required_fields": ["property_address", "sale_price"],
                "export_sections": ["Property", "Parties", "Financial", "Documents", "Outstanding Items", "Possession"],
            },
        },
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # UNIVERSAL
    # ═══════════════════════════════════════════════════════════════════════════
    "general": {
        "id": "general",
        "name": "General",
        "icon": "\U0001f4cb",
        "description": "Universal meeting notes for any context",
        "color": "#7C3AED",
        "compliance_tags": [],
        "templates": {
            "general_notes": {
                "id": "general_notes",
                "name": "General Meeting Notes",
                "description": "Standard meeting analysis with summaries, decisions, and action items",
                "prompt_template": """You are an expert meeting analyst. Analyze the following meeting transcript and extract structured information.

Meeting Title: {meeting_title}

TRANSCRIPT:
{transcript}

Please provide a comprehensive analysis in the following EXACT JSON format:

{{
  "summary": ["Key point 1", "Key point 2", "Key point 3"],
  "key_decisions": ["Decision 1", "Decision 2"],
  "action_items": [{{"task": "Task description", "assignee": "Person or TBD", "deadline": "Date or Not specified", "priority": "High/Medium/Low"}}],
  "discussion_topics": ["Topic 1", "Topic 2"],
  "follow_up_items": ["Follow-up item 1"],
  "meeting_type": "Planning / Status Update / Brainstorm / Review / Decision / Interview / Training / Other",
  "sentiment": "Productive / Challenging / Neutral / Positive / Tense"
}}

IMPORTANT: Return ONLY valid JSON. Be specific — use real names, dates, and topics from the transcript.""",
                "output_schema": {"summary": "list", "key_decisions": "list", "action_items": "list", "discussion_topics": "list"},
                "required_fields": ["summary", "action_items"],
                "export_sections": ["Summary", "Key Decisions", "Action Items", "Discussion Topics", "Follow-up"],
            },
        },
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def get_vertical(vertical_id):
    """Return the full vertical config dict, or None if not found."""
    return VERTICALS.get(vertical_id)


def get_template(vertical_id, template_id):
    """Return a specific template dict, or None."""
    vertical = VERTICALS.get(vertical_id)
    if vertical:
        return vertical.get("templates", {}).get(template_id)
    return None


def get_all_verticals():
    """Return a list of all verticals with basic info (id, name, icon, description, color)."""
    return [
        {
            "id": v["id"],
            "name": v["name"],
            "icon": v["icon"],
            "description": v["description"],
            "color": v.get("color", "#7C3AED"),
        }
        for v in VERTICALS.values()
    ]


def build_prompt(vertical_id, template_id, transcript, meeting_title="Meeting"):
    """Build the complete prompt string by substituting transcript and title into the template."""
    template = get_template(vertical_id, template_id)
    if not template:
        return None
    return template["prompt_template"].format(
        transcript=transcript,
        meeting_title=meeting_title,
    )


def parse_template_output(vertical_id, template_id, raw_json):
    """
    Parse and validate raw JSON output against the template schema.
    Fills in defaults for missing required fields.
    Returns parsed dict or None on failure.
    """
    template = get_template(vertical_id, template_id)
    if not template:
        return None

    # Try to parse JSON
    parsed = None

    # Direct parse
    try:
        parsed = json.loads(raw_json)
    except (json.JSONDecodeError, TypeError):
        pass

    # Try markdown code fences
    if parsed is None:
        match = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", str(raw_json))
        if match:
            try:
                parsed = json.loads(match.group(1))
            except json.JSONDecodeError:
                pass

    # Try finding { ... }
    if parsed is None:
        match = re.search(r"\{[\s\S]+\}", str(raw_json))
        if match:
            try:
                parsed = json.loads(match.group(0))
            except json.JSONDecodeError:
                pass

    if parsed is None:
        return None

    # Fill defaults for missing required fields
    for field in template.get("required_fields", []):
        if field not in parsed:
            schema_type = template.get("output_schema", {}).get(field, "str")
            if "list" in str(schema_type):
                parsed[field] = []
            elif "dict" in str(schema_type):
                parsed[field] = {}
            else:
                parsed[field] = "Not available"

    return parsed


def get_vertical_export_header(vertical_id):
    """Return a formatted header string for exports."""
    vertical = VERTICALS.get(vertical_id)
    if not vertical:
        return "MeetingMind — Meeting Notes"
    return f"MeetingMind — {vertical['icon']} {vertical['name']}"
