---
name: dealer-finder
description: Find and score local dealers / distributors for an industrial product (pumps, vacuum pumps, etc.) in Indonesia, Vietnam or Cambodia, and output a sourced CSV + WhatsApp drafts. Use when the user says "find dealers", "find distributors", "dealer list", "cari distributor", "tìm nhà phân phối", or names a product + country to sell into (e.g. "submersible pumps Indonesia", "vacuum pumps Vietnam"). Every row must carry a source URL — no source, no row.
---

# Dealer Finder

Input: **product + country**, optionally a **principal brand** you represent (e.g. "vacuum pumps, Vietnam, principal: Edwards").
Output: a scored dealer CSV where every fact has a source, plus outreach drafts for the top 30. A human sends the messages — never send them yourself.

## 0. Setup
- If `local.md` exists next to this file, read it first (machine-specific settings such as the Exa key file).
- Read `countries/<country>.md` for cities, directories, language notes and the product section matching the request. If the country or product section is missing, write it first in the same shape (local-language keywords, top cities + why, competitor brands, local B2B directories), then continue.
- Exa search: `python3 ~/.claude/skills/dealer-finder/scripts/exa_search.py "<query>" -n 10 [--domains a.com,b.com] [--category company] [--env-file <path>]`. Needs `EXA_API_KEY` in env or `--env-file`. If the key is missing, stop and tell the user — don't hunt for keys.
- Fallback if no Exa: WebSearch + WebFetch.
- Optional: with an Apify MCP / `APIFY_TOKEN`, run the Google Maps actor (`compass/crawler-google-places`) per keyword × city for bulk phone/rating data. Without it, skip.
- Output folder: `./dealer-finder/<country>-<product>-<YYYY-MM-DD>/`. Save raw search results to `raw/*.jsonl` as you go.

## 1. Seed — existing channels (highest quality)
1. **If a principal brand is given:** map its existing channel in this country first (brand site "where to buy" / contact pages, Exa `"<principal> distributor <country>"`). Add column `carries_principal` (yes / no / unknown). Confirmed existing distributors stay in the CSV with `EXISTING CHANNEL` in notes and are excluded from outreach. Resellers of the principal with unconfirmed status: flag in notes, don't assume either way.
2. **Competitor brands** (from the country file): Exa `"<brand> distributor <country>"` + the local-language variant, then WebFetch the brand's distributor page. Record each distributor with brands carried + source URL.
3. If the principal and a competitor share a parent group (country file notes this), mark that competitor's dealers `possible conflict (same parent group)`.

## 2. Expand — keyword × city
For each local keyword × top city: Exa search plain, then with `--domains` set to the country's directories. Pull company name, city, phone/WhatsApp, email, website, brands mentioned. Run in parallel batches; ~40–80 queries total.

## 3. Dedupe + verify
- Merge by normalized company name (drop legal suffixes from the country file, punctuation) and by phone.
- For the top ~40, WebFetch at least one source to confirm the company exists and sells the product. Unconfirmed → `verified=no`, keep but rank lower.
- Never invent a phone, email, address or brand. Blank is fine.

## 4. Score (0–10)
| Signal | Points |
|---|---|
| Sells the same product category | +3 |
| Industrial / B2B customers (segments in the country file) | +2 |
| Multi-brand (not exclusive to one competitor) | +2 |
| Multiple branches / covers several provinces | +1 |
| Has website or active marketplace store | +1 |
| Verified in step 3 | +1 |
| Exclusive dealer of a big competitor | −2 |
| Retail-only shop, single outlet | −1 |

## 5. Output
`dealers.csv` columns:
`rank,score,company,city,province,phone_whatsapp,email,website,brands_carried,carries_principal,segment,verified,source_url_1,source_url_2,notes`
(drop `carries_principal` if no principal was given)

`outreach.md` — top 30 (excluding existing channel): one WhatsApp message each in the outreach language from the country file, ≤5 lines: who we are (sender = `[Name]` placeholder, never a real person), product, why them (a brand/segment they carry), ask for a 15-min call. Plain text, no links.

`summary.md` — counts (found / verified / existing channel / per city), top 10 table, gaps.

## 6. Report back
Total rows, verified count, existing-channel count, top 10 (company · city · score · why), file paths. State plainly where coverage is thin.

## Known limits (from real runs)
- B2B directories often hide phone/email behind login → expect ~half the rows without contacts.
- Consumer marketplaces return a lot of noise (cleaners, spare parts) — filter hard.
- High-end segments (semiconductor, pharma) are often served directly by principals, so dealer search under-covers them.
- Small towns and Cambodia have thin web presence; many dealers exist only on Facebook / Google Maps.

## Rules
- No source URL → drop the row.
- Don't contact anyone, submit forms, or sign up for directories.
- Keep the user's identity out of search queries.
