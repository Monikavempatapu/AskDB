import sqlite3
import difflib
import re

class NL2SQL:
    def __init__(self, table_name, columns):
        self.table_name = table_name
        self.columns = columns

    def _match_col(self, query):
        query_lc = query.lower()
        # Try exact match
        for col in self.columns:
            if col.lower() in query_lc:
                return col
        # Fuzzy/partial match for cricket/match terms
        cricket_terms = {
            "batting": ["batting_hand", "batting style", "batting"],
            "bowling": ["bowling_skill", "bowling", "bowling style"],
            "City": ["City", "nation"],
            "player": ["playername", "name", "player name"],
            "runs": ["runs", "score"],
            "wickets": ["wickets"],
            # Match database terms:
            "city": ["city", "venue", "location"],
            "date": ["date", "match date"],
            "season": ["season", "year"],
            "team1": ["team1", "first team", "home team"],
            "team2": ["team2", "second team", "away team"],
            "winner": ["winner", "winning team"],
            "toss": ["toss_winner", "toss", "toss winner"],
            "umpire": ["umpire1", "umpire2", "umpire"],
        }
        for key, colnames in cricket_terms.items():
            for cname in colnames:
                if key in query_lc or cname in query_lc:
                    for col in self.columns:
                        if cname.replace(" ", "").lower() in col.replace("_", "").lower():
                            return col
        # Fallback: partial word match
        for col in self.columns:
            for word in query_lc.split():
                if word in col.lower():
                    return col
        return self.columns[0] if self.columns else "*"

    def _extract_value(self, query):
        # Try to extract quoted value
        quoted = re.findall(r"'([^']+)'", query)
        if quoted:
            return quoted[0]
        # Try to extract after keywords
        match = re.search(r"(from|with|is|equals|containing|named|named as|having|of|by)\s+([A-Za-z0-9\s\+\-]+)", query.lower())
        if match:
            return match.group(2).strip()
        # Fallback: last word
        return query.strip().split()[-1]

    def generate_sql(self, query):
        query_lc = query.lower()
        col = self._match_col(query)

        # Handle "more than" or "greater than"
        match = re.search(r'(more than|greater than|above|over)\s+(\d+)', query_lc)
        if match and col:
            return f"SELECT * FROM {self.table_name} WHERE {col} > {match.group(2)};"

        # Handle "less than", "below", "under"
        match = re.search(r'(less than|below|under)\s+(\d+)', query_lc)
        if match and col:
            return f"SELECT * FROM {self.table_name} WHERE {col} < {match.group(2)};"

        # Handle "between ... and ..."
        match = re.search(r'between\s+(\d+)\s+and\s+(\d+)', query_lc)
        if match and col:
            return f"SELECT * FROM {self.table_name} WHERE {col} BETWEEN {match.group(1)} AND {match.group(2)};"

        # Count queries
        if "how many" in query_lc or "count" in query_lc:
            val = self._extract_value(query)
            # If the value is numeric or quoted, add WHERE
            if col and val and (val.isdigit() or val.replace('.', '', 1).isdigit() or val.isalpha()):
                return f"SELECT COUNT(*) FROM {self.table_name} WHERE {col} = '{val}';"
            elif col:
                return f"SELECT COUNT({col}) FROM {self.table_name};"
            return f"SELECT COUNT(*) FROM {self.table_name};"

        # Sum queries
        if "sum" in query_lc:
            val = self._extract_value(query)
            if col and val and (val.isdigit() or val.replace('.', '', 1).isdigit() or val.isalpha()):
                return f"SELECT SUM({col}) FROM {self.table_name} WHERE {col} = '{val}';"
            elif col:
                return f"SELECT SUM({col}) FROM {self.table_name};"

        # Max queries
        if "maximum" in query_lc or "highest" in query_lc or "max" in query_lc:
            if col:
                return f"SELECT MAX({col}) FROM {self.table_name};"

        # Min queries
        if "minimum" in query_lc or "lowest" in query_lc or "min" in query_lc:
            if col:
                return f"SELECT MIN({col}) FROM {self.table_name};"

        # Top N queries
        match = re.search(r'(top|first)\s+(\d+)', query_lc)
        if match:
            n = match.group(2)
            order_col = col if col else self.columns[0]
            return f"SELECT * FROM {self.table_name} ORDER BY {order_col} DESC LIMIT {n};"

        # WHERE with contains/like
        if col and ("contains" in query_lc or "like" in query_lc):
            val = self._extract_value(query)
            return f"SELECT * FROM {self.table_name} WHERE {col} LIKE '%{val}%';"

        # WHERE with equals/is/with/having
        if col and ("equals" in query_lc or "is" in query_lc or "with" in query_lc or "held" in query_lc or "having" in query_lc or "from" in query_lc):
            val = self._extract_value(query)
            return f"SELECT * FROM {self.table_name} WHERE {col} = '{val}';"

        # Show all
        if "all" in query_lc or "show" in query_lc or self.table_name.lower() in query_lc:
            return f"SELECT * FROM {self.table_name};"

        # Default fallback
        return f"SELECT * FROM {self.table_name};"
