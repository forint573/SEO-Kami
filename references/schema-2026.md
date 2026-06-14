# Schema / Structured Data 2026

Which structured data still earns rich results, which is deprecated, and what each type requires. All deprecation/threshold claims are **PROVEN** (Google primary docs).

## Contents
- [Still earns vs deprecated (table)](#still-earns-vs-deprecated)
- [JSON-LD over microdata](#json-ld-over-microdata)
- [Required properties per common type](#required-properties)
- [Removing deprecated schema = no ranking drop](#removing-deprecated-schema)
- [Schema is not required for AI features](#schema-and-ai)
- [Assets](#assets)

## Still earns vs deprecated

| Type | Status | Notes |
|---|---|---|
| Product | STILL EARNS | Merchant listings, price/availability, review stars |
| Review / AggregateRating | STILL EARNS | Star ratings on eligible host types (Product, Recipe, etc.) |
| Article | STILL EARNS | Top-stories, headline/image enrichment |
| Recipe | STILL EARNS | Recipe rich result, host carousel |
| Video | STILL EARNS | Video rich result, key moments, live badge |
| Event | STILL EARNS | Event rich result |
| Organization | STILL EARNS | Knowledge-panel/entity signals (logo, sameAs) |
| Person | STILL EARNS | Entity/knowledge-panel signals |
| LocalBusiness | STILL EARNS | Local rich result + entity NAP signals |
| Breadcrumb | STILL EARNS | Breadcrumb trail in SERP |
| **FAQPage** | **DEPRECATED ~2026-05-07** | Markup still valid; zero enhancement except authoritative gov/health sites |
| **HowTo** | **DEPRECATED** | No rich result on any surface |
| **ClaimReview, SpecialAnnouncement, Vehicle Listing, Course Info, Estimated Salary, Learning Video, Book Actions, Practice Problems** | **DEPRECATED 2025-2026** | Removed in Google's "simplifying search results" effort (rolling Sept 2025 → Jan 2026). Markup stays valid; the specific rich-result display and Search Console reporting are gone, ranking unaffected. PROVEN ([Google blog](https://developers.google.com/search/blog/2025/06/simplifying-search-results)) |

PROVEN. Validity (parses, no errors) is separate from eligibility (earns a visual feature). Deprecated types are still valid markup; they simply no longer render an enhancement.

## JSON-LD over microdata

Use **JSON-LD** (a `<script type="application/ld+json">` block), not microdata or RDFa. JSON-LD decouples markup from rendered DOM, survives template/JS changes, is Google's recommended format, and is easiest to validate and template. Microdata couples structured data to visible HTML and is brittle. PROVEN (Google recommendation).

## Required properties

Minimum properties Google needs to consider a type for its rich result. Omitting a required property forfeits eligibility silently. PROVEN.

- **Product** — `name`, `image`; plus for merchant listing one of `offers` (with `price`, `priceCurrency`, `availability`) or `aggregateRating`/`review`. `offers` is what unlocks price/availability display.
- **Review** — `itemReviewed`, `reviewRating` (with `ratingValue`), `author`. **AggregateRating** — `itemReviewed`, `ratingValue`, `ratingCount` (or `reviewCount`). Ratings must reflect on-page, verifiable reviews.
- **Article** — `headline`; strongly recommended `image`, `datePublished`, `author` (as `Person`/`Organization` with `name`).
- **Recipe** — `name`, `image`; recommended `recipeIngredient`, `recipeInstructions`, plus `aggregateRating`/`nutrition`/`video` for richer display.
- **Video** — `name`, `description`, `thumbnailUrl`, `uploadDate`; `contentUrl` or `embedUrl` for indexing.
- **Event** — `name`, `startDate`, `location` (with address or `VirtualLocation`).
- **Organization** — `name`, `url`; recommended `logo`, `sameAs` (drives entity/knowledge-panel signals).
- **Person** — `name`; recommended `url`, `sameAs`, `jobTitle`.
- **LocalBusiness** — `name`, `address`; recommended `telephone`, `openingHours`, `geo`, consistent NAP matching the Google Business Profile.
- **BreadcrumbList** — ordered `itemListElement` of `ListItem` each with `position`, `name`, `item`.

## Removing deprecated schema

Removing FAQPage or HowTo markup causes **no ranking drop**. PROVEN. These never were ranking factors — they granted a SERP visual enhancement that no longer renders. Leaving stale FAQPage/HowTo costs nothing but earns nothing (outside authoritative gov/health for FAQPage); remove it during cleanups to cut template weight without ranking risk.

## Schema and AI

Structured data is **not required for AI features** and is **not an AI shortcut**. PROVEN — Google's 2026 AI-optimization guidance lists "special schema markup" among things NOT needed for AI Overviews / AI Mode, which run on the same index and core quality systems. Schema helps classic rich results and entity clarity (`Organization`/`Person` `sameAs` feed entity understanding); it does not buy AI citation. Flag "add FAQ schema to win AI answers" as HYPE.

## Assets

- Templates: `assets/schema-templates.json` (copy-paste JSON-LD blocks per type above).
- Validator: `schema_check.py` (flags deprecated types, missing required properties, microdata usage).
- Validate output in Google's Rich Results Test and Search Console "Enhancements" reports — only currently-supported types report there.
