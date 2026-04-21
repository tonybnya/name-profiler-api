"""
Script Name : search_parser.py
Description : Natural language query parser for profile search
Author : @tonybnya
"""

import re
from typing import Dict, Any, List, Tuple, Optional

# Country name variations to ISO code mapping
COUNTRY_MAPPINGS = {
    # Africa
    "nigeria": "NG",
    "ghana": "GH",
    "kenya": "KE",
    "south africa": "ZA",
    "egypt": "EG",
    "morocco": "MA",
    "ethiopia": "ET",
    "tanzania": "TZ",
    "uganda": "UG",
    "algeria": "DZ",
    "sudan": "SD",
    "angola": "AO",
    "mozambique": "MZ",
    "cameroon": "CM",
    "ivory coast": "CI",
    "cote d'ivoire": "CI",
    "madagascar": "MG",
    "niger": "NE",
    "burkina faso": "BF",
    "mali": "ML",
    "malawi": "MW",
    "zambia": "ZM",
    "senegal": "SN",
    "chad": "TD",
    "somalia": "SO",
    "zimbabwe": "ZW",
    "guinea": "GN",
    "rwanda": "RW",
    "benin": "BJ",
    "tunisia": "TN",
    "libya": "LY",
    "liberia": "LR",
    "sierra leone": "SL",
    "togolese": "TG",
    "togo": "TG",
    "central african republic": "CF",
    "mauritania": "MR",
    "eritrea": "ER",
    "gambia": "GM",
    "botswana": "BW",
    "gabon": "GA",
    "lesotho": "LS",
    "guinea-bissau": "GW",
    "equatorial guinea": "GQ",
    "mauritius": "MU",
    "eswatini": "SZ",
    "swaziland": "SZ",
    "djibouti": "DJ",
    "comoros": "KM",
    "cape verde": "CV",
    "sao tome and principe": "ST",
    "seychelles": "SC",
    "namibia": "NA",
    "congo": "CG",
    "democratic republic of congo": "CD",
    "drc": "CD",
    "burundi": "BI",
    
    # North America
    "united states": "US",
    "usa": "US",
    "america": "US",
    "canada": "CA",
    "mexico": "MX",
    
    # South America
    "brazil": "BR",
    "argentina": "AR",
    "colombia": "CO",
    "peru": "PE",
    "venezuela": "VE",
    "chile": "CL",
    "ecuador": "EC",
    "guatemala": "GT",
    "bolivia": "BO",
    "cuba": "CU",
    "haiti": "HT",
    "dominican republic": "DO",
    "honduras": "HN",
    "paraguay": "PY",
    "nicaragua": "NI",
    "el salvador": "SV",
    "costa rica": "CR",
    "panama": "PA",
    "uruguay": "UY",
    "jamaica": "JM",
    "trinidad and tobago": "TT",
    "guyana": "GY",
    "suriname": "SR",
    "barbados": "BB",
    "saint lucia": "LC",
    "grenada": "GD",
    "saint vincent and the grenadines": "VC",
    "antigua and barbuda": "AG",
    "dominica": "DM",
    "saint kitts and nevis": "KN",
    "belize": "BZ",
    "bahamas": "BS",
    
    # Europe
    "united kingdom": "GB",
    "uk": "GB",
    "britain": "GB",
    "england": "GB",
    "germany": "DE",
    "france": "FR",
    "italy": "IT",
    "spain": "ES",
    "poland": "PL",
    "romania": "RO",
    "netherlands": "NL",
    "holland": "NL",
    "belgium": "BE",
    "czech republic": "CZ",
    "czechia": "CZ",
    "greece": "GR",
    "portugal": "PT",
    "sweden": "SE",
    "hungary": "HU",
    "austria": "AT",
    "belarus": "BY",
    "switzerland": "CH",
    "bulgaria": "BG",
    "serbia": "RS",
    "denmark": "DK",
    "finland": "FI",
    "slovakia": "SK",
    "norway": "NO",
    "ireland": "IE",
    "croatia": "HR",
    "bosnia and herzegovina": "BA",
    "albania": "AL",
    "lithuania": "LT",
    "slovenia": "SI",
    "latvia": "LV",
    "estonia": "EE",
    "macedonia": "MK",
    "north macedonia": "MK",
    "moldova": "MD",
    "luxembourg": "LU",
    "malta": "MT",
    "iceland": "IS",
    "montenegro": "ME",
    "cyprus": "CY",
    "monaco": "MC",
    "liechtenstein": "LI",
    "san marino": "SM",
    "andorra": "AD",
    "vatican": "VA",
    "vatican city": "VA",
    "russia": "RU",
    "ukraine": "UA",
    "turkey": "TR",
    
    # Asia
    "china": "CN",
    "india": "IN",
    "indonesia": "ID",
    "pakistan": "PK",
    "bangladesh": "BD",
    "japan": "JP",
    "philippines": "PH",
    "vietnam": "VN",
    "turkey": "TR",
    "iran": "IR",
    "thailand": "TH",
    "myanmar": "MM",
    "burma": "MM",
    "south korea": "KR",
    "korea": "KR",
    "iraq": "IQ",
    "afghanistan": "AF",
    "saudi arabia": "SA",
    "uzbekistan": "UZ",
    "malaysia": "MY",
    "nepal": "NP",
    "yemen": "YE",
    "north korea": "KP",
    "sri lanka": "LK",
    "kazakhstan": "KZ",
    "syria": "SY",
    "cambodia": "KH",
    "jordan": "JO",
    "azerbaijan": "AZ",
    "united arab emirates": "AE",
    "uae": "AE",
    "tajikistan": "TJ",
    "israel": "IL",
    "laos": "LA",
    "lebanon": "LB",
    "kyrgyzstan": "KG",
    "turkmenistan": "TM",
    "singapore": "SG",
    "oman": "OM",
    "state of palestine": "PS",
    "palestine": "PS",
    "kuwait": "KW",
    "georgia": "GE",
    "mongolia": "MN",
    "armenia": "AM",
    "qatar": "QA",
    "bahrain": "BH",
    "east timor": "TL",
    "timor-leste": "TL",
    "brunei": "BN",
    "bhutan": "BT",
    "maldives": "MV",
    
    # Oceania
    "australia": "AU",
    "papua new guinea": "PG",
    "new zealand": "NZ",
    "fiji": "FJ",
    "solomon islands": "SB",
    "vanuatu": "VU",
    "samoa": "WS",
    "micronesia": "FM",
    "tonga": "TO",
    "kiribati": "KI",
    "palau": "PW",
    "marshall islands": "MH",
    "tuvalu": "TV",
    "nauru": "NR",
}

# Age keyword mappings
AGE_KEYWORDS = {
    "young": (16, 24),
    "child": "child",
    "children": "child",
    "teenager": "teenager",
    "teenagers": "teenager",
    "teen": "teenager",
    "teens": "teenager",
    "adult": "adult",
    "adults": "adult",
    "senior": "senior",
    "seniors": "senior",
    "elderly": "senior",
    "old": "senior",
}

# Gender synonyms
GENDER_MAPPINGS = {
    "male": "male",
    "males": "male",
    "man": "male",
    "men": "male",
    "boy": "male",
    "boys": "male",
    "female": "female",
    "females": "female",
    "woman": "female",
    "women": "female",
    "girl": "female",
    "girls": "female",
}

# Age comparators
AGE_COMPARATORS = {
    "above": "min",
    "over": "min",
    "older than": "min",
    "more than": "min",
    "greater than": "min",
    "after": "min",
    "below": "max",
    "under": "max",
    "less than": "max",
    "younger than": "max",
    "before": "max",
}


def extract_countries(query: str) -> Tuple[List[str], str]:
    """Extract country codes from query. Returns list of country codes and remaining query."""
    found_countries = []
    remaining = query.lower()
    
    # Sort by length (descending) to match longer names first
    sorted_countries = sorted(COUNTRY_MAPPINGS.keys(), key=len, reverse=True)
    
    for country_name in sorted_countries:
        if country_name in remaining:
            found_countries.append(COUNTRY_MAPPINGS[country_name])
            remaining = remaining.replace(country_name, "")
    
    return found_countries, remaining


def extract_gender(query: str) -> Tuple[Optional[str], str]:
    """Extract gender from query. Returns gender or None, and remaining query."""
    remaining = query.lower()
    found_gender = None
    
    # Check for "male and female" or "female and male" pattern
    if ("male and female" in remaining or 
        "female and male" in remaining or
        "men and women" in remaining or
        "women and men" in remaining):
        # Return None means both genders
        remaining = remaining.replace("male and female", "").replace("female and male", "")
        remaining = remaining.replace("men and women", "").replace("women and men", "")
        return None, remaining
    
    # Sort by length (descending) to match longer phrases first
    sorted_genders = sorted(GENDER_MAPPINGS.keys(), key=len, reverse=True)
    
    for gender_word in sorted_genders:
        if gender_word in remaining:
            found_gender = GENDER_MAPPINGS[gender_word]
            remaining = remaining.replace(gender_word, "")
            break
    
    return found_gender, remaining


def extract_age_group(query: str) -> Tuple[Optional[str], str]:
    """Extract age group keyword from query. Returns age group or None, and remaining query."""
    remaining = query.lower()
    found_age_group = None
    
    for keyword, group in AGE_KEYWORDS.items():
        if isinstance(group, str) and keyword in remaining:
            found_age_group = group
            remaining = remaining.replace(keyword, "")
            break
    
    return found_age_group, remaining


def extract_young_age(query: str) -> Tuple[Optional[Tuple[int, int]], str]:
    """Extract 'young' keyword which maps to age range 16-24."""
    remaining = query.lower()
    found_range = None
    
    if "young" in remaining:
        found_range = AGE_KEYWORDS["young"]  # (16, 24)
        remaining = remaining.replace("young", "")
    
    return found_range, remaining


def extract_exact_age(query: str) -> Tuple[Optional[int], str]:
    """Extract exact age like 'aged 25' or 'age 25'."""
    remaining = query.lower()
    found_age = None
    
    # Patterns: "aged 25", "age 25", "25 years old", "25 year old"
    patterns = [
        r'aged\s+(\d+)',
        r'age\s+(\d+)',
        r'(\d+)\s+years?\s+old',
        r'(\d+)\s+year\s+old',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, remaining)
        if match:
            found_age = int(match.group(1))
            remaining = re.sub(pattern, "", remaining)
            break
    
    return found_age, remaining


def extract_age_comparators(query: str) -> Tuple[Dict[str, int], str]:
    """Extract age comparators like 'above 30', 'under 50'."""
    remaining = query.lower()
    result = {}
    
    # Sort by length (descending) for longer phrases first
    sorted_comparators = sorted(AGE_COMPARATORS.keys(), key=len, reverse=True)
    
    for comparator in sorted_comparators:
        # Pattern: "comparator 30" or "comparator thirty"
        pattern = rf'{re.escape(comparator)}\s+(\d+)'
        matches = re.findall(pattern, remaining)
        
        for match in matches:
            age_val = int(match)
            comp_type = AGE_COMPARATORS[comparator]
            result[comp_type] = age_val
            remaining = re.sub(pattern, "", remaining, count=1)
    
    return result, remaining


def resolve_age_conflicts(
    age_group: Optional[str],
    young_range: Optional[Tuple[int, int]],
    exact_age: Optional[int],
    comparators: Dict[str, int]
) -> Dict[str, Any]:
    """Resolve conflicts between different age specifications."""
    result = {}
    
    # Priority: exact_age > comparators > young_range > age_group
    
    if exact_age is not None:
        # Exact age: set both min and max to that age
        result["min_age"] = exact_age
        result["max_age"] = exact_age
        return result
    
    # Build from comparators
    if "min" in comparators:
        result["min_age"] = comparators["min"]
    if "max" in comparators:
        result["max_age"] = comparators["max"]
    
    # Handle young range
    if young_range is not None:
        if "min_age" in result and "max_age" in result:
            # Intersect: young(16-24) + min_age(20) = max(20,16) to min(24,result[max])
            result["min_age"] = max(result["min_age"], young_range[0])
            result["max_age"] = min(result["max_age"], young_range[1])
        elif "min_age" in result:
            # young(16-24) + min_age(20) = 20-24
            result["min_age"] = max(result["min_age"], young_range[0])
            result["max_age"] = young_range[1]
        elif "max_age" in result:
            # young(16-24) + max_age(20) = 16-20
            result["min_age"] = young_range[0]
            result["max_age"] = min(result["max_age"], young_range[1])
        else:
            # Just young
            result["min_age"] = young_range[0]
            result["max_age"] = young_range[1]
    
    # Handle age_group
    if age_group is not None:
        age_group_ranges = {
            "child": (0, 12),
            "teenager": (13, 19),
            "adult": (20, 59),
            "senior": (60, 150),
        }
        
        if age_group in age_group_ranges:
            group_min, group_max = age_group_ranges[age_group]
            
            if "min_age" in result and "max_age" in result:
                # Intersect age_group with existing range
                result["min_age"] = max(result["min_age"], group_min)
                result["max_age"] = min(result["max_age"], group_max)
            elif "min_age" in result:
                result["min_age"] = max(result["min_age"], group_min)
                result["max_age"] = group_max
            elif "max_age" in result:
                result["min_age"] = group_min
                result["max_age"] = min(result["max_age"], group_max)
            else:
                result["age_group"] = age_group
    
    return result


def parse_search_query(query: str) -> Optional[Dict[str, Any]]:
    """
    Parse natural language query into filter parameters.
    
    Returns dict with filters or None if uninterpretable.
    
    Examples:
        "young males from nigeria" -> {"gender": "male", "min_age": 16, "max_age": 24, "country_id": ["NG"]}
        "females above 30" -> {"gender": "female", "min_age": 30}
        "people from angola" -> {"country_id": ["AO"]}
    """
    if not query or not query.strip():
        return None
    
    query = query.lower().strip()
    result = {}
    
    # Extract countries first (handle "or" between countries)
    # Check for "or" pattern in countries
    country_parts = []
    if " or " in query:
        # Split by " or " and look for countries in each part
        parts = query.split(" or ")
        for part in parts:
            countries, _ = extract_countries(part.strip())
            country_parts.extend(countries)
        
        # Also extract from full query
        all_countries, query_without_countries = extract_countries(query)
        
        # Use countries found in or-separation
        if country_parts:
            result["country_id"] = list(set(country_parts))  # Remove duplicates
        elif all_countries:
            result["country_id"] = all_countries
    else:
        countries, query_without_countries = extract_countries(query)
        if countries:
            result["country_id"] = countries
    
    # Continue with remaining processing on query without country names
    working_query = query_without_countries if 'query_without_countries' in locals() else query
    
    # Extract gender
    gender, working_query = extract_gender(working_query)
    if gender is not None:
        result["gender"] = gender
    # If gender is None, it means "male and female" or similar was found (both genders)
    # So we don't add gender filter
    
    # Extract age-related terms
    age_group, working_query = extract_age_group(working_query)
    young_range, working_query = extract_young_age(working_query)
    exact_age, working_query = extract_exact_age(working_query)
    comparators, working_query = extract_age_comparators(working_query)
    
    # Resolve age conflicts
    age_filters = resolve_age_conflicts(age_group, young_range, exact_age, comparators)
    result.update(age_filters)
    
    # Check if query is interpretable
    # A query is uninterpretable if:
    # 1. It's empty after processing
    # 2. No filters were extracted
    # 3. Contains non-meaningful words that don't map to anything
    
    # Clean up remaining query
    working_query = re.sub(r'\s+', ' ', working_query).strip()
    
    # Remove common filler words
    filler_words = {'people', 'person', 'from', 'and', 'or', 'the', 'a', 'an', 'of', 'in', 'with', 'who', 'are', 'is', 'that', 'have', 'has'}
    remaining_words = [w for w in working_query.split() if w not in filler_words]
    
    # If we have filters, it's interpretable even with some leftover words
    if result:
        return result
    
    # If no filters extracted, check if query was just filler words
    if not remaining_words or len(remaining_words) == 0:
        return {}  # Empty but valid (e.g., "people")
    
    # If there are meaningful words left that we couldn't parse
    # Query like "xyz123" or random gibberish should be uninterpretable
    if remaining_words and len(remaining_words) >= 1:
        return None  # Uninterpretable - has words we couldn't map to anything
    
    return result
