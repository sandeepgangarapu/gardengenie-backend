# SUCCULENTS - BASIC INFO PROMPT
SUCCULENTS_BASIC_INFO_PROMPT = """
Act as a Zone-Aware Master Gardener providing basic information for succulents.

**Input Information:**
*   **Plant Name:** {plant_name}
*   **User USDA Hardiness Zone:** {user_zone}
*   **Plant Group:** {plant_group}

**Generate basic plant information in JSON format:**

```json
{{
  "plantName": "[Corrected Common Name]",
  "description": "[Brief description of the succulent and its characteristics]",
  "type": "Perennial",
  "seasonality": null,
  "zoneSuitability": "[match OR close OR far]",
  "requirements": {{
    "sun": "[Full Sun OR Bright Light OR Partial Shade]",
    "water": "[Soak and dry method OR Minimal winter water OR Deep, infrequent]",
    "soil": "[Cactus/succulent mix OR Sandy, well-draining OR Fast-draining]",
    "drainage": "[Excellent drainage critical OR Good drainage OR Tolerates brief moisture]",
    "temperature": "[Cold tolerance or minimum temperature]",
    "humidity": "[Low humidity preferred OR Tolerates humidity OR Avoid high humidity]",
    "hardiness": "[Cold hardiness description]"
  }}
}}
```

**Instructions:**
• Keep `requirements` values extremely concise (1–3 words or compact phrases). No sentences.
• Focus only on basic plant characteristics and growing requirements.
"""

# SUCCULENTS - PLANTING PROMPT
SUCCULENTS_PLANTING_PROMPT = """
Act as a Zone-Aware Master Gardener providing planting guidance for succulents.

**Input Information:**
*   **Plant Name:** {plant_name}
*   **User USDA Hardiness Zone:** {user_zone}
*   **Plant Group:** {plant_group}

**Generate planting instructions in JSON format:**

```json
{{
  "seedStartingMonth": null,
  "plantingMonth": "[Month(s) or range for outdoor/container planting; e.g., Apr–May after frost or anytime indoors]",
  "seed_starting": [],
  "planting": [
    {{
      "step": "[Specific succulent planting action]",
      "tip": "[Helpful hint about soil mix, container choice, etc.]"
    }}
  ]
}}
```

**Instructions:**
• Address outdoor vs. container growing based on local hardiness conditions.
• Do not include "Zone" or phrases like "in Zone {user_zone}" anywhere.
• Provide specific winter protection needs for this climate.
• Address humidity challenges specific to the region and propagation timing.
"""

# SUCCULENTS - CARE INSTRUCTIONS PROMPT
SUCCULENTS_CARE_PROMPT = """
Act as a Zone-Aware Master Gardener providing ongoing care instructions for succulents.

**Input Information:**
*   **Plant Name:** {plant_name}
*   **User USDA Hardiness Zone:** {user_zone}
*   **Plant Group:** {plant_group}

**Generate care instructions organized by priority in JSON format:**

```json
{{
  "care_plan": {{
    "must_do": [
      {{ "text": "[Essential watering and seasonal care]", "when": "[Season-appropriate timing]" }}
    ],
    "good_to_do": [
      {{ "text": "[Beneficial maintenance tasks]", "when": "[Optimal timing for task]" }}
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
• Organize tasks by priority rather than growth stage. Keep 1–8 total tasks across all priority levels.
"""