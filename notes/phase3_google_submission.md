# Phase 3: Google Transit Submission Guide

## The Hard Truth

**Google does NOT accept community/user-generated GTFS submissions.**

From Google's official form:
> "We currently do not accept user generated contents"

Only **authorized representatives of transit agencies** can submit feeds.

---

## Your Options

### Option A: Get ONCF to Submit (Ideal)

**Why it's best:**
- Official feed = maintained long-term
- Real-time data possible
- Google prioritizes official sources

**How to approach ONCF:**

1. **Find the right contact:**
   - ONCF Digital/IT department
   - Marketing/Communications (tourism angle)
   - Email: contact@oncf.ma or through LinkedIn

2. **Pitch framing (avoid "Google Maps doesn't work"):**
   ```
   Subject: GTFS Transit Data - International Accessibility Standard
   
   ONCF has excellent rail service, but international visitors cannot 
   find train schedules in Google Maps, Apple Maps, or accessibility 
   tools used by visually impaired travelers.
   
   GTFS is a simple, static data format (just CSV files) that publishes 
   the same schedule information already visible on station boards. 
   No operational secrets. No real-time tracking required.
   
   I have prepared a draft GTFS feed covering Al Boraq and Al Atlas 
   services that could serve as a starting point.
   
   Benefits:
   - Tourism: 14M+ visitors/year can plan rail trips
   - Accessibility: Blind navigation tools require GTFS
   - Climate: Promotes rail over car/taxi
   - Zero cost: Static file hosting only
   ```

3. **Offer to help:**
   - Provide the GTFS we built as a starting template
   - Offer to validate and maintain initially
   - Make it easy for them to say yes

---

### Option B: Mobility Database (Immediate Visibility)

**What:** [Mobility Database](https://database.mobilitydata.org/) is a public GTFS aggregator

**Benefits:**
- No official agency approval needed for listing
- Apps like Citymapper, Transit, Moovit check this database
- Creates public pressure/visibility
- Google sometimes discovers feeds here

**How to submit:**
1. Host GTFS zip file publicly (GitHub releases, S3, etc.)
2. Submit to: https://database.mobilitydata.org/add-a-feed
3. Feed becomes discoverable by all transit apps

**Limitation:** Google may not ingest without official agency confirmation

---

### Option C: Transit App Direct Integration

**Skip Google, go direct to:**

| App | How to Submit | Notes |
|-----|---------------|-------|
| **Citymapper** | citymapper.com/contact | Often adds community feeds |
| **Moovit** | moovitapp.com/partners | Large user base |
| **Transit App** | transitapp.com/partners | Popular in North America/Europe |
| **Apple Maps** | maps.apple.com/transit | Uses OSM + accepts GTFS |
| **Rome2Rio** | rome2rio.com | Already has some Morocco data |

These apps are often more receptive to community feeds than Google.

---

### Option D: OpenTripPlanner (Self-Hosted)

**What:** Open-source trip planner you can host yourself

**How:**
1. Deploy OpenTripPlanner with Morocco GTFS + OSM data
2. Create a simple web interface
3. Publish as "Morocco Rail Planner"
4. Build user base → pressure on ONCF

**Pros:** Full control, immediate results
**Cons:** Requires hosting, won't appear in Google Maps

---

## Recommended Strategy

### Parallel approach:

1. **Immediate (this week):**
   - [ ] Validate GTFS with MobilityData validator
   - [ ] Host GTFS on GitHub releases
   - [ ] Submit to Mobility Database
   - [ ] Submit to Citymapper/Transit App

2. **Short-term (this month):**
   - [ ] Draft email to ONCF (use framing above)
   - [ ] Find ONCF contacts on LinkedIn
   - [ ] Send pitch with GTFS attached

3. **Medium-term (if ONCF ignores):**
   - [ ] Deploy OpenTripPlanner instance
   - [ ] Create simple "Morocco Rail" web app
   - [ ] Share on Reddit/Twitter for visibility
   - [ ] Contact travel bloggers who write about Morocco

---

## Google Transit Partner Portal Details

**URL:** https://support.google.com/transitpartners/contact/agency_participate

**Required fields:**
- Organization must be official transit agency
- Contact with signing authority
- GTFS feed URL (fetch) or file (manual)
- Service details (rail type, country, cities)

**What they check:**
- Fixed routes and schedules ✓ (ONCF qualifies)
- Publicly accessible service ✓
- GTFS format ✓
- Authorized representative ✗ (this is the blocker)

---

## Key Contacts to Research

- **ONCF Official:** contact@oncf.ma
- **Morocco Ministry of Transport:** Equipment and Transport Ministry
- **Google Transit:** transit-partners@google.com (for questions)
- **MobilityData:** info@mobilitydata.org (GTFS standards body)

---

## Files Ready for Submission

```
rail_maroc/gtfs/
├── agency.txt      ✓
├── stops.txt       ✓ (33 stations)
├── routes.txt      ✓ (9 routes)
├── trips.txt       ✓ (60 trips)
├── stop_times.txt  ✓ (240 entries)
├── calendar.txt    ✓
└── feed_info.txt   ✓
```

Next step: Zip these files and validate.
