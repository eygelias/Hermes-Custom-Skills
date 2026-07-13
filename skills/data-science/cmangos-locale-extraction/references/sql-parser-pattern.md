# SQL Parser for CMaNGOS OtherLocales.sql

## Problem
The `OtherLocales.sql` file is 45.6 MB with multiple INSERT statements per table. Simple regex parsing fails because:
1. Multiple INSERT blocks per table (5 for creatures, 29 for quests)
2. Escaped quotes `\'` in strings
3. Nested parentheses in values

## Working Parser Design (v5)

### Step 1: Find all INSERT blocks
```python
search_str = f"INSERT INTO `{table_name}` VALUES "
pos = 0
while True:
    idx = sql_text.find(search_str, pos)
    if idx < 0:
        break
    start = idx + len(search_str)
    end = sql_text.find(";", start)
    values_block = sql_text[start:end]
    # Parse tuples in this block
    pos = end + 1
```

### Step 2: Parse tuples with state tracking
```python
i = 0
n = len(values_block)
while i < n:
    ch = values_block[i]
    if ch == '(':
        # Start tuple - track paren depth and string state
        values = []
        current = ""
        in_string = False
        paren_depth = 1
        i += 1
        while i < n and paren_depth > 0:
            ch = values_block[i]
            if in_string:
                if ch == '\\':
                    i += 2; continue  # Skip escaped char
                if ch == "'":
                    if i+1 < n and values_block[i+1] == "'":
                        current += "'"; i += 2; continue  # Escaped quote ''
                    in_string = False; i += 1; continue
                current += ch; i += 1; continue
            else:
                if ch == "'":
                    in_string = True; i += 1; continue
                if ch == ',':
                    values.append(current); current = ""; i += 1; continue
                if ch == '(':
                    paren_depth += 1; i += 1; continue
                if ch == ')':
                    paren_depth -= 1
                    if paren_depth == 0:
                        values.append(current)
                        # Process this tuple
                    i += 1; continue
                current += ch; i += 1; continue
    i += 1
```

### Step 3: Extract locale-specific name
```python
LOCALE_NAME_COL = {
    "koKR": 1, "frFR": 2, "deDE": 3, "zhCN": 4, "zhTW": 5,
    "esES": 6, "esMX": 7, "ptBR": 8,
}

# In tuple processing:
if len(values) > name_col:
    entry_id = int(values[0])
    name = values[name_col].strip()
    if name and not name.startswith('[UNUSED]') and not name.startswith('[INUTILISÉ]'):
        result[str(entry_id)] = name
```

## Common Failures
- **Regex `INSERT INTO.*VALUES`**: Fails on multi-line INSERT or nested parens
- **Simple split on `,`**: Fails on commas inside quoted strings
- **Only processing first INSERT**: Misses data in subsequent INSERT blocks
- **Not handling `\'`**: Corrupts NPC names with apostrophes
