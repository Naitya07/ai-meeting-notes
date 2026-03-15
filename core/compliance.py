"""
MeetingMind — Compliance & Consent Management Engine
50+ jurisdictions | 10 compliance frameworks | Audit logging
Edge-native architecture = automatic compliance for most frameworks.
"""

import json
import os
import time
import locale
from datetime import datetime
from pathlib import Path
from typing import Optional

# ─────────────────────────────────────────────────────────────────────────────
# STORAGE PATHS
# ─────────────────────────────────────────────────────────────────────────────
STORAGE_DIR = Path.home() / ".meetingmind"
AUDIT_DIR = STORAGE_DIR / "audit"

# ─────────────────────────────────────────────────────────────────────────────
# JURISDICTIONS — Recording consent laws
# ─────────────────────────────────────────────────────────────────────────────
JURISDICTIONS = {
    # ── US ALL-PARTY CONSENT STATES ──
    "US-CA": {"code": "US-CA", "name": "California", "consent_type": "all_party", "description": "California Penal Code 632 — all parties must consent to recording", "fine_range": "$2,500 per violation + civil damages", "special_notes": "Criminal and civil liability. Also CCPA for data privacy."},
    "US-CT": {"code": "US-CT", "name": "Connecticut", "consent_type": "all_party", "description": "All parties must consent", "fine_range": "Up to $5,000 fine", "special_notes": ""},
    "US-FL": {"code": "US-FL", "name": "Florida", "consent_type": "all_party", "description": "Florida Statute 934.03 — all parties must consent", "fine_range": "Felony, up to 5 years prison", "special_notes": "One of the strictest states"},
    "US-IL": {"code": "US-IL", "name": "Illinois", "consent_type": "all_party", "description": "All parties must consent. BIPA applies to voiceprints.", "fine_range": "$1,000-$5,000 per BIPA violation", "special_notes": "BIPA: Biometric Information Privacy Act. Voiceprints are protected biometric identifiers."},
    "US-MA": {"code": "US-MA", "name": "Massachusetts", "consent_type": "all_party", "description": "All parties must consent — one of the strictest", "fine_range": "Up to $10,000 fine + 5 years prison", "special_notes": "Strictest wiretapping law in the US"},
    "US-MD": {"code": "US-MD", "name": "Maryland", "consent_type": "all_party", "description": "All parties must consent", "fine_range": "Up to $10,000 fine", "special_notes": ""},
    "US-MT": {"code": "US-MT", "name": "Montana", "consent_type": "all_party", "description": "All parties must consent", "fine_range": "Misdemeanor", "special_notes": ""},
    "US-NH": {"code": "US-NH", "name": "New Hampshire", "consent_type": "all_party", "description": "All parties must consent", "fine_range": "Class B felony", "special_notes": ""},
    "US-PA": {"code": "US-PA", "name": "Pennsylvania", "consent_type": "all_party", "description": "All parties must consent", "fine_range": "Felony, up to 7 years", "special_notes": ""},
    "US-WA": {"code": "US-WA", "name": "Washington", "consent_type": "all_party", "description": "All parties must consent — RCW 9.73.030", "fine_range": "Gross misdemeanor + civil damages", "special_notes": ""},
    "US-NV": {"code": "US-NV", "name": "Nevada", "consent_type": "all_party", "description": "All parties must consent for in-person", "fine_range": "Category D felony", "special_notes": "Phone calls are one-party"},

    # ── US ONE-PARTY CONSENT STATES (representative set) ──
    "US-NY": {"code": "US-NY", "name": "New York", "consent_type": "one_party", "description": "One party consent — NY Penal Law 250.00", "fine_range": "Class E felony for illegal wiretapping", "special_notes": ""},
    "US-TX": {"code": "US-TX", "name": "Texas", "consent_type": "one_party", "description": "One party consent", "fine_range": "State jail felony", "special_notes": ""},
    "US-GA": {"code": "US-GA", "name": "Georgia", "consent_type": "one_party", "description": "One party consent", "fine_range": "Felony", "special_notes": ""},
    "US-OH": {"code": "US-OH", "name": "Ohio", "consent_type": "one_party", "description": "One party consent", "fine_range": "Felony of the 4th degree", "special_notes": ""},
    "US-NC": {"code": "US-NC", "name": "North Carolina", "consent_type": "one_party", "description": "One party consent", "fine_range": "Class H felony", "special_notes": ""},
    "US-NJ": {"code": "US-NJ", "name": "New Jersey", "consent_type": "one_party", "description": "One party consent", "fine_range": "3rd degree crime", "special_notes": ""},
    "US-VA": {"code": "US-VA", "name": "Virginia", "consent_type": "one_party", "description": "One party consent", "fine_range": "Class 6 felony", "special_notes": ""},
    "US-MI": {"code": "US-MI", "name": "Michigan", "consent_type": "one_party", "description": "One party consent", "fine_range": "Felony, up to 2 years", "special_notes": ""},
    "US-CO": {"code": "US-CO", "name": "Colorado", "consent_type": "one_party", "description": "One party consent", "fine_range": "Class 6 felony", "special_notes": ""},
    "US-AZ": {"code": "US-AZ", "name": "Arizona", "consent_type": "one_party", "description": "One party consent", "fine_range": "Class 5 felony", "special_notes": ""},
    "US-MN": {"code": "US-MN", "name": "Minnesota", "consent_type": "one_party", "description": "One party consent", "fine_range": "Felony", "special_notes": ""},
    "US-WI": {"code": "US-WI", "name": "Wisconsin", "consent_type": "one_party", "description": "One party consent", "fine_range": "Class H felony", "special_notes": ""},
    "US-TN": {"code": "US-TN", "name": "Tennessee", "consent_type": "one_party", "description": "One party consent", "fine_range": "Class D felony", "special_notes": ""},
    "US-IN": {"code": "US-IN", "name": "Indiana", "consent_type": "one_party", "description": "One party consent", "fine_range": "Level 5 felony", "special_notes": ""},
    "US-MO": {"code": "US-MO", "name": "Missouri", "consent_type": "one_party", "description": "One party consent", "fine_range": "Class E felony", "special_notes": ""},
    "US-OR": {"code": "US-OR", "name": "Oregon", "consent_type": "one_party", "description": "One party consent", "fine_range": "Class A misdemeanor", "special_notes": ""},
    "US-DC": {"code": "US-DC", "name": "District of Columbia", "consent_type": "one_party", "description": "One party consent", "fine_range": "Up to $10,000 fine", "special_notes": ""},

    # ── CANADA ──
    "CA-FED": {"code": "CA-FED", "name": "Canada (Federal)", "consent_type": "one_party", "description": "Criminal Code s.184 — one party consent federally", "fine_range": "Up to 5 years imprisonment", "special_notes": "PIPEDA applies for private sector data handling"},
    "CA-QC": {"code": "CA-QC", "name": "Quebec", "consent_type": "all_party", "description": "Quebec Civil Code Art. 36 — stricter than federal", "fine_range": "Civil damages + Quebec Law 25 penalties", "special_notes": "Law 25 (2024) adds stricter privacy requirements"},
    "CA-BC": {"code": "CA-BC", "name": "British Columbia", "consent_type": "one_party", "description": "One party consent, PIPA applies", "fine_range": "Up to $100,000", "special_notes": ""},
    "CA-ON": {"code": "CA-ON", "name": "Ontario", "consent_type": "one_party", "description": "One party consent federally", "fine_range": "Criminal Code penalties", "special_notes": ""},

    # ── EUROPE ──
    "EU-GDPR": {"code": "EU-GDPR", "name": "European Union (GDPR)", "consent_type": "explicit", "description": "GDPR Article 6/7 — explicit consent required. DPIA mandatory for employee recording.", "fine_range": "Up to 4% of annual global turnover or EUR 20M", "special_notes": "Voice data is personal data. Art.9 — biometric data requires explicit consent. Data minimization principle."},
    "EU-DE": {"code": "EU-DE", "name": "Germany (BDSG)", "consent_type": "explicit", "description": "Strictest in EU. BDSG + works council rights.", "fine_range": "GDPR fines + BDSG penalties", "special_notes": "Works councils can veto recording. Employee monitoring heavily restricted."},
    "EU-FR": {"code": "EU-FR", "name": "France (CNIL)", "consent_type": "explicit", "description": "CNIL requires explicit employee consent for recording", "fine_range": "GDPR fines", "special_notes": "CNIL is very active enforcement body"},
    "UK": {"code": "UK", "name": "United Kingdom", "consent_type": "explicit", "description": "UK GDPR — separate from EU but similar requirements", "fine_range": "Up to GBP 17.5M or 4% of turnover", "special_notes": "ICO is the regulatory body"},

    # ── ASIA-PACIFIC ──
    "JP": {"code": "JP", "name": "Japan (APPI)", "consent_type": "explicit", "description": "Act on Protection of Personal Information — consent required for personal data processing", "fine_range": "Up to JPY 100M for corporations", "special_notes": "2022 amendments strengthened individual rights. Cross-border transfer restrictions."},
    "KR": {"code": "KR", "name": "South Korea (PIPA)", "consent_type": "explicit", "description": "Personal Information Protection Act — very strict, consent required", "fine_range": "Up to 3% of total revenue", "special_notes": "AI Framework Act (Jan 2026) adds AI-specific requirements."},
    "IN": {"code": "IN", "name": "India (DPDP)", "consent_type": "explicit", "description": "Digital Personal Data Protection Act 2023", "fine_range": "Up to INR 250 crore (~$30M)", "special_notes": "Broad consent requirements. 22 official languages."},
    "CN": {"code": "CN", "name": "China (PIPL)", "consent_type": "explicit", "description": "Personal Information Protection Law — explicit consent + data localization", "fine_range": "Up to CNY 50M or 5% of revenue", "special_notes": "Data localization required. Cross-border transfer restrictions. Cybersecurity Law also applies."},
    "SG": {"code": "SG", "name": "Singapore (PDPA)", "consent_type": "explicit", "description": "Personal Data Protection Act — consent required", "fine_range": "Up to SGD 1M or 10% of annual turnover", "special_notes": "Smart Nation initiative driving AI adoption."},
    "AU": {"code": "AU", "name": "Australia (Privacy Act)", "consent_type": "one_party", "description": "Privacy Act 1988 — consent varies by state for recording", "fine_range": "Up to AUD 50M", "special_notes": "Notifiable Data Breaches scheme. State-level recording variations."},
    "NZ": {"code": "NZ", "name": "New Zealand", "consent_type": "one_party", "description": "Privacy Act 2020 — one party consent generally", "fine_range": "Up to NZD 10,000", "special_notes": ""},

    # ── MIDDLE EAST ──
    "AE": {"code": "AE", "name": "UAE", "consent_type": "explicit", "description": "Federal Decree-Law 45/2021 — consent required for personal data", "fine_range": "Up to AED 5M", "special_notes": "DIFC and ADGM have separate data protection regimes."},
    "SA": {"code": "SA", "name": "Saudi Arabia (PDPL)", "consent_type": "explicit", "description": "Personal Data Protection Law — consent required", "fine_range": "Up to SAR 5M + imprisonment", "special_notes": "NCA cybersecurity framework also applies."},
    "IL-IS": {"code": "IL-IS", "name": "Israel", "consent_type": "one_party", "description": "Privacy Protection Law 1981 — one party consent", "fine_range": "Criminal and civil penalties", "special_notes": "EU adequacy determination. Strong tech sector."},

    # ── LATIN AMERICA ──
    "BR": {"code": "BR", "name": "Brazil (LGPD)", "consent_type": "explicit", "description": "Lei Geral de Protecao de Dados — explicit consent required", "fine_range": "Up to R$50M or 2% of revenue", "special_notes": "Extraterritorial reach. Opt-in consent model."},
    "MX": {"code": "MX", "name": "Mexico", "consent_type": "explicit", "description": "LFPDPPP — Federal data protection law", "fine_range": "Up to 3x damage caused", "special_notes": "INAI dissolution creates enforcement uncertainty."},
    "CO": {"code": "CO", "name": "Colombia", "consent_type": "explicit", "description": "Law 1581 — prior, express, informed consent required", "fine_range": "Up to 2,000 minimum wages", "special_notes": "Strong enforcement by SIC."},
    "AR": {"code": "AR", "name": "Argentina", "consent_type": "explicit", "description": "Law 25,326 — data protection with EU adequacy", "fine_range": "Administrative sanctions", "special_notes": "EU adequacy determination."},

    # ── AFRICA ──
    "ZA": {"code": "ZA", "name": "South Africa (POPIA)", "consent_type": "explicit", "description": "Protection of Personal Information Act — consent required", "fine_range": "Up to ZAR 10M or imprisonment", "special_notes": "11 official languages. JSE financial sector."},
    "NG": {"code": "NG", "name": "Nigeria (NDPR)", "consent_type": "explicit", "description": "Nigeria Data Protection Regulation", "fine_range": "Up to 2% of annual gross revenue", "special_notes": "Largest African economy. Fintech boom."},
    "KE": {"code": "KE", "name": "Kenya", "consent_type": "explicit", "description": "Data Protection Act 2019", "fine_range": "Up to KES 5M or 1% of annual turnover", "special_notes": "East African tech hub."},
}


# ─────────────────────────────────────────────────────────────────────────────
# COMPLIANCE FRAMEWORKS
# ─────────────────────────────────────────────────────────────────────────────
COMPLIANCE_FRAMEWORKS = {
    "hipaa": {
        "id": "hipaa",
        "name": "HIPAA",
        "description": "Health Insurance Portability and Accountability Act — protects PHI (Protected Health Information)",
        "verticals": ["healthcare", "veterinary"],
        "requirements": [
            "Safeguard PHI from unauthorized access",
            "Implement access controls and audit trails",
            "Business Associate Agreements for cloud vendors",
            "Breach notification within 60 days",
            "Minimum necessary standard for data access",
        ],
        "meetingmind_compliance": "100% on-device processing eliminates PHI transmission. No BAA required — no data leaves the device. Audit trail stored locally.",
        "icon": "\U0001f3e5",
        "color": "#EF4444",
    },
    "attorney_client": {
        "id": "attorney_client",
        "name": "Attorney-Client Privilege",
        "description": "Protects confidential communications between attorneys and clients from disclosure",
        "verticals": ["legal"],
        "requirements": [
            "Communications must remain confidential",
            "No unauthorized third-party access",
            "Cloud storage may waive privilege (Heppner ruling, 2026)",
            "Work product doctrine protection",
        ],
        "meetingmind_compliance": "On-device processing preserves privilege absolutely. No third-party access. Heppner-safe — no cloud AI touching privileged communications.",
        "icon": "\u2696\ufe0f",
        "color": "#3B82F6",
    },
    "ferpa": {
        "id": "ferpa",
        "name": "FERPA",
        "description": "Family Educational Rights and Privacy Act — protects student education records",
        "verticals": ["education"],
        "requirements": [
            "Protect personally identifiable information from education records",
            "Obtain consent before disclosing student records",
            "Maintain records of access to education records",
        ],
        "meetingmind_compliance": "Student data processed and stored entirely on the school's device. No third-party disclosure. FERPA-compliant by architecture.",
        "icon": "\U0001f393",
        "color": "#06B6D4",
    },
    "sec_17a4": {
        "id": "sec_17a4",
        "name": "SEC Rule 17a-4",
        "description": "Securities and Exchange Commission recordkeeping requirements for broker-dealers",
        "verticals": ["financial", "insurance"],
        "requirements": [
            "Retain business communications for 3-6 years",
            "Records must be non-rewritable and non-erasable (WORM)",
            "Must be readily accessible for 2 years",
            "Audit trail for all modifications",
        ],
        "meetingmind_compliance": "On-device storage with audit logging satisfies retention. Local storage can be backed up to WORM-compliant media.",
        "icon": "\U0001f3e6",
        "color": "#10B981",
    },
    "finra_3110": {
        "id": "finra_3110",
        "name": "FINRA Rule 3110",
        "description": "Supervisory requirements for member firms — supervision of registered representatives",
        "verticals": ["financial"],
        "requirements": [
            "Supervise business communications",
            "Review and approve customer communications",
            "Maintain supervisory procedures",
        ],
        "meetingmind_compliance": "Meeting notes provide documented supervision trail. Compliance officer can review on the local system.",
        "icon": "\U0001f4ca",
        "color": "#10B981",
    },
    "bipa": {
        "id": "bipa",
        "name": "Illinois BIPA",
        "description": "Biometric Information Privacy Act — voiceprints are protected biometric identifiers",
        "verticals": ["healthcare", "hr", "sales"],
        "requirements": [
            "Written consent before collecting biometric data",
            "Published data retention and destruction policy",
            "No sale or profit from biometric data",
            "Reasonable security measures",
        ],
        "meetingmind_compliance": "On-device processing means no biometric data (voiceprints) is transmitted, stored in cloud, or shared with third parties. Zero BIPA exposure.",
        "icon": "\U0001f441\ufe0f",
        "color": "#F59E0B",
    },
    "gdpr": {
        "id": "gdpr",
        "name": "GDPR",
        "description": "EU General Data Protection Regulation — comprehensive data protection for EU residents",
        "verticals": ["healthcare", "legal", "financial", "hr", "education", "sales", "government"],
        "requirements": [
            "Lawful basis for processing (consent or legitimate interest)",
            "Data minimization and purpose limitation",
            "Right to erasure (right to be forgotten)",
            "Data Protection Impact Assessment for high-risk processing",
            "Data portability",
            "72-hour breach notification",
        ],
        "meetingmind_compliance": "On-device = data minimization by design. No cross-border data transfers. No third-party processors. Privacy by default.",
        "icon": "\U0001f1ea\U0001f1fa",
        "color": "#6366F1",
    },
    "coppa": {
        "id": "coppa",
        "name": "COPPA",
        "description": "Children's Online Privacy Protection Act — protects data of children under 13",
        "verticals": ["education"],
        "requirements": [
            "Parental consent before collecting children's data",
            "Clear privacy policy",
            "Data minimization for children's information",
            "Reasonable security measures",
        ],
        "meetingmind_compliance": "No children's data collected or transmitted. On-device processing means no third-party access to minors' information.",
        "icon": "\U0001f476",
        "color": "#06B6D4",
    },
    "cjis": {
        "id": "cjis",
        "name": "CJIS Security Policy",
        "description": "Criminal Justice Information Services — security requirements for criminal justice data",
        "verticals": ["government"],
        "requirements": [
            "Access control and authentication",
            "Audit and accountability",
            "Encryption of data at rest and in transit",
            "Personnel security screening",
        ],
        "meetingmind_compliance": "On-device processing keeps criminal justice data isolated. No cloud transmission. Local storage with access controls.",
        "icon": "\U0001f46e",
        "color": "#6366F1",
    },
    "fedramp": {
        "id": "fedramp",
        "name": "FedRAMP",
        "description": "Federal Risk and Authorization Management Program — security assessment for cloud services used by government",
        "verticals": ["government"],
        "requirements": [
            "Security assessment and authorization",
            "Continuous monitoring",
            "NIST SP 800-53 security controls",
            "Independent third-party assessment",
        ],
        "meetingmind_compliance": "Edge-native architecture may qualify for FedRAMP 20x (accelerated path) due to minimal cloud footprint. On-device = reduced attack surface.",
        "icon": "\U0001f3db\ufe0f",
        "color": "#6366F1",
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# AUDIT LOGGER
# ─────────────────────────────────────────────────────────────────────────────
class AuditLogger:
    """Logs compliance events to ~/.meetingmind/audit/ as JSON files."""

    def __init__(self):
        AUDIT_DIR.mkdir(parents=True, exist_ok=True)

    def log(self, event_type, meeting_id=None, details="", jurisdiction=None, vertical=None):
        """Log a compliance event."""
        event = {
            "event_type": event_type,
            "timestamp": datetime.now().isoformat(),
            "meeting_id": meeting_id,
            "details": details,
            "jurisdiction": jurisdiction,
            "vertical": vertical,
        }
        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{event_type}.json"
        filepath = AUDIT_DIR / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(event, f, indent=2)
        return event

    def get_events(self, meeting_id=None, event_type=None, start_date=None, end_date=None):
        """Query audit events with optional filters."""
        events = []
        if not AUDIT_DIR.exists():
            return events

        for filepath in sorted(AUDIT_DIR.glob("*.json"), reverse=True):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    event = json.load(f)

                # Apply filters
                if meeting_id and event.get("meeting_id") != meeting_id:
                    continue
                if event_type and event.get("event_type") != event_type:
                    continue
                if start_date:
                    event_date = event.get("timestamp", "")[:10]
                    if event_date < start_date:
                        continue
                if end_date:
                    event_date = event.get("timestamp", "")[:10]
                    if event_date > end_date:
                        continue

                events.append(event)
            except (json.JSONDecodeError, IOError):
                continue

        return events

    def export(self, meeting_id=None):
        """Export audit events as a list."""
        return self.get_events(meeting_id=meeting_id)


# ─────────────────────────────────────────────────────────────────────────────
# CONSENT MANAGER
# ─────────────────────────────────────────────────────────────────────────────
class ConsentManager:
    """Manages recording consent based on jurisdiction."""

    def __init__(self, jurisdiction_code=None):
        self.jurisdiction_code = jurisdiction_code or detect_jurisdiction()
        self.audit = AuditLogger()

    def get_consent_requirements(self):
        """Return consent requirements for the current jurisdiction."""
        j = JURISDICTIONS.get(self.jurisdiction_code)
        if j:
            return j
        # Default to explicit consent (safest)
        return {
            "code": self.jurisdiction_code or "UNKNOWN",
            "name": "Unknown Jurisdiction",
            "consent_type": "explicit",
            "description": "Jurisdiction not recognized. Defaulting to all-party explicit consent (safest).",
            "fine_range": "Unknown",
            "special_notes": "Please verify recording consent laws for your jurisdiction.",
        }

    def generate_consent_prompt(self, vertical_id=None, participant_names=None):
        """Generate a consent script for the meeting host to read."""
        reqs = self.get_consent_requirements()
        consent_type = reqs.get("consent_type", "explicit")

        # Get vertical-specific language
        vertical_context = ""
        if vertical_id == "healthcare":
            vertical_context = " This recording may contain Protected Health Information (PHI) and will be processed in compliance with HIPAA."
        elif vertical_id == "legal":
            vertical_context = " This recording is protected by attorney-client privilege and will not be transmitted to any third party."
        elif vertical_id == "financial":
            vertical_context = " This recording will be retained in compliance with SEC and FINRA recordkeeping requirements."
        elif vertical_id == "education":
            vertical_context = " This recording may contain student information protected by FERPA."

        participants_text = ""
        if participant_names:
            participants_text = f" Participants: {', '.join(participant_names)}."

        if consent_type in ("all_party", "explicit"):
            return (
                f"This meeting will be recorded and transcribed using MeetingMind. "
                f"All processing occurs on this device — no audio or data will be sent to any cloud service or third party.{vertical_context}{participants_text} "
                f"Under {reqs['name']} law, all participants must consent to this recording. "
                f"Do all participants consent to being recorded?"
            )
        else:
            return (
                f"This meeting will be recorded and transcribed using MeetingMind. "
                f"All processing occurs on this device — no data leaves this machine.{vertical_context}{participants_text} "
                f"At least one participant in the conversation consents to this recording as required by {reqs['name']} law."
            )

    def log_consent(self, meeting_id, participants, consent_type, timestamp=None):
        """Log that consent was obtained."""
        self.audit.log(
            event_type="consent_given",
            meeting_id=meeting_id,
            details=f"Consent type: {consent_type}. Participants: {', '.join(participants) if participants else 'Not specified'}",
            jurisdiction=self.jurisdiction_code,
        )

    def check_compliance(self, vertical_id, jurisdiction_code=None):
        """Return applicable compliance frameworks and their status."""
        jcode = jurisdiction_code or self.jurisdiction_code
        frameworks = get_frameworks_for_vertical(vertical_id)
        return frameworks

    def get_compliance_badges(self, vertical_id):
        """Return compliance badge dicts for display."""
        frameworks = get_frameworks_for_vertical(vertical_id)
        badges = []
        for fw in frameworks:
            badges.append({
                "id": fw["id"],
                "name": fw["name"],
                "icon": fw.get("icon", "\U0001f512"),
                "color": fw.get("color", "#7C3AED"),
                "description": fw.get("meetingmind_compliance", "Compliant via on-device processing"),
            })
        return badges

    def export_audit_log(self, meeting_id=None):
        """Export audit trail as JSON."""
        return self.audit.export(meeting_id=meeting_id)


# ─────────────────────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def detect_jurisdiction():
    """Attempt to detect user's jurisdiction from timezone/locale."""
    try:
        # Try timezone
        tz = time.tzname[0] if time.tzname else ""

        # Common timezone to jurisdiction mapping
        tz_map = {
            "EST": "US-NY", "EDT": "US-NY",
            "CST": "US-TX", "CDT": "US-TX",
            "MST": "US-CO", "MDT": "US-CO",
            "PST": "US-CA", "PDT": "US-CA",
            "GMT": "UK", "BST": "UK",
            "CET": "EU-GDPR", "CEST": "EU-GDPR",
            "JST": "JP",
            "KST": "KR",
            "IST": "IN",
            "CST": "CN",  # China Standard Time (ambiguous with US Central)
            "SGT": "SG",
            "AEST": "AU", "AEDT": "AU",
            "NZST": "NZ", "NZDT": "NZ",
            "BRT": "BR",
        }

        if tz in tz_map:
            return tz_map[tz]

        # Try locale
        loc = locale.getdefaultlocale()
        if loc and loc[0]:
            country = loc[0].split("_")[-1].upper() if "_" in loc[0] else ""
            locale_map = {
                "US": "US-NY",  # Default to one-party state
                "CA": "CA-FED",
                "GB": "UK",
                "DE": "EU-DE",
                "FR": "EU-FR",
                "JP": "JP",
                "KR": "KR",
                "IN": "IN",
                "CN": "CN",
                "SG": "SG",
                "AU": "AU",
                "NZ": "NZ",
                "BR": "BR",
                "ZA": "ZA",
            }
            if country in locale_map:
                return locale_map[country]

    except Exception:
        pass

    return "US-NY"  # Default to one-party consent


def get_frameworks_for_vertical(vertical_id):
    """Return list of applicable compliance framework dicts for a vertical."""
    applicable = []
    for fw in COMPLIANCE_FRAMEWORKS.values():
        if vertical_id in fw.get("verticals", []):
            applicable.append(fw)
    return applicable


def generate_privacy_notice(vertical_id, jurisdiction_code=None):
    """Generate a privacy notice text for the given vertical and jurisdiction."""
    jcode = jurisdiction_code or detect_jurisdiction()
    j = JURISDICTIONS.get(jcode, {})
    frameworks = get_frameworks_for_vertical(vertical_id)

    fw_names = ", ".join(fw["name"] for fw in frameworks) if frameworks else "general data protection"

    return (
        f"PRIVACY NOTICE\n\n"
        f"MeetingMind processes all audio, transcription, and AI analysis entirely on this device. "
        f"No data is transmitted to any cloud service, third-party processor, or external server.\n\n"
        f"Jurisdiction: {j.get('name', jcode)}\n"
        f"Consent Type: {j.get('consent_type', 'explicit').replace('_', ' ').title()}\n"
        f"Applicable Frameworks: {fw_names}\n\n"
        f"Data Storage: All meeting data is stored locally at ~/.meetingmind/ on this device.\n"
        f"Data Retention: {get_data_retention_policy(vertical_id).get('period', 'As configured by user')}.\n"
        f"Data Deletion: Users can delete any meeting record at any time.\n\n"
        f"For questions about data handling, contact your organization's data protection officer."
    )


def get_data_retention_policy(vertical_id):
    """Return recommended retention period and policy text for a vertical."""
    policies = {
        "healthcare": {"period": "7 years (HIPAA minimum for medical records)", "policy": "Retain clinical documentation for a minimum of 7 years per HIPAA. Some states require longer retention."},
        "legal": {"period": "6-10 years (varies by matter type)", "policy": "Retain client files per state bar requirements. Typically 6 years after matter closes. Litigation hold may extend."},
        "financial": {"period": "6 years (SEC Rule 17a-4)", "policy": "Retain business communications for 6 years. First 2 years must be readily accessible."},
        "education": {"period": "5 years after student graduates or transfers", "policy": "Retain FERPA-protected records per institutional policy."},
        "government": {"period": "Per records retention schedule", "policy": "Follow applicable government records retention schedule. FOIA-responsive records may have specific requirements."},
        "hr": {"period": "3-7 years after employment ends", "policy": "Retain employment records per federal and state requirements. EEOC requires 1 year minimum."},
        "construction": {"period": "10 years (statute of repose)", "policy": "Retain construction records for the duration of the statute of repose, typically 10 years."},
        "insurance": {"period": "6 years", "policy": "Retain claims and policy records per state insurance department requirements."},
    }
    return policies.get(vertical_id, {"period": "As configured by user", "policy": "Retain meeting records per your organization's data retention policy."})
