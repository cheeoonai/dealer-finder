# dealer-finder

A Claude Code skill that finds local **dealers and distributors** for industrial products in **Indonesia, Vietnam and Cambodia**, and scores them. Pumps and vacuum pumps come configured; other products can be added.

Ask ChatGPT for distributors and it makes up companies and phone numbers. This skill searches the web with [Exa](https://exa.ai), opens each source page to check it, and keeps a company **only if a real URL backs it**.

## What you get

For each run, a folder `dealer-finder/<country>-<product>-<date>/` containing:

| File | Contents |
|---|---|
| `dealers.csv` | Scored list: company, city, phone/WhatsApp, email, website, brands carried, verified flag, source URLs, notes |
| `outreach.md` | WhatsApp/Zalo message drafts in the local language for the top 30. They are **not sent**; you review and send them yourself |
| `summary.md` | Counts, top 10, and where coverage is thin |

A first real run (vacuum pumps, Indonesia, 62 searches) returned 36 dealers, 32 of them confirmed on their source pages, in about 15 minutes.

## Install

```bash
git clone https://github.com/cheeoonai/dealer-finder ~/.claude/skills/dealer-finder
```

Get an Exa API key at [exa.ai](https://exa.ai) (there is a free tier), then:

```bash
export EXA_API_KEY=your_key_here
```

The script uses only the Python standard library, so there is nothing to `pip install`.

## Use

In Claude Code:

```
find dealers, submersible pumps, Indonesia
find distributors, vacuum pumps, Vietnam, principal: <brand you represent>
```

With `principal:` set, the skill first maps that brand's **existing** distributors in the country and leaves them out of outreach. It also flags dealers of competitors that share the brand's parent group.

## How it works

1. **Seed**: the principal's existing channel, then competitor brands' distributor lists, which are the highest-quality leads.
2. **Expand**: local-language keywords × industrial cities, plain and on local B2B directories.
3. **Dedupe and verify**: merges by name and phone, and opens the source page for the top ~40.
4. **Score 0–10**: same product category, B2B segment, multi-brand, branches, verified; points are deducted for exclusive dealers of big competitors.
5. **Output**: CSV, outreach drafts and summary.

## Add a country or product

Copy `countries/indonesia.md` and fill in the same sections: language and phone notes, directories, cities with the reason for each, then one `## Product:` block per product (keywords, segments, competitor brands). If a country file is missing, the skill writes one first.

## Optional

- **Apify** (Google Maps actor) adds bulk phone numbers and ratings if you have an `APIFY_TOKEN` or the Apify MCP.
- Put machine-specific settings in a `local.md` next to `SKILL.md`. It's gitignored.

## Limits

- B2B directories often hide contact details behind a login, so about half the rows have no phone number.
- In Cambodia and in small towns, many dealers exist only on Facebook or Google Maps.
- High-end segments such as semiconductor are usually served directly by the brands, so this kind of search finds few dealers there.

## License

MIT
