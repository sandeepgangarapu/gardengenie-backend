# BULBS - BASIC INFO PROMPT
BULBS_BASIC_INFO_PROMPT = """
Act as a Zone-Aware Master Gardener providing basic information for bulbs.

**Input Information:**
*   **Plant Name:** {plant_name}
*   **User USDA Hardiness Zone:** {user_zone}
*   **Plant Group:** {plant_group}

**Generate basic plant information in JSON format:**

```json
{{
  "plantName": "[Corrected Common Name]",
  "description": "[Brief description of the bulb and its blooms]",
  "type": "Perennial",
  "seasonality": "[Spring-blooming OR Summer-blooming OR Fall-blooming]",
  "zoneSuitability": "[match OR close OR far]",
  "requirements": {{
    "sun": "[Full Sun OR Partial Shade OR Full Shade]",
    "water": "[During growing season only OR Minimal after dormancy OR Consistent spring moisture]",
    "soil": "[Well-draining, fertile OR Sandy, well-draining OR Rich but draining]",
    "drainage": "[Excellent drainage required OR Good drainage OR Tolerates some moisture]",
    "chilling": "[Requires cold treatment OR Pre-chilled OR Natural winter chill]",
    "plantingDepth": "[3x bulb height OR Specific depth requirement]",
    "rowSpacing": "[Row spacing distance - e.g., 6-8 inches apart OR N/A for naturalized planting]",
    "bulbType": "[True bulb OR Corm OR Tuber OR Rhizome]"
  }}
}}
```

**Instructions:**
• Keep `requirements` values extremely concise (1–3 words or compact ranges). No sentences.
• Focus only on basic plant characteristics and growing requirements.
"""

# BULBS - PLANTING PROMPT
BULBS_PLANTING_PROMPT = """
Act as a Zone-Aware Master Gardener providing planting guidance for bulbs.

**Input Information:**
*   **Plant Name:** {plant_name}
*   **User USDA Hardiness Zone:** {user_zone}
*   **Plant Group:** {plant_group}

**Generate planting instructions in JSON format:**

```json
{{
  "seedStartingMonth": null,
  "plantingMonth": "[Month(s) or range for planting bulbs; e.g., Sep–Nov for spring bulbs or Mar–Apr for summer bulbs]",
  "seed_starting": [],
  "planting": [
    {{
      "step": "[Specific bulb planting action]",
      "tip": "[Helpful hint about bulb orientation, depth, etc.]"
    }}
  ]
}}
```

**Instructions:**
• Provide exact planting timing based on soil temperature and frost dates.
• Do not include "Zone" or phrases like "in Zone {user_zone}" anywhere.
• Include pre-chilling requirements if needed for this zone.
• Address zone-specific challenges (drainage in clay soil, heat tolerance, etc.).
• Specify naturalization potential and suitable companions.
"""

# BULBS - CARE INSTRUCTIONS PROMPT
BULBS_CARE_PROMPT = """
Act as a Zone-Aware Master Gardener providing ongoing care instructions for bulbs.

**Input Information:**
*   **Plant Name:** {plant_name}
*   **User USDA Hardiness Zone:** {user_zone}
*   **Plant Group:** {plant_group}

**Generate care instructions organized by priority in JSON format:**

```json
{{
  "care_plan": {{
    "must_do": [
      {{ "text": "[Essential post-bloom care for bulb health]", "when": "[After flowering period]" }}
    ],
    "good_to_do": [
      {{ "text": "[Supporting tasks for optimal growth]", "when": "[Growing season]" }}
    ],
    "optional": []
  }}
}}
```

**Instructions:**
• Each care_plan item has only: text, when (month/range or relative phrase).
• Tasks are organized into must_do (essential), good_to_do (recommended), and optional arrays.
• Use local climate patterns for "when" values.
• Do not include "Zone" or phrases like "in Zone {user_zone}" anywhere.
• Focus only on post-plant tasks organized by priority. Keep 1–8 total tasks across all priority levels.
"""