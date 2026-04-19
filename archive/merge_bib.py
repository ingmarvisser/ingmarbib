#!/usr/bin/env python3
"""Merge ingmar.bib, ingmarInProgress.bib, and works.bib into combined.bib"""

import re
import unicodedata
from copy import deepcopy
from collections import defaultdict

BASE_DIR = '/Users/ingmar/github/ingmarbib'

STOP_WORDS = {
    'a', 'an', 'the', 'of', 'in', 'on', 'and', 'for', 'to', 'with',
    'from', 'by', 'at', 'as', 'is', 'are', 'was', 'were', 'be', 'been',
    'it', 'its', 'this', 'that', 'these', 'those', 'or', 'but', 'not',
    'into', 'than', 'do', 'does',
}

PARTICLES = {'van', 'de', 'von', 'der', 'den', 'ter', 'te', 'le', 'la', 'du', 'des', 'op'}

# Fields to drop when importing from works.bib (too verbose or irrelevant)
SKIP_FIELDS = {'abstract', 'keywords', 'language', 'day', 'month', 'issn'}

# ---------------------------------------------------------------------------
# BibTeX parser
# ---------------------------------------------------------------------------

def find_matching_brace(s, start):
    depth = 0
    for i in range(start, len(s)):
        if s[i] == '{':
            depth += 1
        elif s[i] == '}':
            depth -= 1
            if depth == 0:
                return i
    return -1


def parse_field_value(s, i):
    """Return (value_without_outer_delimiters, next_i)."""
    while i < len(s) and s[i] in ' \t\n':
        i += 1
    if i >= len(s):
        return '', i
    if s[i] == '{':
        end = find_matching_brace(s, i)
        if end == -1:
            return s[i+1:], len(s)
        return s[i+1:end], end + 1
    if s[i] == '"':
        j = i + 1
        depth = 0
        while j < len(s):
            if s[j] == '{':
                depth += 1
            elif s[j] == '}':
                depth -= 1
            elif s[j] == '"' and depth == 0:
                break
            j += 1
        return s[i+1:j], j + 1
    # Bare value (number or month macro like apr)
    j = i
    while j < len(s) and s[j] not in ', \t\n}':
        j += 1
    return s[i:j].strip(), j


def parse_fields(s):
    fields = {}
    order = []
    i = 0
    while i < len(s):
        while i < len(s) and s[i] in ' \t\n,':
            i += 1
        if i >= len(s):
            break
        eq = s.find('=', i)
        if eq == -1:
            break
        nb = s.find('{', i)
        nq = s.find('"', i)
        # Find the next delimiter before eq
        next_delim = min((x for x in [nb, nq] if x != -1), default=eq + 1)
        if next_delim < eq:
            break
        name = s[i:eq].strip().lower()
        if not re.match(r'^[a-z][a-z0-9_-]*$', name):
            break
        i = eq + 1
        value, i = parse_field_value(s, i)
        if name not in fields:
            order.append(name)
        fields[name] = value
    return fields, order


def parse_bib(content):
    """Parse a BibTeX file into a list of entry dicts."""
    entries = []
    i = 0
    while i < len(content):
        at = content.find('@', i)
        if at == -1:
            break
        brace = content.find('{', at)
        if brace == -1:
            break
        etype = content[at+1:brace].strip().lower()
        if etype in ('comment', 'string', 'preamble'):
            i = brace + 1
            continue
        end = find_matching_brace(content, brace)
        if end == -1:
            break
        inner = content[brace+1:end]
        comma = inner.find(',')
        if comma == -1:
            i = end + 1
            continue
        key = inner[:comma].strip()
        fields, order = parse_fields(inner[comma+1:])
        # Normalise entry type
        if etype == 'conference':
            etype = 'inproceedings'
        entries.append({'type': etype, 'key': key, 'fields': fields, 'order': order})
        i = end + 1
    return entries


def parse_works_bib(content):
    """Parse works.bib, stripping HTML garbage first."""
    # Remove <head>...</head> blocks and bare HTML tags
    content = re.sub(r'<head>.*?</head>', '', content, flags=re.DOTALL | re.IGNORECASE)
    content = re.sub(r'<[^>]+>', '', content)
    # Strip <scp>...</scp> inside field values
    content = re.sub(r'<scp>(.*?)</scp>', r'\1', content, flags=re.IGNORECASE)
    return parse_bib(content)

# ---------------------------------------------------------------------------
# Text normalisation (for key generation and matching — never touches output)
# ---------------------------------------------------------------------------

def strip_latex(s):
    """Convert LaTeX accent commands to base ASCII — for analysis only, not for output."""
    # {\textXXX} macros (e.g. \textquoteright) — must come before generic rules
    s = re.sub(r'\{\\text[a-zA-Z]+\}', '', s)
    # {\v{S}} → S
    s = re.sub(r'\{\\[a-zA-Z`\'"^~.=]\{([a-zA-Z])\}\}', r'\1', s)
    # {\"u} → u
    s = re.sub(r'\{\\[`\'"^~.=]([a-zA-Z])\}', r'\1', s)
    # {\ss} etc → last letter
    s = re.sub(r'\{\\([a-zA-Z]+)\}', lambda m: m.group(1)[-1], s)
    # Remove remaining braces/backslashes
    s = re.sub(r'[{}\\]', '', s)
    # Normalize Unicode (ș→s, ü→u, ý→y, etc.)
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode('ascii')
    return s


def normalize_doi(doi):
    """Normalize a DOI string for comparison."""
    if not doi:
        return ''
    doi = doi.lower().strip()
    for prefix in ('https://doi.org/', 'http://doi.org/',
                   'http://dx.doi.org/', 'https://dx.doi.org/'):
        if doi.startswith(prefix):
            doi = doi[len(prefix):]
    return doi


def normalize_title_for_match(title):
    """Normalize a title for fuzzy matching (not used in output)."""
    # Convert Unicode hyphens/dashes to ASCII hyphen BEFORE strip_latex
    # (strip_latex's NFKD+ascii encode would otherwise silently drop them)
    title = re.sub(r'[\u2010-\u2015\u2212]', '-', title)
    clean = strip_latex(title)
    # Normalize remaining hyphens to spaces
    clean = re.sub(r'-', ' ', clean)
    # Strip digits (year refs like "(1999)" differ only in spacing)
    clean = re.sub(r'\d+', '', clean)
    clean = re.sub(r'[^\w\s]', '', clean.lower())
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean


def title_jaccard(norm1, norm2):
    """Word-level Jaccard similarity between two normalized titles."""
    w1 = set(norm1.split())
    w2 = set(norm2.split())
    if not w1 or not w2:
        return 0.0
    return len(w1 & w2) / len(w1 | w2)

# ---------------------------------------------------------------------------
# Author normalisation
# ---------------------------------------------------------------------------

def brace_split(name):
    """Split name on spaces, treating {brace groups} as atomic tokens.
    This ensures '{\v S}lipogor' stays as one token rather than splitting
    on the space inside the LaTeX accent command."""
    tokens = []
    current = []
    depth = 0
    for ch in name:
        if ch == '{':
            depth += 1
            current.append(ch)
        elif ch == '}':
            depth -= 1
            current.append(ch)
        elif ch == ' ' and depth == 0:
            if current:
                tokens.append(''.join(current))
                current = []
        else:
            current.append(ch)
    if current:
        tokens.append(''.join(current))
    return tokens


def name_to_last_first(name):
    """Convert a single author name to 'Last, First' format."""
    name = name.strip()
    # Strip trailing "et al" variants
    name = re.sub(r'\s+et\s+al\.?\s*$', '', name, flags=re.IGNORECASE).strip()
    if not name or name.lower() in ('others', 'et al', 'et al.'):
        return 'others'
    clean = strip_latex(name)
    if ',' in clean:
        return name  # Already Last, First
    # Use brace-aware split so '{\v S}lipogor' stays as one token
    words = brace_split(name)
    if len(words) <= 1:
        return name
    # Find last name start, accounting for particles (check stripped form)
    li = len(words) - 1
    if li > 0 and strip_latex(words[li-1]).lower() in PARTICLES:
        li -= 1
    last = ' '.join(words[li:])
    first = ' '.join(words[:li])
    return f"{last}, {first}" if first else name


def normalize_authors(author_str):
    """Normalize author string to 'Last, First and …' format."""
    if not author_str:
        return author_str
    if ';' in author_str:
        parts = [p.strip() for p in author_str.split(';')]
    elif re.search(r'\s+and\s+', author_str, re.IGNORECASE):
        parts = re.split(r'\s+and\s+', author_str, flags=re.IGNORECASE)
    else:
        fc = author_str.find(',')
        if fc > 0 and ' ' in author_str[:fc]:
            parts = [p.strip() for p in author_str.split(',')]
        else:
            return author_str
    normalized = [name_to_last_first(p) for p in parts if p.strip()]
    return ' and '.join(normalized)

# ---------------------------------------------------------------------------
# Status normalisation
# ---------------------------------------------------------------------------

STATUS_MAP = [
    (['in preparation', 'in prep'],           'in preparation'),
    (['in revision'],                           'in revision'),
    (['in principle accept', 'ipa'],           'IPA'),
    (['stage 1 '],                              'stage 1 registered report'),
    (['stage 2'],                               'stage 2 registered report'),
    (['submitted', 'under review'],            'under review'),
    (['preregistration', 'pre-registration'], 'preregistration'),
    (['preprint'],                              'preprint'),
]

STATUS_CANONICAL = {s for _, s in STATUS_MAP} | {'IPA'}


def normalize_status(entry):
    note = entry['fields'].get('note', '').strip()
    publisher = entry['fields'].get('publisher', '').strip()
    if publisher.lower() == 'submitted':
        entry['fields']['publisher'] = ''
        if not note:
            note = 'submitted'
    if not note:
        return entry
    nl = note.lower()
    for triggers, canonical in STATUS_MAP:
        if any(t in nl for t in triggers):
            entry['fields']['note'] = canonical
            return entry
    return entry

# ---------------------------------------------------------------------------
# Citation key generation
# ---------------------------------------------------------------------------

def first_author_last(author_str):
    parts = re.split(r'\s+and\s+', author_str, flags=re.IGNORECASE)
    first = parts[0].strip()
    clean = strip_latex(first)
    if ',' in clean:
        last = clean.split(',')[0].strip()
    else:
        words = clean.split()
        li = len(words) - 1
        if li > 0 and words[li-1].lower() in PARTICLES:
            li -= 1
        last = words[li] if words else 'unknown'
    return re.sub(r'[^a-z]', '', last.lower())


def first_substantive_word(title):
    clean = strip_latex(title)
    clean = re.sub(r'[^\w\s]', ' ', clean)
    for word in clean.split():
        w = re.sub(r'[^a-zA-Z0-9]', '', word).lower()
        if len(w) > 1 and not w.isdigit() and w not in STOP_WORDS:
            return w
    return 'untitled'


def make_key(entry):
    author = entry['fields'].get('author', '')
    year   = entry['fields'].get('year', '0000')
    title  = entry['fields'].get('title', '')
    return f"{first_author_last(author)}{year}{first_substantive_word(title)}"

# ---------------------------------------------------------------------------
# Merge helpers
# ---------------------------------------------------------------------------

def count_pub_fields(entry):
    """Score how 'published' an entry is."""
    f = entry['fields']
    score = 0
    doi = (f.get('doi', '') + f.get('url', '')).lower()
    if f.get('journal') or f.get('booktitle'):
        score += 2
    if f.get('volume'):
        score += 1
    if f.get('pages'):
        score += 1
    # Penalise OSF/preprint DOIs
    if f.get('doi') and not any(x in doi for x in ('osf.io', 'preprint', 'psyarxiv')):
        score += 2
    return score


def is_preprint_doi(doi_str, url_str=''):
    combined = (doi_str + url_str).lower()
    return any(x in combined for x in ('osf.io', 'psyarxiv', 'preprints', 'biorxiv', 'medrxiv'))


def merge_base_entries(base, extra):
    """Merge extra into base for ingmar/inProgress merging (keep richer fields)."""
    result = deepcopy(base)
    for field, value in extra['fields'].items():
        existing = result['fields'].get(field, '')
        if field == 'date-added':
            if value and (not existing or value < existing):
                result['fields'][field] = value
                if field not in result['order']:
                    result['order'].append(field)
        elif field == 'date-modified':
            if value and (not existing or value > existing):
                result['fields'][field] = value
                if field not in result['order']:
                    result['order'].append(field)
        else:
            if value and len(value) > len(existing):
                result['fields'][field] = value
                if field not in result['order']:
                    result['order'].append(field)
    return result


def update_with_published(existing, published, preprint_doi=None):
    """
    Replace an in-progress combined.bib entry with the published version.
    Keeps the existing citation key. Adds preprint DOI to note if provided.
    """
    result = deepcopy(existing)
    result['type'] = published['type']

    import_fields = ['journal', 'booktitle', 'volume', 'number', 'pages',
                     'doi', 'url', 'publisher', 'editor', 'organization']
    for field in import_fields:
        val = published['fields'].get(field, '').strip()
        if val:
            result['fields'][field] = val
            if field not in result['order']:
                result['order'].append(field)

    # Update year only for entries that were in-progress (had a status note);
    # for already-published entries keep the existing year (works.bib export years can be wrong)
    current_note_lower = existing['fields'].get('note', '').strip().lower()
    was_in_progress = current_note_lower in {s.lower() for s in STATUS_CANONICAL}
    if was_in_progress:
        pub_yr = int(published['fields'].get('year', 0) or 0)
        ex_yr  = int(existing['fields'].get('year', 0) or 0)
        if pub_yr >= ex_yr:
            result['fields']['year'] = str(pub_yr)

    # Update author if published version has fuller names
    pub_author = published['fields'].get('author', '').strip()
    ex_author = result['fields'].get('author', '').strip()
    if pub_author and len(pub_author) > len(ex_author):
        result['fields']['author'] = pub_author

    # Clear status note from existing entry
    current_note = result['fields'].get('note', '').strip()
    if current_note.lower() in {s.lower() for s in STATUS_CANONICAL}:
        result['fields']['note'] = ''

    # Add preprint DOI to note
    if preprint_doi:
        result['fields']['note'] = f'preprint: https://doi.org/{preprint_doi}'
        if 'note' not in result['order']:
            result['order'].append('note')

    return result

# ---------------------------------------------------------------------------
# works.bib deduplication
# ---------------------------------------------------------------------------

def dedup_within_works(entries):
    """
    Dedup works.bib by normalized title.
    Returns (best_entries_list, preprint_doi_map)
    preprint_doi_map: normalized_title -> best preprint DOI string
    """
    groups = defaultdict(list)
    for e in entries:
        title = e['fields'].get('title', '')
        nt = normalize_title_for_match(title)
        if nt:
            groups[nt].append(e)
        else:
            groups[e['key']].append(e)  # no title: use key

    best_entries = []
    preprint_doi_map = {}

    for nt, group in groups.items():
        if len(group) == 1:
            best_entries.append(group[0])
            continue

        # Sort by publication score descending
        group.sort(key=count_pub_fields, reverse=True)
        best = group[0]

        # Collect preprint DOIs from lower-ranked versions
        pdois = []
        for e in group[1:]:
            doi = e['fields'].get('doi', '').strip()
            url = e['fields'].get('url', '').strip()
            d = normalize_doi(doi) or normalize_doi(url)
            if d and is_preprint_doi(doi, url):
                pdois.append(d)

        if pdois:
            preprint_doi_map[nt] = pdois[0]  # keep most relevant one

        best_entries.append(best)

    return best_entries, preprint_doi_map

# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

FIELD_ORDER = [
    'author', 'title', 'year', 'journal', 'booktitle', 'volume', 'number',
    'pages', 'publisher', 'institution', 'school', 'editor', 'organization',
    'doi', 'url', 'note', 'date-added', 'date-modified',
]


def format_entry(entry):
    lines = [f"@{entry['type']}{{{entry['key']},"]
    seen = set()
    ordered = []
    for f in FIELD_ORDER:
        if f in entry['fields']:
            ordered.append(f)
            seen.add(f)
    for f in entry['order']:
        if f not in seen and f in entry['fields'] and f not in SKIP_FIELDS:
            ordered.append(f)
            seen.add(f)
    skip_prefixes = ('bdsk-url',)
    rows = []
    for f in ordered:
        if any(f.startswith(p) for p in skip_prefixes):
            continue
        if f in SKIP_FIELDS:
            continue
        v = entry['fields'].get(f, '').strip()
        if v:
            rows.append(f"\t{f} = {{{v}}},")
    if rows:
        rows[-1] = rows[-1].rstrip(',')
    lines.extend(rows)
    lines.append("}")
    return '\n'.join(lines)

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    # --- Phase 1: merge ingmar.bib + ingmarInProgress.bib ---
    with open(f'{BASE_DIR}/ingmar.bib', encoding='utf-8') as f:
        e1 = parse_bib(f.read())
    with open(f'{BASE_DIR}/ingmarInProgress.bib', encoding='utf-8') as f:
        e2 = parse_bib(f.read())

    print(f"ingmar.bib:           {len(e1)} entries")
    print(f"ingmarInProgress.bib: {len(e2)} entries")

    merged = {e['key']: e for e in e1}
    for e in e2:
        if e['key'] in merged:
            merged[e['key']] = merge_base_entries(merged[e['key']], e)
        else:
            merged[e['key']] = e

    print(f"After ingmar dedup:   {len(merged)} entries")

    # Normalize ingmar entries
    for key in list(merged.keys()):
        e = merged[key]
        e = normalize_status(e)
        if 'author' in e['fields']:
            e['fields']['author'] = normalize_authors(e['fields']['author'])
        merged[key] = e

    # --- Phase 2: parse works.bib ---
    with open(f'{BASE_DIR}/works.bib', encoding='utf-8') as f:
        works_raw = parse_works_bib(f.read())

    print(f"works.bib raw:        {len(works_raw)} entries")

    # Drop SKIP_FIELDS from works entries
    for e in works_raw:
        for f in list(e['fields'].keys()):
            if f in SKIP_FIELDS:
                del e['fields'][f]
                if f in e['order']:
                    e['order'].remove(f)

    # --- Phase 3: dedup within works.bib ---
    works_deduped, preprint_doi_map = dedup_within_works(works_raw)
    print(f"works.bib after dedup: {len(works_deduped)} entries")

    # Dedup again by original works.bib key (same key, different titles → keep highest score)
    by_key = {}
    for e in works_deduped:
        k = e['key']
        if k not in by_key or count_pub_fields(e) > count_pub_fields(by_key[k]):
            by_key[k] = e
    works_deduped = list(by_key.values())
    print(f"works.bib after key-dedup: {len(works_deduped)} entries")

    # Normalize works entries
    for e in works_deduped:
        if 'author' in e['fields']:
            e['fields']['author'] = normalize_authors(e['fields']['author'])
        # works.bib entries that are just preprints get status note
        doi = e['fields'].get('doi', '')
        pub = e['fields'].get('publisher', '')
        if is_preprint_doi(doi) or pub.lower() in ('center for open science', 'psyarxiv', 'osf'):
            if not e['fields'].get('journal') and not e['fields'].get('volume'):
                if not e['fields'].get('note'):
                    e['fields']['note'] = 'preprint'

    # --- Phase 4: match works entries against existing ---
    # Build lookup indices for combined entries
    doi_index = {}    # normalized_doi -> original_key
    title_index = {}  # normalized_title -> original_key

    for key, e in merged.items():
        doi = normalize_doi(e['fields'].get('doi', ''))
        if doi:
            doi_index[doi] = key
        nt = normalize_title_for_match(e['fields'].get('title', ''))
        if nt:
            title_index[nt] = key

    added_new = 0
    updated = 0
    skipped_already_there = 0

    for we in works_deduped:
        w_doi = normalize_doi(we['fields'].get('doi', ''))
        w_title = normalize_title_for_match(we['fields'].get('title', ''))
        w_score = count_pub_fields(we)
        preprint_doi = preprint_doi_map.get(w_title)

        # Find match: DOI exact → title exact → title Jaccard similarity
        match_key = None
        if w_doi and w_doi in doi_index:
            match_key = doi_index[w_doi]
        elif w_title and w_title in title_index:
            match_key = title_index[w_title]
        else:
            # Fuzzy title match: find best Jaccard similarity >= 0.80
            best_score = 0.0
            best_key = None
            for idx_title, idx_key in title_index.items():
                j = title_jaccard(w_title, idx_title)
                if j > best_score:
                    best_score = j
                    best_key = idx_key
            if best_score >= 0.72:
                match_key = best_key

        if match_key:
            existing = merged[match_key]
            ex_score = count_pub_fields(existing)
            if w_score > ex_score:
                merged[match_key] = update_with_published(existing, we, preprint_doi)
                updated += 1
                print(f"  UPDATED: {match_key} (score {ex_score} → {w_score})")
            else:
                skipped_already_there += 1
        else:
            # New entry — add it
            we_copy = deepcopy(we)
            new_key = make_key(we_copy)
            we_copy['key'] = new_key  # temporary; will be finalised below
            # Add preprint DOI to note if this entry itself is preprint but has related preprint
            if preprint_doi and not is_preprint_doi(we['fields'].get('doi', '')):
                we_copy['fields']['note'] = f'preprint: https://doi.org/{preprint_doi}'
            # Store with a temporary unique key to avoid clashes
            temp_key = f"__new__{we['key']}"
            merged[temp_key] = we_copy
            added_new += 1
            print(f"  NEW:     {new_key}  (from {we['key']})")

    print(f"\nworks.bib: {updated} updated, {added_new} new, {skipped_already_there} already covered")
    print(f"Total before key assignment: {len(merged)}")

    entries = list(merged.values())

    # --- Phase 5: generate final citation keys ---
    raw_keys = [make_key(e) for e in entries]
    from collections import Counter
    counts = Counter(raw_keys)
    suffix_tracker = {}
    final_keys = []
    for rk in raw_keys:
        if counts[rk] == 1:
            final_keys.append(rk)
        else:
            n = suffix_tracker.get(rk, 0)
            suffix_tracker[rk] = n + 1
            final_keys.append(rk if n == 0 else rk + chr(ord('a') + n))

    # Report key changes (from original ingmar.bib keys only)
    ingmar_keys = {e['key'] for e in e1}
    changes = []
    for e, old_key, new_key in zip(entries, [e['key'] for e in entries], final_keys):
        if old_key != new_key and old_key in ingmar_keys:
            changes.append((old_key, new_key))
        e['key'] = new_key

    # Sort: year descending, then key ascending
    entries.sort(key=lambda e: (-int(e['fields'].get('year', 0) or 0), e['key']))

    # --- Phase 6: write ---
    header = """\
%% This BibTeX bibliography file was created using BibDesk.
%% https://bibdesk.sourceforge.io/

%% Combined from ingmar.bib, ingmarInProgress.bib, and works.bib
%% Saved with string encoding Unicode (UTF-8)

"""
    body = '\n\n'.join(format_entry(e) for e in entries)
    out = f'{BASE_DIR}/combined.bib'
    with open(out, 'w', encoding='utf-8') as f:
        f.write(header + body + '\n')

    print(f"\nWritten {len(entries)} entries to {out}")
    print(f"\nCitation key changes from ingmar.bib ({len(changes)}):")
    for old, new in sorted(changes):
        print(f"  {old:45s} -> {new}")

    from collections import Counter as C
    dups = [k for k, n in C(final_keys).items() if n > 1]
    if dups:
        print(f"\nWARNING: duplicate keys: {dups}")
    else:
        print("\nNo duplicate keys.")


if __name__ == '__main__':
    main()
