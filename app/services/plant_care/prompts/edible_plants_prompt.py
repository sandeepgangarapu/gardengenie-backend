# EDIBLE PLANTS - BASIC INFO PROMPT
EDIBLE_PLANTS_BASIC_INFO_PROMPT = """
Act as a Zone-Aware Master Gardener providing basic information for edible plants.

**Input Information:**
*   **Plant Name:** {plant_name}
*   **User USDA Hardiness Zone:** {user_zone}
*   **Plant Group:** {plant_group}

**Generate basic plant information in JSON format:**

```json
{{
  "plantName": "[Corrected Common Name]",
  "description": "[Brief description of the edible plant, its uses, and expected yields]",
  "type": "Annual",
  "seasonality": "[Cool Season OR Warm Season]",
  "zoneSuitability": "[match OR close OR far]",
  "requirements": {{
    "sun": "[Full Sun OR Partial Shade OR Full Shade]",
    "water": "[Deep weekly OR Consistent moisture OR Moderate]",
    "soil": "[Well-draining, fertile OR Sandy loam OR Rich, organic]",
    "ph": "[6.0-7.0 OR 6.5-7.5 OR Specific range]",
    "spacing": "[Plant spacing requirements - e.g., 12-18 inches apart]",
    "rowSpacing": "[Row spacing distance - e.g., 18-24 inches apart OR N/A for single plants]",
    "daysToMaturity": "[e.g., 60-80 days OR 45 days to first harvest]"
  }}
}}
```

**Instructions:**
• Keep `requirements` values extremely concise (1–3 words or compact ranges). No sentences.
• Focus only on basic plant characteristics and growing requirements.
"""

# EDIBLE PLANTS - SEED STARTING & PLANTING PROMPT  
EDIBLE_PLANTS_PLANTING_PROMPT = """
Act as a Zone-Aware Master Gardener providing seed starting and planting guidance for edible plants.

**Input Information:**
*   **Plant Name:** {plant_name}
*   **User USDA Hardiness Zone:** {user_zone}
*   **Plant Group:** {plant_group}

**Generate seed starting and planting instructions in JSON format:**

```json
{{
  "seedStartingMonth": "[Month(s) or range for starting seeds; use local frost dates, e.g., Feb–Mar indoors]",
  "plantingMonth": "[Month(s) or range for transplanting/direct sowing; e.g., Apr–May after last frost]",
  "seed_starting": [
    {{
      "step": "[Specific seed starting action]",
      "tip": "[Helpful hint or technique]"
    }}
  ],
  "planting": [
    {{
      "step": "[Specific planting action]",
      "tip": "[Helpful hint or technique]"
    }}
  ]
}}
```

**Instructions:**
• Use local frost dates and season length for timing. 
• Do not include "Zone" or phrases like "in Zone {user_zone}" anywhere.
• Provide concise month names/ranges only for timing fields.
• Include succession planting guidance where relevant.
• Address soil preparation specific to the crop and region.
"""

# EDIBLE PLANTS - CARE INSTRUCTIONS PROMPT
EDIBLE_PLANTS_CARE_PROMPT = """
Act as a Zone-Aware Master Gardener providing ongoing care instructions for edible plants.

**Input Information:**
*   **Plant Name:** {plant_name}
*   **User USDA Hardiness Zone:** {user_zone}
*   **Plant Group:** {plant_group}

**Generate care instructions organized by priority in JSON format:**

```json
{{
  "care_plan": {{
    "must_do": [
      {{ "text": "[Essential care tasks for this edible plant]", "when": "[Critical timing periods]" }}
    ],
    "good_to_do": [
      {{ "text": "[Beneficial tasks for better yields]", "when": "[Recommended timing]" }}
    ],
    "optional": []
  }}
}}
```

**Instructions:**
• Each care_plan item has only: text, when (month/range or relative phrase).
• Tasks are organized into must_do (essential), good_to_do (recommended), and optional arrays.
• Use local frost dates and season length for "when" values.
• Do not include "Zone" or phrases like "in Zone {user_zone}" anywhere.
• Include pest/disease monitoring and fertility needs specific to the crop.
• Focus only on post-planting maintenance tasks.
"""