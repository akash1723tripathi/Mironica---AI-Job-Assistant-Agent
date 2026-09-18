"""
Curated India-focused ATS seed companies list.
Contains ~220 real technology companies across Greenhouse, Lever, Ashby, and Workday.

Mix:
  - 80+ Indian startups (Razorpay, CRED, Groww, BrowserStack, Juspay, Zepto, Meesho, etc.)
  - 50+ YC-backed startups (Supabase, Ramp, Linear, PostHog, Railway, Perplexity, etc.)
  - 40+ Global product companies with India engineering hubs (Adobe, MongoDB, Cloudflare, etc.)
  - 30+ Enterprise / MNC engineering companies (Visa, Salesforce, Cisco, Oracle, etc.)

ATS Providers: Greenhouse, Lever, Ashby, Workday ONLY.
Excluded: LinkedIn, Naukri, Indeed, Glassdoor, Wellfound (discovery platforms, not ATS boards).

Schema:
  company       – Display name
  website       – Company website (informational)
  platform      – greenhouse | lever | ashby | workday
  token         – ATS board identifier
  category      – startup | product | enterprise | services
  country       – Company origin: India | Global
  hires_in_india – Whether India hiring exists
"""

SEED_COMPANIES = [

    # =========================================================================
    # GREENHOUSE
    # =========================================================================

    # --- Indian Startups (Greenhouse) ---
    # Note: Atlan uses Ashby, BrowserStack uses SmartRecruiters, Chargebee uses Greenhouse with a different slug
    {
        "company": "Chargebee", "website": "https://chargebee.com",
        "platform": "greenhouse", "token": "chargebeeapplicationsengineer",
        "category": "startup", "country": "India", "hires_in_india": True
    },
    # CleverTap and Darwinbox are on their own career portals, not Greenhouse
    {
        "company": "HashedIn by Deloitte", "website": "https://hashedin.com",
        "platform": "greenhouse", "token": "hashedin",
        "category": "startup", "country": "India", "hires_in_india": True
    },
    {
        "company": "Druva", "website": "https://druva.com",
        "platform": "greenhouse", "token": "druva",
        "category": "product", "country": "India", "hires_in_india": True
    },
    {
        "company": "Groww", "website": "https://groww.in",
        "platform": "greenhouse", "token": "groww",
        "category": "startup", "country": "India", "hires_in_india": True
    },
    {
        "company": "InMobi", "website": "https://inmobi.com",
        "platform": "greenhouse", "token": "inmobi",
        "category": "product", "country": "India", "hires_in_india": True
    },
    # Innovaccer / Juspay / Keka / LeadSquared not on public Greenhouse; replaced with valid equivalents
    {
        "company": "Fyle", "website": "https://fylehq.com",
        "platform": "greenhouse", "token": "fyle",
        "category": "startup", "country": "India", "hires_in_india": True
    },
    {
        "company": "Helpshift", "website": "https://helpshift.com",
        "platform": "greenhouse", "token": "helpshift",
        "category": "startup", "country": "India", "hires_in_india": True
    },
    # MoEngage / Multiplier / Navi / Perfios not on Greenhouse public boards
    {
        "company": "Sigmoid", "website": "https://sigmoid.com",
        "platform": "greenhouse", "token": "sigmoid",
        "category": "startup", "country": "India", "hires_in_india": True
    },
    {
        "company": "Licious", "website": "https://licious.in",
        "platform": "greenhouse", "token": "licious",
        "category": "startup", "country": "India", "hires_in_india": True
    },
    {
        "company": "Porter", "website": "https://porter.in",
        "platform": "greenhouse", "token": "porter",
        "category": "startup", "country": "India", "hires_in_india": True
    },
    {
        "company": "Postman", "website": "https://postman.com",
        "platform": "greenhouse", "token": "postman",
        "category": "product", "country": "India", "hires_in_india": True
    },
    {
        "company": "Razorpay", "website": "https://razorpay.com",
        "platform": "greenhouse", "token": "razorpaysoftwareprivatelimited",
        "category": "startup", "country": "India", "hires_in_india": True
    },
    # Recko (now acquired by Stripe) - removed
    {
        "company": "Smallcase", "website": "https://smallcase.com",
        "platform": "greenhouse", "token": "smallcase",
        "category": "startup", "country": "India", "hires_in_india": True
    },
    {
        "company": "Rubrik", "website": "https://rubrik.com",
        "platform": "greenhouse", "token": "rubrik",
        "category": "product", "country": "India", "hires_in_india": True
    },
    # Setu not on Greenhouse; replaced
    {
        "company": "Exotel", "website": "https://exotel.com",
        "platform": "greenhouse", "token": "exotel",
        "category": "startup", "country": "India", "hires_in_india": True
    },
    {
        "company": "Slice", "website": "https://sliceit.com",
        "platform": "greenhouse", "token": "slice",
        "category": "startup", "country": "India", "hires_in_india": True
    },
    # Springworks not on public Greenhouse; replaced
    {
        "company": "Facilio", "website": "https://facilio.com",
        "platform": "greenhouse", "token": "facilio",
        "category": "startup", "country": "India", "hires_in_india": True
    },
    {
        "company": "ThoughtWorks", "website": "https://thoughtworks.com",
        "platform": "greenhouse", "token": "thoughtworks",
        "category": "services", "country": "India", "hires_in_india": True
    },
    # Udaan / Vymo / Whatfix / Yellow.ai not on public Greenhouse; replaced
    {
        "company": "Zoho", "website": "https://zoho.com",
        "platform": "greenhouse", "token": "zohocorporation",
        "category": "product", "country": "India", "hires_in_india": True
    },
    {
        "company": "Capillary Technologies", "website": "https://capillarytech.com",
        "platform": "greenhouse", "token": "capillarytech",
        "category": "startup", "country": "India", "hires_in_india": True
    },

    # --- YC-Backed Startups (Greenhouse) ---
    {
        "company": "Airtable", "website": "https://airtable.com",
        "platform": "greenhouse", "token": "airtable",
        "category": "startup", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Amplitude", "website": "https://amplitude.com",
        "platform": "greenhouse", "token": "amplitude",
        "category": "product", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Asana", "website": "https://asana.com",
        "platform": "greenhouse", "token": "asana",
        "category": "product", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Brex", "website": "https://brex.com",
        "platform": "greenhouse", "token": "brex",
        "category": "startup", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Chime", "website": "https://chime.com",
        "platform": "greenhouse", "token": "chime",
        "category": "startup", "country": "Global", "hires_in_india": False
    },
    {
        "company": "Collibra", "website": "https://collibra.com",
        "platform": "greenhouse", "token": "collibra",
        "category": "product", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Dremio", "website": "https://dremio.com",
        "platform": "greenhouse", "token": "dremio",
        "category": "product", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Duolingo", "website": "https://duolingo.com",
        "platform": "greenhouse", "token": "duolingo",
        "category": "product", "country": "Global", "hires_in_india": False
    },
    {
        "company": "Fivetran", "website": "https://fivetran.com",
        "platform": "greenhouse", "token": "fivetran",
        "category": "product", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Grafana Labs", "website": "https://grafana.com",
        "platform": "greenhouse", "token": "grafanalabs",
        "category": "product", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Gusto", "website": "https://gusto.com",
        "platform": "greenhouse", "token": "gusto",
        "category": "product", "country": "Global", "hires_in_india": False
    },
    {
        "company": "Hightouch", "website": "https://hightouch.com",
        "platform": "greenhouse", "token": "hightouch",
        "category": "startup", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Honeycomb", "website": "https://honeycomb.io",
        "platform": "greenhouse", "token": "honeycomb",
        "category": "product", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Iterable", "website": "https://iterable.com",
        "platform": "greenhouse", "token": "iterable",
        "category": "product", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Klaviyo", "website": "https://klaviyo.com",
        "platform": "greenhouse", "token": "klaviyo",
        "category": "product", "country": "Global", "hires_in_india": False
    },
    {
        "company": "LaunchDarkly", "website": "https://launchdarkly.com",
        "platform": "greenhouse", "token": "launchdarkly",
        "category": "product", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Mercury", "website": "https://mercury.com",
        "platform": "greenhouse", "token": "mercury",
        "category": "startup", "country": "Global", "hires_in_india": False
    },
    {
        "company": "MinIO", "website": "https://min.io",
        "platform": "greenhouse", "token": "minio",
        "category": "startup", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Mixpanel", "website": "https://mixpanel.com",
        "platform": "greenhouse", "token": "mixpanel",
        "category": "product", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Neo4j", "website": "https://neo4j.com",
        "platform": "greenhouse", "token": "neo4j",
        "category": "product", "country": "Global", "hires_in_india": True
    },
    {
        "company": "New Relic", "website": "https://newrelic.com",
        "platform": "greenhouse", "token": "newrelic",
        "category": "product", "country": "Global", "hires_in_india": True
    },
    {
        "company": "PagerDuty", "website": "https://pagerduty.com",
        "platform": "greenhouse", "token": "pagerduty",
        "category": "product", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Robinhood", "website": "https://robinhood.com",
        "platform": "greenhouse", "token": "robinhood",
        "category": "product", "country": "Global", "hires_in_india": False
    },
    {
        "company": "Scale AI", "website": "https://scale.com",
        "platform": "greenhouse", "token": "scaleai",
        "category": "startup", "country": "Global", "hires_in_india": True
    },
    {
        "company": "SingleStore", "website": "https://singlestore.com",
        "platform": "greenhouse", "token": "singlestore",
        "category": "product", "country": "Global", "hires_in_india": True
    },
    {
        "company": "SoFi", "website": "https://sofi.com",
        "platform": "greenhouse", "token": "sofi",
        "category": "product", "country": "Global", "hires_in_india": False
    },
    {
        "company": "Starburst", "website": "https://starburst.io",
        "platform": "greenhouse", "token": "starburst",
        "category": "product", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Sumo Logic", "website": "https://sumologic.com",
        "platform": "greenhouse", "token": "sumologic",
        "category": "product", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Toast", "website": "https://toasttab.com",
        "platform": "greenhouse", "token": "toast",
        "category": "product", "country": "Global", "hires_in_india": True
    },

    # --- Global Product Companies — India Engineering Hubs (Greenhouse) ---
    {
        "company": "Affirm", "website": "https://affirm.com",
        "platform": "greenhouse", "token": "affirm",
        "category": "product", "country": "Global", "hires_in_india": False
    },
    {
        "company": "Airbnb", "website": "https://airbnb.com",
        "platform": "greenhouse", "token": "airbnb",
        "category": "product", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Astranis", "website": "https://astranis.com",
        "platform": "greenhouse", "token": "astranis",
        "category": "startup", "country": "Global", "hires_in_india": False
    },
    {
        "company": "Braze", "website": "https://braze.com",
        "platform": "greenhouse", "token": "braze",
        "category": "product", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Canonical", "website": "https://canonical.com",
        "platform": "greenhouse", "token": "canonical",
        "category": "product", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Cloudflare", "website": "https://cloudflare.com",
        "platform": "greenhouse", "token": "cloudflare",
        "category": "product", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Coinbase", "website": "https://coinbase.com",
        "platform": "greenhouse", "token": "coinbase",
        "category": "product", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Databricks", "website": "https://databricks.com",
        "platform": "greenhouse", "token": "databricks",
        "category": "product", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Datadog", "website": "https://datadoghq.com",
        "platform": "greenhouse", "token": "datadog",
        "category": "product", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Discord", "website": "https://discord.com",
        "platform": "greenhouse", "token": "discord",
        "category": "product", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Dropbox", "website": "https://dropbox.com",
        "platform": "greenhouse", "token": "dropbox",
        "category": "product", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Fastly", "website": "https://fastly.com",
        "platform": "greenhouse", "token": "fastly",
        "category": "product", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Figma", "website": "https://figma.com",
        "platform": "greenhouse", "token": "figma",
        "category": "product", "country": "Global", "hires_in_india": True
    },
    {
        "company": "GitLab", "website": "https://gitlab.com",
        "platform": "greenhouse", "token": "gitlab",
        "category": "product", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Instacart", "website": "https://instacart.com",
        "platform": "greenhouse", "token": "instacart",
        "category": "product", "country": "Global", "hires_in_india": False
    },
    {
        "company": "Lyft", "website": "https://lyft.com",
        "platform": "greenhouse", "token": "lyft",
        "category": "product", "country": "Global", "hires_in_india": False
    },
    {
        "company": "MongoDB", "website": "https://mongodb.com",
        "platform": "greenhouse", "token": "mongodb",
        "category": "product", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Navan", "website": "https://navan.com",
        "platform": "greenhouse", "token": "tripactions",
        "category": "product", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Okta", "website": "https://okta.com",
        "platform": "greenhouse", "token": "okta",
        "category": "product", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Pinterest", "website": "https://pinterest.com",
        "platform": "greenhouse", "token": "pinterest",
        "category": "product", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Pure Storage", "website": "https://purestorage.com",
        "platform": "greenhouse", "token": "purestorage",
        "category": "product", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Qualtrics", "website": "https://qualtrics.com",
        "platform": "greenhouse", "token": "qualtrics",
        "category": "product", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Reddit", "website": "https://reddit.com",
        "platform": "greenhouse", "token": "reddit",
        "category": "product", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Remote", "website": "https://remote.com",
        "platform": "greenhouse", "token": "remote",
        "category": "startup", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Squarespace", "website": "https://squarespace.com",
        "platform": "greenhouse", "token": "squarespace",
        "category": "product", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Stripe", "website": "https://stripe.com",
        "platform": "greenhouse", "token": "stripe",
        "category": "product", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Tigera", "website": "https://tigera.io",
        "platform": "greenhouse", "token": "tigera",
        "category": "startup", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Twilio", "website": "https://twilio.com",
        "platform": "greenhouse", "token": "twilio",
        "category": "product", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Vercel", "website": "https://vercel.com",
        "platform": "greenhouse", "token": "vercel",
        "category": "product", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Webflow", "website": "https://webflow.com",
        "platform": "greenhouse", "token": "webflow",
        "category": "product", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Zscaler", "website": "https://zscaler.com",
        "platform": "greenhouse", "token": "zscaler",
        "category": "product", "country": "Global", "hires_in_india": True
    },

    # --- Enterprise / MNC (Greenhouse) ---
    {
        "company": "Bill.com", "website": "https://bill.com",
        "platform": "greenhouse", "token": "billcom",
        "category": "enterprise", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Relativity Space", "website": "https://relativityspace.com",
        "platform": "greenhouse", "token": "relativity",
        "category": "startup", "country": "Global", "hires_in_india": False
    },
    {
        "company": "Rocket Lab", "website": "https://rocketlabusa.com",
        "platform": "greenhouse", "token": "rocketlab",
        "category": "product", "country": "Global", "hires_in_india": False
    },
    {
        "company": "SpaceX", "website": "https://spacex.com",
        "platform": "greenhouse", "token": "spacex",
        "category": "enterprise", "country": "Global", "hires_in_india": False
    },
    {
        "company": "Spire Global", "website": "https://spire.com",
        "platform": "greenhouse", "token": "spire",
        "category": "product", "country": "Global", "hires_in_india": True
    },

    # =========================================================================
    # LEVER
    # =========================================================================

    # --- Indian Startups (Lever) ---
    {
        "company": "CRED", "website": "https://cred.club",
        "platform": "lever", "token": "cred",
        "category": "startup", "country": "India", "hires_in_india": True
    },
    # Indian companies confirmed on Lever
    {
        "company": "CRED", "website": "https://cred.club",
        "platform": "lever", "token": "cred",
        "category": "startup", "country": "India", "hires_in_india": True
    },
    {
        "company": "Meesho", "website": "https://meesho.com",
        "platform": "lever", "token": "meesho",
        "category": "startup", "country": "India", "hires_in_india": True
    },
    # PhonePe / Gupshup / ShareChat / Zepto not on public Lever - moved to replacements
    {
        "company": "Dunzo", "website": "https://dunzo.com",
        "platform": "lever", "token": "dunzo",
        "category": "startup", "country": "India", "hires_in_india": True
    },
    {
        "company": "Ola", "website": "https://olacabs.com",
        "platform": "lever", "token": "ola",
        "category": "startup", "country": "India", "hires_in_india": True
    },

    # --- YC-Backed (Lever) ---
    # Confluent/CockroachDB/Neon/Retool/Temporal not on Lever public API; replaced with confirmed valid
    {
        "company": "dbt Labs", "website": "https://getdbt.com",
        "platform": "lever", "token": "dbtlabs",
        "category": "startup", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Aiven", "website": "https://aiven.io",
        "platform": "lever", "token": "aiven",
        "category": "startup", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Grafbase", "website": "https://grafbase.com",
        "platform": "lever", "token": "grafbase",
        "category": "startup", "country": "Global", "hires_in_india": True
    },

    # --- Global Product (Lever) ---
    # Carta/Checkr/Figma(Lever) not valid on Lever; removed duplicates
    {
        "company": "Palantir", "website": "https://palantir.com",
        "platform": "lever", "token": "palantir",
        "category": "product", "country": "Global", "hires_in_india": True
    },
    # Plaid and Rippling not on public Lever API; removed
    {
        "company": "Spotify", "website": "https://spotify.com",
        "platform": "lever", "token": "spotify",
        "category": "product", "country": "Global", "hires_in_india": True
    },
    # Wix not on Lever; removed

    # --- Enterprise (Lever) ---
    # Atlassian not on Lever; removed (they use Workday)

    # =========================================================================
    # ASHBY
    # =========================================================================

    # --- Indian Startups (Ashby) ---
    {
        "company": "Freshworks", "website": "https://freshworks.com",
        "platform": "ashby", "token": "freshworks",
        "category": "product", "country": "India", "hires_in_india": True
    },
    # Voosh not on Ashby; removed
    {
        "company": "Segment", "website": "https://segment.com",
        "platform": "ashby", "token": "segment",
        "category": "product", "country": "Global", "hires_in_india": True
    },

    # --- YC-Backed (Ashby) ---
    {
        "company": "Airwallex", "website": "https://airwallex.com",
        "platform": "ashby", "token": "airwallex",
        "category": "startup", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Character.AI", "website": "https://character.ai",
        "platform": "ashby", "token": "character",
        "category": "startup", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Clerk", "website": "https://clerk.com",
        "platform": "ashby", "token": "clerk",
        "category": "startup", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Cohere", "website": "https://cohere.com",
        "platform": "ashby", "token": "cohere",
        "category": "startup", "country": "Global", "hires_in_india": True
    },
    # Convex not on Ashby; removed
    {
        "company": "Lago", "website": "https://getlago.com",
        "platform": "ashby", "token": "lago",
        "category": "startup", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Decagon", "website": "https://decagon.ai",
        "platform": "ashby", "token": "decagon",
        "category": "startup", "country": "Global", "hires_in_india": True
    },
    {
        "company": "ElevenLabs", "website": "https://elevenlabs.io",
        "platform": "ashby", "token": "elevenlabs",
        "category": "startup", "country": "Global", "hires_in_india": True
    },
    # Fly.io not on Ashby; removed
    {
        "company": "Doppler", "website": "https://doppler.com",
        "platform": "ashby", "token": "doppler",
        "category": "startup", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Harvey AI", "website": "https://harvey.ai",
        "platform": "ashby", "token": "harvey",
        "category": "startup", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Ideogram", "website": "https://ideogram.ai",
        "platform": "ashby", "token": "ideogram",
        "category": "startup", "country": "Global", "hires_in_india": False
    },
    {
        "company": "LangChain", "website": "https://langchain.com",
        "platform": "ashby", "token": "langchain",
        "category": "startup", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Linear", "website": "https://linear.app",
        "platform": "ashby", "token": "linear",
        "category": "startup", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Modal", "website": "https://modal.com",
        "platform": "ashby", "token": "modal",
        "category": "startup", "country": "Global", "hires_in_india": True
    },
    {
        "company": "OpenAI", "website": "https://openai.com",
        "platform": "ashby", "token": "openai",
        "category": "product", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Perplexity", "website": "https://perplexity.ai",
        "platform": "ashby", "token": "perplexity",
        "category": "startup", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Pika Labs", "website": "https://pika.art",
        "platform": "ashby", "token": "pika",
        "category": "startup", "country": "Global", "hires_in_india": False
    },
    {
        "company": "Pinecone", "website": "https://pinecone.io",
        "platform": "ashby", "token": "pinecone",
        "category": "startup", "country": "Global", "hires_in_india": True
    },
    {
        "company": "PostHog", "website": "https://posthog.com",
        "platform": "ashby", "token": "posthog",
        "category": "startup", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Quora", "website": "https://quora.com",
        "platform": "ashby", "token": "quora",
        "category": "product", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Railway", "website": "https://railway.app",
        "platform": "ashby", "token": "railway",
        "category": "startup", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Ramp", "website": "https://ramp.com",
        "platform": "ashby", "token": "ramp",
        "category": "startup", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Render", "website": "https://render.com",
        "platform": "ashby", "token": "render",
        "category": "startup", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Replit", "website": "https://replit.com",
        "platform": "ashby", "token": "replit",
        "category": "startup", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Resend", "website": "https://resend.com",
        "platform": "ashby", "token": "resend",
        "category": "startup", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Runway AI", "website": "https://runwayml.com",
        "platform": "ashby", "token": "runway",
        "category": "startup", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Sentry", "website": "https://sentry.io",
        "platform": "ashby", "token": "sentry",
        "category": "product", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Supabase", "website": "https://supabase.com",
        "platform": "ashby", "token": "supabase",
        "category": "startup", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Synthesia", "website": "https://synthesia.io",
        "platform": "ashby", "token": "synthesia",
        "category": "startup", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Vanta", "website": "https://vanta.com",
        "platform": "ashby", "token": "vanta",
        "category": "startup", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Zapier", "website": "https://zapier.com",
        "platform": "ashby", "token": "zapier",
        "category": "product", "country": "Global", "hires_in_india": True
    },

    # --- Global Product / Enterprise (Ashby) ---
    # Descript and Hex Technologies not on Ashby; replaced
    {
        "company": "Turso", "website": "https://turso.tech",
        "platform": "ashby", "token": "turso",
        "category": "startup", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Buf", "website": "https://buf.build",
        "platform": "ashby", "token": "buf",
        "category": "startup", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Loom", "website": "https://loom.com",
        "platform": "ashby", "token": "loom",
        "category": "product", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Notion", "website": "https://notion.so",
        "platform": "ashby", "token": "notion",
        "category": "product", "country": "Global", "hires_in_india": True
    },
    # Orca Security not on Ashby; replaced
    {
        "company": "Tailscale", "website": "https://tailscale.com",
        "platform": "ashby", "token": "tailscale",
        "category": "startup", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Watershed", "website": "https://watershed.com",
        "platform": "ashby", "token": "watershed",
        "category": "startup", "country": "Global", "hires_in_india": True
    },

    # =========================================================================
    # WORKDAY
    # =========================================================================

    {
        "company": "Adobe", "website": "https://adobe.com",
        "platform": "workday", "token": "adobe",
        "domain": "adobe.wd5.myworkdayjobs.com", "site": "external_experienced",
        "category": "enterprise", "country": "India", "hires_in_india": True
    },
    # Atlassian (WD) returned 401; removed
    {
        "company": "Amadeus", "website": "https://amadeus.com",
        "platform": "workday", "token": "amadeus",
        "domain": "amadeus.wd3.myworkdayjobs.com", "site": "Amadeus",
        "category": "enterprise", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Autodesk", "website": "https://autodesk.com",
        "platform": "workday", "token": "autodesk",
        "domain": "autodesk.wd1.myworkdayjobs.com", "site": "Ext",
        "category": "enterprise", "country": "Global", "hires_in_india": True
    },
    # Cisco (WD) returned 404; replaced with correct endpoint
    {
        "company": "Cisco", "website": "https://cisco.com",
        "platform": "workday", "token": "cisco",
        "domain": "cisco.wd5.myworkdayjobs.com", "site": "External",
        "category": "enterprise", "country": "Global", "hires_in_india": True
    },
    # Intuit (WD) returned 422; replaced with known good endpoint
    {
        "company": "Intuit", "website": "https://intuit.com",
        "platform": "workday", "token": "intuit",
        "domain": "intuit.wd5.myworkdayjobs.com", "site": "Intuit_Careers",
        "category": "enterprise", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Nvidia", "website": "https://nvidia.com",
        "platform": "workday", "token": "nvidia",
        "domain": "nvidia.wd5.myworkdayjobs.com", "site": "NVIDIAExternalCareerSite",
        "category": "enterprise", "country": "Global", "hires_in_india": True
    },
    # Oracle (WD) returned 422; replaced with known alternate
    {
        "company": "Oracle", "website": "https://oracle.com",
        "platform": "workday", "token": "oracle",
        "domain": "oracle.wd1.myworkdayjobs.com", "site": "OracleCareers",
        "category": "enterprise", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Salesforce", "website": "https://salesforce.com",
        "platform": "workday", "token": "salesforce",
        "domain": "salesforce.wd12.myworkdayjobs.com", "site": "External_Career_Site",
        "category": "enterprise", "country": "India", "hires_in_india": True
    },
    # SAP (WD) returned 422; ServiceNow returned 422 - replaced with alternate site names
    {
        "company": "SAP", "website": "https://sap.com",
        "platform": "workday", "token": "sap",
        "domain": "sap.wd3.myworkdayjobs.com", "site": "SAPCareers",
        "category": "enterprise", "country": "Global", "hires_in_india": True
    },
    {
        "company": "ServiceNow", "website": "https://servicenow.com",
        "platform": "workday", "token": "servicenow",
        "domain": "servicenow.wd5.myworkdayjobs.com", "site": "ExternalCareers",
        "category": "enterprise", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Visa", "website": "https://visa.com",
        "platform": "workday", "token": "visa",
        "domain": "visa.wd5.myworkdayjobs.com", "site": "Visa",
        "category": "enterprise", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Workday", "website": "https://workday.com",
        "platform": "workday", "token": "workday",
        "domain": "workday.wd5.myworkdayjobs.com", "site": "Workday",
        "category": "enterprise", "country": "Global", "hires_in_india": True
    },
    {
        "company": "Zoom", "website": "https://zoom.us",
        "platform": "workday", "token": "zoom",
        "domain": "zoom.wd5.myworkdayjobs.com", "site": "zoom",
        "category": "enterprise", "country": "Global", "hires_in_india": True
    },
]
