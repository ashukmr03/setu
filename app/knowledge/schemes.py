"""
Official scheme records — sourced only from verified Indian government portals.
Each record is manually verified or scraped from the official URL listed.
The LLM is strictly forbidden from using information outside these records.
"""

SCHEMES: list[dict] = [
    {
        "scheme_name": "PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)",
        "category": "Agriculture / Farmer Welfare",
        "state_or_national": "National",
        "eligibility": (
            "Small and marginal farmers with cultivable land up to 2 hectares. "
            "Excludes institutional land holders, farmer families holding constitutional posts, "
            "serving/retired government employees (except Group D/Multi-Tasking Staff), "
            "taxpayers, professionals (doctors, engineers, lawyers, CAs, architects)."
        ),
        "benefits": (
            "Financial benefit of Rs 6,000 per year paid in three equal instalments of Rs 2,000 "
            "directly to the bank account of the farmer family."
        ),
        "required_documents": [
            "Aadhaar card",
            "Land ownership records (Khatauni/ROR)",
            "Bank account passbook (linked to Aadhaar)",
            "Mobile number",
        ],
        "application_steps": [
            "1. Visit the official PM-KISAN portal: https://pmkisan.gov.in",
            "2. Click 'New Farmer Registration' on the homepage.",
            "3. Enter Aadhaar number and mobile number.",
            "4. Fill in personal and land details.",
            "5. Upload required documents.",
            "6. Submit and note the registration number.",
            "7. Alternatively, visit your local Common Service Centre (CSC) or Patwari/Lekhpal office.",
        ],
        "responsible_department": "Ministry of Agriculture & Farmers Welfare, Government of India",
        "official_application_url": "https://pmkisan.gov.in/NewFarmerRegistration.aspx",
        "source_url": "https://pmkisan.gov.in",
        "source_page_title": "PM-KISAN Official Portal",
        "last_verified_date": "2024-10-01",
        "verified_by": "setu-scraper-v1",
    },
    {
        "scheme_name": "Ayushman Bharat - Pradhan Mantri Jan Arogya Yojana (AB-PMJAY)",
        "category": "Health Insurance",
        "state_or_national": "National",
        "eligibility": (
            "Families listed in the Socio-Economic Caste Census (SECC) 2011 database. "
            "Covers deprived rural families and occupational categories of urban workers. "
            "No restriction on family size or age. "
            "Check eligibility at the official portal using Aadhaar or ration card number."
        ),
        "benefits": (
            "Health cover of Rs 5 lakh per family per year for secondary and tertiary hospitalisation "
            "at empanelled public and private hospitals across India. Cashless and paperless treatment."
        ),
        "required_documents": [
            "Aadhaar card (any family member)",
            "Ration card",
            "Mobile number registered with Aadhaar",
        ],
        "application_steps": [
            "1. Check eligibility at https://mera.pmjay.gov.in using mobile number.",
            "2. If eligible, visit nearest Ayushman Mitra at empanelled hospital or CSC.",
            "3. Verify identity with Aadhaar-based e-KYC.",
            "4. Receive Ayushman card (Golden Card).",
            "5. Use card for cashless treatment at any empanelled hospital.",
        ],
        "responsible_department": "National Health Authority (NHA), Ministry of Health & Family Welfare",
        "official_application_url": "https://mera.pmjay.gov.in",
        "source_url": "https://pmjay.gov.in",
        "source_page_title": "Ayushman Bharat PM-JAY Official Website",
        "last_verified_date": "2024-10-01",
        "verified_by": "setu-scraper-v1",
    },
    {
        "scheme_name": "National Scholarship Portal - Central Sector Scheme of Scholarships (CSSS)",
        "category": "Education / Scholarship",
        "state_or_national": "National",
        "eligibility": (
            "Students who passed Class 12 from a recognized board with more than 80 percentile marks. "
            "Parental income must not exceed Rs 4.5 lakh per annum. "
            "Enrolled in a regular degree course (not distance education) at a college/university. "
            "Not receiving any other scholarship."
        ),
        "benefits": (
            "Rs 12,000 per annum for undergraduate students. "
            "Rs 20,000 per annum for postgraduate students. "
            "Direct bank transfer."
        ),
        "required_documents": [
            "Class 12 marksheet",
            "Income certificate (issued by competent authority)",
            "Bank account details (student's own account)",
            "Aadhaar card",
            "Institution verification",
            "Caste certificate (if applicable)",
        ],
        "application_steps": [
            "1. Register at https://scholarships.gov.in (National Scholarship Portal).",
            "2. Login with your credentials.",
            "3. Select 'Central Sector Scheme of Scholarships' under Ministry of Education.",
            "4. Fill application form with academic and personal details.",
            "5. Upload required documents.",
            "6. Submit and get institution verification done.",
            "7. Track status on the portal.",
        ],
        "responsible_department": "Ministry of Education, Department of Higher Education",
        "official_application_url": "https://scholarships.gov.in",
        "source_url": "https://scholarships.gov.in/fresh/schemeDetails.action?schemeId=61",
        "source_page_title": "National Scholarship Portal - CSSS",
        "last_verified_date": "2024-10-01",
        "verified_by": "setu-scraper-v1",
    },
    {
        "scheme_name": "PM Awas Yojana - Gramin (PMAY-G)",
        "category": "Housing",
        "state_or_national": "National",
        "eligibility": (
            "Homeless families or families living in zero, one, or two room houses with kutcha walls/roof. "
            "Listed in SECC 2011 data. "
            "Excludes families with any member owning a motorised vehicle, refrigerator, Rs 50,000 in Kisan Credit Card, "
            "or earning more than Rs 15,000/month. "
            "Priority to SC/ST, minorities, freed bonded labourers, widows, ex-servicemen."
        ),
        "benefits": (
            "Rs 1.20 lakh in plain areas and Rs 1.30 lakh in hilly/difficult areas for construction of a pucca house. "
            "Additional Rs 12,000 for toilet construction under Swachh Bharat Mission. "
            "90 days unskilled labour wages under MGNREGS."
        ),
        "required_documents": [
            "Aadhaar card",
            "Bank account passbook",
            "SECC 2011 data inclusion proof",
            "BPL card (if applicable)",
            "Job card under MGNREGS",
        ],
        "application_steps": [
            "1. Check your name in the SECC 2011 Awaiting List at https://pmayg.nic.in.",
            "2. Contact your Gram Panchayat or Block Development Officer.",
            "3. Submit Aadhaar and bank account details for geo-tagging and verification.",
            "4. Construction is monitored via the AwaasSoft system.",
            "5. Funds are transferred directly to bank account in instalments.",
        ],
        "responsible_department": "Ministry of Rural Development, Government of India",
        "official_application_url": "https://pmayg.nic.in",
        "source_url": "https://pmayg.nic.in",
        "source_page_title": "Pradhan Mantri Awaas Yojana Gramin",
        "last_verified_date": "2024-10-01",
        "verified_by": "setu-scraper-v1",
    },
    {
        "scheme_name": "Sukanya Samriddhi Yojana (SSY)",
        "category": "Girl Child / Savings",
        "state_or_national": "National",
        "eligibility": (
            "Account can be opened for a girl child below 10 years of age. "
            "Only two accounts per family (one per girl child, maximum two girls). "
            "Parent or legal guardian opens the account."
        ),
        "benefits": (
            "High interest rate (currently 8.2% per annum, revised quarterly by Government). "
            "Tax exemption under Section 80C. "
            "Partial withdrawal of 50% after girl turns 18 for education. "
            "Full maturity after 21 years from account opening."
        ),
        "required_documents": [
            "Girl child's birth certificate",
            "Parent/guardian's identity proof (Aadhaar, PAN)",
            "Parent/guardian's address proof",
            "Photograph of girl child and guardian",
        ],
        "application_steps": [
            "1. Visit any post office or authorised bank branch (SBI, PNB, Bank of Baroda, etc.).",
            "2. Collect and fill Form-1 (SSY Account Opening Form).",
            "3. Submit form with required documents and initial deposit (minimum Rs 250).",
            "4. Receive passbook for the account.",
        ],
        "responsible_department": "Ministry of Finance / Department of Posts",
        "official_application_url": "https://www.indiapost.gov.in/Financial/Pages/Content/Sukanya-Samridhi-Account.aspx",
        "source_url": "https://www.myscheme.gov.in/schemes/ssy",
        "source_page_title": "Sukanya Samriddhi Yojana - MyScheme",
        "last_verified_date": "2024-10-01",
        "verified_by": "setu-scraper-v1",
    },
    {
        "scheme_name": "Pradhan Mantri Mudra Yojana (PMMY)",
        "category": "Entrepreneurship / Business Loan",
        "state_or_national": "National",
        "eligibility": (
            "Any Indian citizen who has a business plan for a non-farm income-generating activity "
            "in manufacturing, trading, or services sector with credit need below Rs 10 lakh. "
            "Three categories: Shishu (up to Rs 50,000), Kishore (Rs 50,001 to Rs 5 lakh), "
            "Tarun (Rs 5,00,001 to Rs 10 lakh)."
        ),
        "benefits": (
            "Collateral-free loans up to Rs 10 lakh for small businesses. "
            "Loan through banks, MFIs, NBFCs. "
            "MUDRA card issued for working capital needs."
        ),
        "required_documents": [
            "Identity proof (Aadhaar / Voter ID / Passport)",
            "Address proof",
            "Business plan or project report",
            "Quotation for machinery/equipment (if applicable)",
            "Proof of business existence or registration",
            "Last 6 months bank statement",
            "Caste certificate (if applicable for priority)",
        ],
        "application_steps": [
            "1. Visit any scheduled commercial bank, RRB, MFI, or NBFC.",
            "2. Alternatively apply online at https://www.mudra.org.in.",
            "3. Submit loan application with business plan and documents.",
            "4. Bank evaluates and sanctions the loan.",
            "5. Loan amount disbursed directly to business account.",
        ],
        "responsible_department": "MUDRA (Micro Units Development & Refinance Agency Ltd) / Ministry of Finance",
        "official_application_url": "https://www.mudra.org.in",
        "source_url": "https://www.myscheme.gov.in/schemes/pmmy",
        "source_page_title": "Pradhan Mantri Mudra Yojana - MyScheme",
        "last_verified_date": "2024-10-01",
        "verified_by": "setu-scraper-v1",
    },
    {
        "scheme_name": "Karnataka Rajiv Gandhi Housing Corporation - Ashraya Scheme",
        "category": "Housing",
        "state_or_national": "Karnataka",
        "eligibility": (
            "Below Poverty Line (BPL) families in Karnataka. "
            "Should not own a pucca house. "
            "Family income should not exceed Rs 32,000 per year in rural areas. "
            "Priority to SC/ST, disabled persons, widows, and women-headed households."
        ),
        "benefits": (
            "Financial assistance of Rs 1.20 lakh to Rs 1.50 lakh for construction of a two-room house. "
            "State government top-up over central PMAY-G grant."
        ),
        "required_documents": [
            "BPL certificate",
            "Aadhaar card",
            "Land ownership document (Patta/RTC)",
            "Caste certificate (SC/ST)",
            "Income certificate",
            "Bank passbook",
            "Ration card",
        ],
        "application_steps": [
            "1. Visit your local Gram Panchayat office.",
            "2. Contact the Block Development Officer or KRHCL district office.",
            "3. Submit application with required documents.",
            "4. Verification by local authorities.",
            "5. If approved, funds transferred in instalments.",
            "6. More info: https://ashraya.karnataka.gov.in",
        ],
        "responsible_department": "Karnataka Rajiv Gandhi Housing Corporation Ltd (KRHCL)",
        "official_application_url": "https://ashraya.karnataka.gov.in",
        "source_url": "https://ashraya.karnataka.gov.in",
        "source_page_title": "Ashraya Scheme - KRHCL Karnataka",
        "last_verified_date": "2024-10-01",
        "verified_by": "setu-scraper-v1",
    },
    {
        "scheme_name": "Karnataka Vidya Siri Scholarship",
        "category": "Education / Scholarship",
        "state_or_national": "Karnataka",
        "eligibility": (
            "SC/ST students studying in Government Pre-University Colleges in Karnataka. "
            "Must have passed SSLC (Class 10). "
            "Annual family income must not exceed Rs 2.5 lakh."
        ),
        "benefits": (
            "Scholarship covering tuition fees and maintenance allowance. "
            "Amount varies based on course and category."
        ),
        "required_documents": [
            "SSLC (Class 10) marksheet",
            "Caste certificate (SC/ST)",
            "Income certificate",
            "Aadhaar card",
            "Bank account details",
            "College admission proof",
        ],
        "application_steps": [
            "1. Apply through Karnataka Scholarship Portal: https://scholarships.karnataka.gov.in",
            "2. Register with Aadhaar number and mobile number.",
            "3. Fill in academic and personal details.",
            "4. Upload required documents.",
            "5. Submit for institution verification.",
        ],
        "responsible_department": "Department of Social Welfare, Government of Karnataka",
        "official_application_url": "https://scholarships.karnataka.gov.in",
        "source_url": "https://scholarships.karnataka.gov.in",
        "source_page_title": "Karnataka Scholarship Portal",
        "last_verified_date": "2024-10-01",
        "verified_by": "setu-scraper-v1",
    },
    {
        "scheme_name": "Mahatma Gandhi National Rural Employment Guarantee Scheme (MGNREGS)",
        "category": "Employment / Rural Livelihood",
        "state_or_national": "National",
        "eligibility": (
            "Any adult member (18 years or above) of a rural household willing to do unskilled manual work. "
            "Must be a resident of the Gram Panchayat area where applying."
        ),
        "benefits": (
            "Guaranteed 100 days of wage employment per household per year. "
            "Wage rate as notified by state government (varies by state). "
            "Work must be provided within 15 days of application; otherwise unemployment allowance is paid. "
            "Work within 5 km of residence."
        ),
        "required_documents": [
            "Photo identity proof",
            "Aadhaar card",
            "Bank account passbook",
            "Ration card",
        ],
        "application_steps": [
            "1. Submit a written application to your Gram Panchayat requesting a Job Card.",
            "2. Gram Panchayat issues a Job Card within 15 days.",
            "3. Submit work demand application to Gram Panchayat.",
            "4. Work will be allotted within 15 days.",
            "5. Track work and wages at https://nregastrep.nic.in.",
        ],
        "responsible_department": "Ministry of Rural Development, Government of India",
        "official_application_url": "https://nrega.nic.in",
        "source_url": "https://nrega.nic.in",
        "source_page_title": "MGNREGA Official Portal",
        "last_verified_date": "2024-10-01",
        "verified_by": "setu-scraper-v1",
    },
    {
        "scheme_name": "PM Vishwakarma Yojana",
        "category": "Artisan / Skilled Workers",
        "state_or_national": "National",
        "eligibility": (
            "Artisans and craftspeople working with hands and tools in one of 18 traditional trades "
            "(carpenter, boat maker, armourer, blacksmith, hammer & tool kit maker, locksmith, goldsmith, "
            "potter, sculptor, cobbler/shoesmith, mason, basket/mat/broom weaver, doll & toy maker, "
            "barber, garland maker, washerman, tailor, fishing net maker). "
            "Age 18 years or above. "
            "Not enrolled in PMEGP, PM SVANidhi, or Mudra in the last 5 years."
        ),
        "benefits": (
            "Recognition as Vishwakarma with certificate and ID card. "
            "Skill training (basic 5-7 days + advanced 15 days) with stipend of Rs 500/day. "
            "Toolkit incentive of Rs 15,000. "
            "Collateral-free credit support: Rs 1 lakh (first tranche), Rs 2 lakh (second tranche) at 5% interest. "
            "Digital transaction incentives and marketing support."
        ),
        "required_documents": [
            "Aadhaar card",
            "Mobile number linked to Aadhaar",
            "Bank account details",
            "Proof of trade/craft (self-declaration or certificate)",
            "Ration card or family details",
        ],
        "application_steps": [
            "1. Visit nearest Common Service Centre (CSC) or Gram Panchayat.",
            "2. Register at https://pmvishwakarma.gov.in with Aadhaar-based biometric verification.",
            "3. Select your trade/craft from the 18 listed trades.",
            "4. Complete registration and receive PM Vishwakarma certificate.",
            "5. Enroll in skill training through the portal.",
        ],
        "responsible_department": "Ministry of Micro, Small & Medium Enterprises (MSME), Government of India",
        "official_application_url": "https://pmvishwakarma.gov.in",
        "source_url": "https://pmvishwakarma.gov.in",
        "source_page_title": "PM Vishwakarma Official Portal",
        "last_verified_date": "2024-10-01",
        "verified_by": "setu-scraper-v1",
    },
]
