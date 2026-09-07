#!/usr/bin/env python3
"""Safe CRUD manager for the existing Arcubus Our People page.

Important design choice:
- ADD appends a new .person card; it never rebuilds/replaces existing cards.
- UPDATE replaces only the selected .person card.
- DELETE removes only the selected .person card.
- JSON-LD Person entries are synchronized separately.
- A backup is created before the first write.
"""

import json
import re
import shutil
from html import escape, unescape
from pathlib import Path


DEFAULT_IMAGE = "assets/icons/person.svg"


class PeopleManagerError(Exception):
    """Expected error that can be shown directly by the GUI."""


class PeopleManager:
    START_MARKER = "<!-- PEOPLE_CARDS_START -->"
    END_MARKER = "<!-- PEOPLE_CARDS_END -->"

    def __init__(self, repo_root: Path):
        self.repo_root = Path(repo_root)
        self.people_page = self.repo_root / "site" / "our-people.html"
        self.image_dir = self.repo_root / "site" / "assets" / "images"
        self.backup_page = self.repo_root / "site" / "our-people.backup.html"

    # ------------------------------------------------------------------
    # File / marker handling
    # ------------------------------------------------------------------
    def _read_raw(self):
        if not self.people_page.exists():
            raise PeopleManagerError(f"Missing Our People page: {self.people_page}")
        return self.people_page.read_text(encoding="utf-8")

    def _write(self, html):
        self._backup_once()
        self.people_page.write_text(html, encoding="utf-8")

    def _backup_once(self):
        if not self.backup_page.exists():
            shutil.copy2(self.people_page, self.backup_page)

    @staticmethod
    def _matching_div_end(html, start):
        """Return the end offset of the div opened at `start`."""
        open_match = re.match(r"<div\b[^>]*>", html[start:], flags=re.I)
        if not open_match:
            raise PeopleManagerError("Invalid person-card HTML: opening div not found.")

        pos = start + open_match.end()
        depth = 1
        token_re = re.compile(r"</?div\b[^>]*>", flags=re.I)

        for m in token_re.finditer(html, pos):
            token = m.group(0)
            if token.startswith("</"):
                depth -= 1
                if depth == 0:
                    return m.end()
            elif not token.rstrip().endswith("/>"):
                depth += 1

        raise PeopleManagerError("Could not find the end of a person card.")

    @classmethod
    def _person_spans(cls, html):
        """Return (start, end) spans for direct `.person` cards in the team grid."""
        team_eyebrow = re.search(
            r'<p\s+class=["\']eyebrow["\']>\s*The team\s*</p>',
            html,
            flags=re.I,
        )
        if not team_eyebrow:
            raise PeopleManagerError("Could not locate the 'The team' section.")

        grid_start = html.find('<div class="grid g3">', team_eyebrow.end())
        if grid_start == -1:
            # Be tolerant of single quotes / extra whitespace.
            grid_match = re.search(
                r'<div\s+class=["\']grid\s+g3["\']\s*>',
                html[team_eyebrow.end():],
                flags=re.I,
            )
            if not grid_match:
                raise PeopleManagerError("Could not locate the People team grid.")
            grid_start = team_eyebrow.end() + grid_match.start()

        grid_open_end = html.find(">", grid_start) + 1
        if grid_open_end <= 0:
            raise PeopleManagerError("Could not parse the People team grid.")

        grid_end = cls._matching_div_end(html, grid_start)
        inner_start = grid_open_end
        inner_end = grid_end - len("</div>")

        spans = []
        pos = inner_start
        while pos < inner_end:
            m = re.search(r'<div\b[^>]*class=["\'][^"\']*\bperson\b[^"\']*["\'][^>]*>', html[pos:inner_end], flags=re.I)
            if not m:
                break
            start = pos + m.start()
            end = cls._matching_div_end(html, start)
            if end > inner_end:
                raise PeopleManagerError("A person card extends outside the team grid.")
            spans.append((start, end))
            pos = end

        return spans, grid_start, grid_end

    def ensure_markers(self):
        """Add markers without changing any existing person card."""
        html = self._read_raw()
        if self.START_MARKER in html and self.END_MARKER in html:
            return html

        spans, _, _ = self._person_spans(html)
        if not spans:
            raise PeopleManagerError("No person cards were found in our-people.html.")

        first_start = spans[0][0]
        last_end = spans[-1][1]
        html = (
            html[:first_start]
            + self.START_MARKER + "\n"
            + html[first_start:last_end]
            + "\n" + self.END_MARKER
            + html[last_end:]
        )
        self.people_page.write_text(html, encoding="utf-8")
        return html

    def _read(self):
        return self.ensure_markers()

    def _card_area_bounds(self, html):
        start = html.index(self.START_MARKER) + len(self.START_MARKER)
        end = html.index(self.END_MARKER, start)
        return start, end

    # ------------------------------------------------------------------
    # Card parsing
    # ------------------------------------------------------------------
    @staticmethod
    def _parse_card(card_html, index):
        image_m = re.search(r'<img\s+src=["\']([^"\']+)["\']', card_html, flags=re.I)
        name_m = re.search(r'<h3>(.*?)</h3>', card_html, flags=re.I | re.S)
        role_m = re.search(r'<p\s+class=["\']role["\']>(.*?)</p>', card_html, flags=re.I | re.S)
        profile_m = re.search(
            r'<p>(.*?)</p>\s*<div\s+class=["\']pillrow["\']',
            card_html,
            flags=re.I | re.S,
        )
        pills_m = re.search(
            r'<div\s+class=["\']pillrow["\']>(.*?)</div>',
            card_html,
            flags=re.I | re.S,
        )

        def clean(value):
            if value is None:
                return ""
            value = re.sub(r"<[^>]+>", "", value)
            return unescape(re.sub(r"\s+", " ", value).strip())

        pills = []
        if pills_m:
            pills = [
                clean(x)
                for x in re.findall(
                    r'<span\s+class=["\']pill["\']>(.*?)</span>',
                    pills_m.group(1),
                    flags=re.I | re.S,
                )
            ]

        return {
            "index": index,
            "name": clean(name_m.group(1) if name_m else ""),
            "role": clean(role_m.group(1) if role_m else ""),
            "profile": clean(profile_m.group(1) if profile_m else ""),
            "expertise1": pills[0] if len(pills) > 0 else "",
            "expertise2": pills[1] if len(pills) > 1 else "",
            "image": image_m.group(1).strip() if image_m else DEFAULT_IMAGE,
        }

    def _get_card_spans(self, html):
        """Return absolute spans for .person cards inside the marker block."""
        area_start, area_end = self._card_area_bounds(html)
        spans = []
        pos = area_start

        person_open_re = re.compile(
            r'<div\b[^>]*class=["\'][^"\']*\bperson\b[^"\']*["\'][^>]*>',
            flags=re.I,
        )

        while pos < area_end:
            m = person_open_re.search(html, pos, area_end)
            if not m:
                break
            start = m.start()
            end = self._matching_div_end(html, start)
            if end > area_end:
                raise PeopleManagerError("A person card extends outside the People card area.")
            spans.append((start, end))
            pos = end

        return spans

    def get_people(self):
        html = self._read()
        spans = self._get_card_spans(html)
        people = []
        for i, (start, end) in enumerate(spans):
            people.append(self._parse_card(html[start:end], i))
        return people

    # ------------------------------------------------------------------
    # Card rendering
    # ------------------------------------------------------------------
    @staticmethod
    def _render_card(person):
        image = escape(person.get("image") or DEFAULT_IMAGE, quote=True)
        name = escape(person.get("name", "").strip())
        role = escape(person.get("role", "").strip())
        profile = escape(person.get("profile", "").strip())
        e1 = escape(person.get("expertise1", "").strip())
        e2 = escape(person.get("expertise2", "").strip())

        pills = "".join(
            f'<span class="pill">{x}</span>'
            for x in (e1, e2) if x
        )

        return (
            '<div class="person">\n'
            f'  <div class="monogram"><img src="{image}" alt="" width="22" height="22"></div>\n'
            f'  <h3>{name}</h3>\n'
            f'  <p class="role">{role}</p>\n'
            f'  <p>{profile}</p>\n'
            f'  <div class="pillrow">{pills}</div>\n'
            '</div>'
        )

    # ------------------------------------------------------------------
    # JSON-LD
    # ------------------------------------------------------------------
    def _update_jsonld(self, html, people):
        match = re.search(
            r'(<script\s+type=["\']application/ld\+json["\']\s*>)(.*?)(</script>)',
            html,
            flags=re.I | re.S,
        )
        if not match:
            return html

        try:
            data = json.loads(match.group(2).strip())
        except json.JSONDecodeError:
            # Do not corrupt the page just because JSON-LD is malformed.
            return html

        graph = data.get("@graph", [])
        if not isinstance(graph, list):
            return html

        # Keep non-Person graph nodes exactly as they are.
        non_person = [node for node in graph if node.get("@type") != "Person"]

        person_nodes = []
        for p in people:
            node = {
                "@type": "Person",
                "name": p.get("name", "").strip(),
                "jobTitle": p.get("role", "").strip(),
                "worksFor": {"@id": "https://arcubus.in/#organization"},
                "knowsAbout": [
                    x for x in (p.get("expertise1", "").strip(), p.get("expertise2", "").strip()) if x
                ],
            }
            image = p.get("image", "").strip()
            if image and image != DEFAULT_IMAGE:
                node["image"] = "https://arcubus.in/" + image.lstrip("./")
            person_nodes.append(node)

        data["@graph"] = non_person + person_nodes
        new_json = json.dumps(data, ensure_ascii=False, indent=2)
        return html[:match.start(2)] + "\n" + new_json + "\n" + html[match.end(2):]

    # ------------------------------------------------------------------
    # Team counts
    # ------------------------------------------------------------------
    @staticmethod
    def _role_counts(people):
        directors = sum("director" in p.get("role", "").lower() for p in people)
        managers = sum("manager" in p.get("role", "").lower() for p in people)
        analysts = sum("analyst" in p.get("role", "").lower() for p in people)
        return directors, managers, analysts

    @staticmethod
    def _plural(n, singular, plural=None):
        plural = plural or singular + "s"
        return f"{n} {singular if n == 1 else plural}"

    def _update_team_counts(self, html, people):
        directors, managers, analysts = self._role_counts(people)
        sentence = (
            "Arcubus Advisors is led by "
            f"{self._plural(directors, 'director')} and staffed by "
            f"{self._plural(managers, 'manager')} and "
            f"{self._plural(analysts, 'analyst')} "
            "working exclusively on transfer pricing from Pune, India. "
            "Each client account has a named manager and analyst who stay with it across engagements."
        )

        pattern = re.compile(r'<p>Arcubus Advisors is led by.*?</p>', flags=re.I | re.S)
        if pattern.search(html):
            return pattern.sub(f"<p>{escape(sentence)}</p>", html, count=1)
        return html

    # ------------------------------------------------------------------
    # Safe write helper
    # ------------------------------------------------------------------
    def _finalize(self, html, people):
        html = self._update_jsonld(html, people)
        html = self._update_team_counts(html, people)
        self._write(html)
        return self.backup_page

    @staticmethod
    def _validate(name, role, bio):
        if not name.strip():
            raise PeopleManagerError("Person name is required.")
        if not role.strip():
            raise PeopleManagerError("Designation / role is required.")
        if not bio.strip():
            raise PeopleManagerError("Profile / experience text is required.")

    # ------------------------------------------------------------------
    # ADD: append only; never rebuild existing cards
    # ------------------------------------------------------------------
    def add_person(self, name, role, bio, expertise1, expertise2, image_source=""):
        self._validate(name, role, bio)
        html = self._read()
        spans = self._get_card_spans(html)
        if not spans:
            raise PeopleManagerError("No existing person cards found.")

        image = self._prepare_image(image_source) if image_source else DEFAULT_IMAGE
        new_person = {
            "name": name.strip(),
            "role": role.strip(),
            "profile": bio.strip(),
            "expertise1": expertise1.strip(),
            "expertise2": expertise2.strip(),
            "image": image,
        }

        # Insert immediately after the current last card, before END_MARKER.
        _, marker_end = self._card_area_bounds(html)
        insert_at = marker_end
        rendered = "\n" + self._render_card(new_person) + "\n"
        html = html[:insert_at] + rendered + html[insert_at:]

        people = self.get_people_from_html(html)
        return self._finalize(html, people)

    # ------------------------------------------------------------------
    # UPDATE: replace only selected card
    # ------------------------------------------------------------------
    def update_person(self, index, name, role, bio, expertise1, expertise2, image_path="", use_default_image=False):
        self._validate(name, role, bio)
        html = self._read()
        spans = self._get_card_spans(html)
        if index < 0 or index >= len(spans):
            raise PeopleManagerError("Selected person no longer exists.")

        people = self.get_people_from_html(html)
        current = people[index]

        if use_default_image:
            image = DEFAULT_IMAGE
        elif image_path:
            image = self._prepare_image(image_path)
        else:
            image = current.get("image") or DEFAULT_IMAGE

        updated = {
            "name": name.strip(),
            "role": role.strip(),
            "profile": bio.strip(),
            "expertise1": expertise1.strip(),
            "expertise2": expertise2.strip(),
            "image": image,
        }

        start, end = spans[index]
        html = html[:start] + self._render_card(updated) + html[end:]
        people = self.get_people_from_html(html)
        return self._finalize(html, people)

    # ------------------------------------------------------------------
    # DELETE: remove only selected card
    # ------------------------------------------------------------------
    def delete_person(self, index):
        html = self._read()
        spans = self._get_card_spans(html)
        if index < 0 or index >= len(spans):
            raise PeopleManagerError("Selected person no longer exists.")

        people = self.get_people_from_html(html)
        start, end = spans[index]
        html = html[:start] + html[end:]
        people.pop(index)
        # Re-read after removal so indexes/counts stay accurate.
        people = self.get_people_from_html(html)
        return self._finalize(html, people)

    # ------------------------------------------------------------------
    # Parse a supplied HTML string without writing it
    # ------------------------------------------------------------------
    def get_people_from_html(self, html):
        spans = self._get_card_spans(html)
        return [self._parse_card(html[s:e], i) for i, (s, e) in enumerate(spans)]

    # ------------------------------------------------------------------
    # Image handling
    # ------------------------------------------------------------------
    def _prepare_image(self, image_source):
        source = Path(image_source)
        if not source.exists() or not source.is_file():
            raise PeopleManagerError(f"Image file not found: {source}")

        allowed = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
        if source.suffix.lower() not in allowed:
            raise PeopleManagerError("Please select a PNG, JPG, JPEG, WEBP, or GIF image.")

        self.image_dir.mkdir(parents=True, exist_ok=True)
        destination = self.image_dir / source.name
        shutil.copy2(source, destination)
        return f"assets/images/{source.name}"


# ----------------------------------------------------------------------
# Compatibility functions used by gui-admin.py
# ----------------------------------------------------------------------

def _default_manager():
    return PeopleManager(Path(__file__).resolve().parent.parent)


def list_people():
    return _default_manager().get_people()


def add_person(name, role, bio, expertise1, expertise2, image_path=""):
    return _default_manager().add_person(name, role, bio, expertise1, expertise2, image_path)


def update_person(index, name, role, bio, expertise1, expertise2, image_path="", use_default_image=False):
    return _default_manager().update_person(
        index, name, role, bio, expertise1, expertise2,
        image_path=image_path,
        use_default_image=use_default_image,
    )


def delete_person(index):
    return _default_manager().delete_person(index)
