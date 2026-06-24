# Methodology · ABM Automation Pipeline

How the three workflows actually decide what is a fit account, who the right contact is, and how the data lands in CRM. This is the same methodology used in production at [Growisto](https://growisto.com), with internal client names and competitor names redacted.

## Data sources

| Source | How it is used |
|---|---|
| **Apollo.io** | Company enrichment (employee count, industry, location, LinkedIn URL), people search by title and seniority, people enrichment to get phone and email from LinkedIn URL |
| **Web Search via Claude tools** | Tech stack verification, Amazon listing verification, revenue and funding data, in-house dev headcount via LinkedIn searches |
| **Zoho CRM** | Dedup gate on existing Target Accounts; push destination for approved accounts and POCs |
| **Zoho Cliq** | #abm-leads channel as real-time input stream for Workflow 3 |
| **Manual input CSV** | Sales provides raw list of brand domains as starting point for Workflow 1 |
| **Ahrefs** | Traffic data, currently manual (Ahrefs MCP not yet connected) |

## Workflow 1 · ICP Scoring step by step

1. Sales provides a CSV with columns: `domain, country, city, state, employee_count, tech_stack, in_house_dev, traffic_ahrefs_k, ecommerce, sells_on_amazon, sold_by, amazon_ratings, amazon_product_count, linkedin_url`
2. For each account, the script reads ICP criteria from `config/icp_criteria.json` and walks top-down (Cat 1 → Cat 4 for India, Cat 1 → Cat 5 for USA)
3. An account qualifies for the highest category whose criteria it meets across all of: ecommerce flag, tech stack in approved list, employee count above threshold, traffic above threshold, location in allowed set, in-house dev flag (Cat 1/2 only), Amazon presence (USA Cat 1-4)
4. Service potential scores are computed separately:
   - **SEO Potential** · Site search volume above 2,000 = High
   - **Tech Potential** · Qualifying tech stack (Shopify / Magento / Custom) + traffic check; no in-house dev = stronger
   - **Amazon Potential** · sold_by = Brand or Amazon-direct + ratings above 100 + product count criteria
5. Output is a structured table (CSV / Excel) for human approval
6. On approval, accounts are pushed to Zoho CRM Target_Accounts with dedup on `Name` field (which equals domain)

### ICP Scoring Thresholds, India

| Category | Min Traffic (Ahrefs K) | Min Employees | Tech Stack | Location |
|---|---|---|---|---|
| Cat 1 | 43K | 200 | Magento, Node, React (approved only) | Metro India |
| Cat 2 | 32K | 100 | Shopify, Magento, Node, React (approved) | All India |
| Cat 3 | 22K | 100 | Shopify, Magento, Node, React | All India |
| Cat 4 | 20K | 50 | Shopify, Magento, WooCommerce, Node, React | All India |

### ICP Scoring Thresholds, USA

| Category | Min Traffic (Ahrefs K) | Min Employees | Amazon |
|---|---|---|---|
| Cat 1 | 43K | 100 | Mandatory, Brand or 1P only, top metros |
| Cat 2 | 43K | 50 | Mandatory, Brand or 1P only, top metros |
| Cat 3 | 11K | 20 | Mandatory, Brand or 1P only, top metros |
| Cat 4 | 11K | 20 | Mandatory, Brand or 1P only, any USA |
| Cat 5 | 11K | 20 | Optional |

## Workflow 2 · POC Extraction step by step

1. Pull approved Target Accounts from Zoho CRM
2. For each account, call Apollo's people search with:
   - `organization_domains`: [domain]
   - `titles`: priority-ordered list from `config/poc_search_titles.json`
   - `seniority_levels`: ["c_suite", "vp", "director"]
   - `contact_email_status`: ["verified", "likely to engage"]
3. For each returned person, compute title priority score from the ladder (lower = better)
4. Select top 1-2 POCs per account; fallback to CEO/Founder if no marketing titles found
5. Apply location filter (default India-only POCs for the #abm-leads channel)
6. Output POC table for human approval
7. On approval, push to Zoho CRM Leads with `Target_Account_Name` lookup linking the POC to their account

### Title Priority Ladder

1. CMO / Chief Marketing Officer
2. VP Marketing
3. VP Growth / VP Ecommerce
4. Head of Marketing
5. Head of Growth / Head of Ecommerce / Head of Digital
6. Marketing Director / Director of Marketing
7. Director of Ecommerce / Director of Growth
8. General Manager
9. CEO / Founder / Co-Founder
10. COO / President
11. CTO (fallback)

## Workflow 3 · Cliq Bot step by step

1. Cron polls the Cliq channel monitor every 5 minutes during business hours (or a manual trigger fires it)
2. Monitor fetches new messages since the last poll timestamp, stored in `output/wf3_last_poll.json`
3. Each message is parsed for:
   - LinkedIn company URL → extract slug → Apollo company lookup
   - LinkedIn profile URL → Apollo people enrich → phone and email
   - Domain (xyz.com) → Apollo org enrichment + people search
   - Plain company name → Apollo company search
4. For LinkedIn profile URLs: call `apollo_people_match` with the URL to get verified phone and email
5. For company inputs: call `apollo_mixed_people_api_search` with the domain plus the title priority list
6. Results are staged to `output/wf3_pocs_YYYY-MM-DD.json`
7. Bot replies in the originating Cliq message with a formatted contact card
8. At 6 PM IST daily, all staged POCs are pushed to Zoho CRM Leads in one batch

### Parsing logic

- `LINKEDIN_PROFILE_RE` matches `linkedin.com/in/<slug>`
- `LINKEDIN_COMPANY_RE` matches `linkedin.com/company/<slug>`
- `DOMAIN_RE` matches a generic domain pattern; common social and tool domains are skip-listed (linkedin.com, twitter.com, github.com, etc.)
- Plain company name fallback if no URL or domain is detected

## Zoho CRM fields used

### Target_Accounts module

| Field | Type | Source / logic |
|---|---|---|
| Name | Text (dedup key) | domain (e.g. examplebrand.com) |
| Website_URL | URL | domain |
| Country | Picklist | India / United States |
| City, State | Text | from Apollo or manual |
| eCommerce | Picklist | Yes / No |
| Tech_Stack | Multiselect | from Apollo / BuiltWith verification |
| In_House_Developers | Picklist | None / Internal / Agency / Maybe |
| Employee_Count | Integer | from Apollo |
| Website_Traffic_Ahrefs | Integer (K) | from Ahrefs (currently manual) |
| Site_Search | Integer | site search volume estimate |
| ABM_Category | Integer (1-5) | computed by ICP scoring |
| SEO_Potential | Picklist | High / Medium / Low |
| Tech_Potential | Picklist | High / Medium / Low |
| Amazon_Potential | Picklist | High / Medium / Low / No |
| Sells_on_Amazon | Picklist | Yes / No |
| Sold_by | Picklist | Brand / Amazon / Third Party |
| Ratings | Picklist | Yes / No (100+ ratings threshold) |
| No_of_products_in_Amazon | Picklist | 0-10 / 10-20 / 20+ |
| Linkedin_URL | URL | from Apollo |
| Company_Type | Picklist | ABM India / ABM USA |
| Account_Status | Picklist | "Cold" (default on create) |
| B2C | Picklist | Yes (default for ecom accounts) |

### Leads module (linked to Target_Accounts)

| Field | Source |
|---|---|
| First_Name, Last_Name | from Apollo person |
| Title | job title from Apollo |
| Email | from Apollo (verified preferred) |
| Phone | mobile from Apollo |
| LinkedIn_URL | from Apollo |
| Target_Account_Name | lookup to Target_Accounts.Name |
| Lead_Owner | configurable per workflow (currently single default for testing) |
| Lead_Status | "Not Contacted" (default) |

## Manual judgment calls

These are decisions a human still makes, not the system:

- **Tech stack approval** for India Cat 1 and Cat 2 requires a human sign-off on whether the brand's stack is genuinely complex enough to warrant agency services
- **Revenue classification** when Apollo or Tracxn data is missing or ambiguous; the system marks "estimated" rather than guessing
- **Amazon Sold-by verification** for borderline accounts requires opening the storefront to confirm direct vs third-party
- **ABM_Category** is held as "Cannot Assign" when traffic data is unavailable, rather than guessing; this was a deliberate choice to avoid polluting the CRM with incorrect tiers
- **Cliq Bot escalations** for messages the parser cannot classify go to a manual queue, not a confident wrong answer
