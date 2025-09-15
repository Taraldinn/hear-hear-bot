"""
Language and localization utilities
Author: aldinn
Email: kferdoush617@gmail.com
"""

import random
from pathlib import Path
import csv
from io import StringIO
import requests
from config.settings import Config


class LanguageManager:
    """Manages language support and motion generation"""

    def __init__(self):
        self.supported_languages = ["english", "bangla"]
        # motions[language] -> list of entries: { 'text': str, 'info': Optional[str] }
        self.motions = {}
        self.load_motions()

    def load_motions(self):
        """Load motions from Google Sheets CSV if configured; otherwise fall back to local files"""
        # Try Google Sheets sources first
        combined = getattr(Config, "MOTIONS_CSV_URL_COMBINED", None)
        en_url = getattr(Config, "MOTIONS_CSV_URL_ENGLISH", None)
        bn_url = getattr(Config, "MOTIONS_CSV_URL_BANGLA", None)

        loaded_any = False

        if combined:
            try:
                data = self._fetch_csv(combined)
                self._load_from_combined_csv(data)
                loaded_any = any(
                    self.motions.get(lang) for lang in self.supported_languages
                )
            except requests.exceptions.RequestException as e:
                print(f"⚠️ Failed to fetch combined CSV: {e}")
            except ValueError as e:
                print(f"⚠️ Failed to parse combined CSV: {e}")

        # If not using combined or combined failed/empty, attempt per-language URLs
        if not loaded_any and (en_url or bn_url):
            try:
                if en_url:
                    en_data = self._fetch_csv(en_url)
                    self.motions["english"] = self._extract_motions_from_simple_csv(
                        en_data
                    )
                if bn_url:
                    bn_data = self._fetch_csv(bn_url)
                    self.motions["bangla"] = self._extract_motions_from_simple_csv(
                        bn_data
                    )
                loaded_any = any(
                    self.motions.get(lang) for lang in self.supported_languages
                )
            except requests.exceptions.RequestException as e:
                print(f"⚠️ Failed to fetch per-language CSVs: {e}")
            except ValueError as e:
                print(f"⚠️ Failed to parse per-language CSVs: {e}")

        # Fallback to local files
        if not loaded_any:
            project_root = Path(__file__).parent.parent.parent
            for language in self.supported_languages:
                file_path = project_root / "data" / f"{language}.txt"
                if file_path.exists():
                    with open(file_path, "r", encoding="utf-8") as f:
                        # Local files contain only motion text (no info slide)
                        self.motions[language] = [
                            {"text": line.strip(), "info": None}
                            for line in f.readlines()
                            if line.strip()
                        ]
                else:
                    self.motions[language] = []

    def _fetch_csv(self, url: str) -> list[list[str]]:
        """Fetch CSV data from a URL and return rows as list of lists"""
        headers = {"User-Agent": "HearHearBot/2.0 (language manager)"}
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        # Google Sheets exported CSV is UTF-8 by default
        content = resp.text
        reader = csv.reader(StringIO(content))
        return [row for row in reader]

    def _load_from_combined_csv(self, rows: list[list[str]]):
        """Parse a combined CSV with headers including 'language', 'motion' and optional 'info'/'info slide'"""
        if not rows:
            return
        # Detect header row
        header = [h.strip().lower() for h in rows[0]]
        data_rows = rows[1:] if header else rows

        # Find columns
        try:
            lang_idx = header.index("language")
        except ValueError:
            lang_idx = None
        try:
            motion_idx = header.index("motion")
        except ValueError:
            motion_idx = None
        # Info slide column can be named 'info' or 'info slide'
        info_idx = None
        for name in ("info slide", "info"):
            try:
                info_idx = header.index(name)
                break
            except ValueError:
                info_idx = None

        # If no header or columns unmatched, attempt heuristic: two columns [language, motion]
        if lang_idx is None or motion_idx is None:
            # Heuristic: if there are 2+ columns, assume first is language, last is motion, and if 3+ columns, middle is info
            for row in rows:
                if not row:
                    continue
                language = (row[0] or "").strip().lower()
                motion = (row[-1] or "").strip()
                info = None
                if len(row) >= 3:
                    info = (row[1] or "").strip() or None
                self._maybe_add_motion(language, motion, info)
            return

        for row in data_rows:
            if not row:
                continue
            language = (
                (row[lang_idx] if lang_idx is not None and lang_idx < len(row) else "")
                .strip()
                .lower()
            )
            motion = (
                row[motion_idx]
                if motion_idx is not None and motion_idx < len(row)
                else ""
            ).strip()
            info = (
                row[info_idx] if info_idx is not None and info_idx < len(row) else ""
            ).strip() or None
            self._maybe_add_motion(language, motion, info)

    def _extract_motions_from_simple_csv(self, rows: list[list[str]]) -> list[dict]:
        """Parse a simple CSV; motion is the first non-empty cell; optional info in a column named 'info' or 'info slide' if present"""
        motions: list[dict] = []
        if not rows:
            return motions
        # Check if first row is a header with 'motion'
        header = [c.strip().lower() for c in rows[0]] if rows and any(rows[0]) else []
        start_idx = (
            1
            if ("motion" in header or "info" in header or "info slide" in header)
            else 0
        )
        info_idx = None
        if start_idx == 1:
            for name in ("info slide", "info"):
                try:
                    info_idx = header.index(name)
                    break
                except ValueError:
                    info_idx = None
        for row in rows[start_idx:]:
            if not row:
                continue
            # Take the first non-empty cell
            text = next((c.strip() for c in row if c and c.strip()), "")
            info = None
            if info_idx is not None and info_idx < len(row):
                info = (row[info_idx] or "").strip() or None
            if text:
                motions.append({"text": text, "info": info})
        return motions

    def _maybe_add_motion(self, language: str, motion: str, info: str | None = None):
        if not language or not motion:
            return
        # Normalize language keys to supported names
        key = None
        if language in ("english", "en", "eng"):
            key = "english"
        elif language in ("bangla", "bn", "bengali", "bangla/bengali"):
            key = "bangla"
        if key and key in self.supported_languages:
            self.motions.setdefault(key, []).append({"text": motion, "info": info})

    def get_random_motion(self, language="english"):
        """Get a random motion in the specified language"""
        if language not in self.motions or not self.motions[language]:
            return "No motions available for this language."

        entry = random.choice(self.motions[language])
        # Backward compatibility: return the text string
        return entry.get("text") if isinstance(entry, dict) else str(entry)

    def get_random_motion_entry(self, language="english"):
        """Return a random motion entry with keys: text, info. None if unavailable."""
        items = self.motions.get(language) or []
        if not items:
            return None
        entry = random.choice(items)
        if isinstance(entry, dict):
            return {"text": entry.get("text"), "info": entry.get("info")}
        # For legacy formats
        return {"text": str(entry), "info": None}

    def get_available_languages(self):
        """Get list of available languages"""
        return [lang for lang in self.supported_languages if self.motions.get(lang)]

    def add_motion(self, language, motion, info=None):
        """Add a new motion to a language. Accepts motion text and optional info slide."""
        if language not in self.motions:
            self.motions[language] = []
        if isinstance(motion, dict):
            text = motion.get("text")
            info_val = motion.get("info")
        else:
            text = str(motion) if motion is not None else None
            info_val = info
        if text:
            self.motions[language].append({"text": text, "info": info_val})

    def get_motion_count(self, language):
        """Get the number of motions for a language"""
        return len(self.motions.get(language, []))


# Global language manager instance
language_manager = LanguageManager()
