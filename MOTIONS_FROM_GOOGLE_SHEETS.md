# Using Google Sheets for Motions

You can store debate motions in Google Sheets and have the bot fetch them automatically at startup. This replaces or complements the local files in `data/english.txt` and `data/bangla.txt`.

## Supported CSV formats

The bot supports two ways of structuring your sheet(s):

1) Combined sheet (single CSV) with headers
- language: english or bangla
- motion: the motion text

2) Separate sheet per language (one CSV per language)
- First column contains the motion text (a header named `motion` is optional)

## Configuration

Set one of the following environment variable combinations:

- MOTIONS_CSV_URL_COMBINED: CSV export URL for the combined sheet

or

- MOTIONS_CSV_URL_ENGLISH: CSV export URL for English motions
- MOTIONS_CSV_URL_BANGLA: CSV export URL for Bangla motions

If both combined and per-language URLs are provided, the bot tries the combined sheet first, then falls back to per-language URLs if needed. If all remote fetches fail, the bot falls back to the local text files.

## Getting a CSV URL from Google Sheets

Option A: Publish to the web as CSV
1. File → Share → Anyone with the link (Viewer)
2. File → Share → Publish to web → Select the sheet tab → CSV → Publish

Option B: Manually build the CSV export URL
- Pattern: `https://docs.google.com/spreadsheets/d/<SHEET_ID>/export?format=csv&gid=<SHEET_GID>`
- SHEET_ID: The long ID in the sheet URL
- gid: The numeric sheet/tab identifier

## Notes

- Remote fetching happens on startup when the bot imports `src/utils/language.py`.
- The bot uses `requests` and times out after ~15s per URL.
- Only the languages `english` and `bangla` are recognized for now. Motions for unknown languages are ignored.
- Local files are still supported and used as a fallback.
