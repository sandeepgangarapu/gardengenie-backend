# ANNUAL FLOWERS - BASIC INFO PROMPT
ANNUAL_FLOWERS_BASIC_INFO_PROMPT = """
Act as a Zone-Aware Master Gardener providing basic information for annual flowers.

**Input Information:**
*   **Plant Name:** {plant_name}
*   **User USDA Hardiness Zone:** {user_zone}
*   **Plant Group:** {plant_group}

**Generate basic plant information in JSON format:**

```json
{{
  "plantName": "[Corrected Common Name]",
  "description": "[Brief description of the annual flower and its characteristics]",
  "type": "Annual",
  "seasonality": "[Cool Season OR Warm Season]",
  "zoneSuitability": "[match OR close OR far]",
  "requirements": {{
    "sun": "[Full Sun OR Partial Shade OR Full Shade]",
    "water": "[Deep weekly OR Consistent moisture OR Moderate]",
    "soil": "[Well-draining, fertile OR Sandy loam OR Rich, organic]",
    "ph": "[6.0-7.0 OR 6.5-7.5 OR Specific range]",
    "spacing": "[Plant spacing requirements - e.g., 8-12 inches apart]",
    "rowSpacing": "[Row spacing distance - e.g., 12-15 inches apart OR N/A for mass planting]",
    "bloomPeriod": "[Spring through frost OR Summer months OR Specific season]",
    "daysToBloom": "[e.g., 60-80 days OR 45 days to first flowers]"
  }}
}}
```

**Instructions:**
• Keep `requirements` values extremely concise (1–3 words or compact ranges). No sentences.
• Focus only on basic plant characteristics and growing requirements.
"""

# ANNUAL FLOWERS - SEED STARTING & PLANTING PROMPT
ANNUAL_FLOWERS_PLANTING_PROMPT = """
Act as a Zone-Aware Master Gardener providing seed starting and planting guidance for annual flowers.

**Input Information:**
*   **Plant Name:** {plant_name}
*   **User USDA Hardiness Zone:** {user_zone}
*   **Plant Group:** {plant_group}

**Generate seed starting and planting instructions in JSON format:**

```json
{{
  "seedStartingMonth": "[Month(s) or range for starting seeds; e.g., Feb–Mar indoors]",
  "plantingMonth": "[Month(s) or range for transplanting/direct sowing; e.g., Apr–May after last frost]",
  "seed_starting": [
    {{
      "step": "[Specific seed starting action]",
      "tip": "[Helpful hint about germination, light requirements, etc.]"
    }}
  ],
  "planting": [
    {{
      "step": "[Specific planting action]",
      "tip": "[Helpful hint about transplanting, direct seeding, etc.]"
    }}
  ]
}}
```

**Instructions:**
• Use local frost dates and growing season for timing.
• Do not include "Zone" or phrases like "in Zone {user_zone}" anywhere.
• Provide concise month names/ranges only for timing fields.
• Include succession planting advice when relevant for continuous blooms.
• Address zone-specific challenges (heat, humidity, short seasons).
"""

# ANNUAL FLOWERS - CARE INSTRUCTIONS PROMPT
ANNUAL_FLOWERS_CARE_PROMPT = """
Act as a Zone-Aware Master Gardener providing ongoing care instructions for annual flowers.

**Input Information:**
*   **Plant Name:** {plant_name}
*   **User USDA Hardiness Zone:** {user_zone}
*   **Plant Group:** {plant_group}

**Generate care instructions organized by priority in JSON format:**

```json
{{
  "care_plan": {{
    "must_do": [
      {{ "text": "[Essential care for healthy flowering]", "when": "[Growing season timing]" }}
    ],
    "good_to_do": [
      {{ "text": "[Tasks to extend bloom period]", "when": "[During flowering]" }}
    ],
    "optional": []
  }}
}}
```

**Instructions:**
• Each care_plan item has only: text, when (month/range or relative phrase).
• Tasks are organized into must_do (essential), good_to_do (recommended), and optional arrays.
• Use local frost dates and growing season for "when" values.
• Do not include "Zone" or phrases like "in Zone {user_zone}" anywhere.
• Cover deadheading techniques for continued flower production.
• Include seed collection and saving tips if relevant to the variety.
• Focus only on post-planting maintenance tasks.
"""