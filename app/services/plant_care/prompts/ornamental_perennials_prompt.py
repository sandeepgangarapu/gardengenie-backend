# ORNAMENTAL PERENNIALS - BASIC INFO PROMPT
ORNAMENTAL_PERENNIALS_BASIC_INFO_PROMPT = """
Act as a Zone-Aware Master Gardener providing basic information for ornamental perennials.

**Input Information:**
*   **Plant Name:** {plant_name}
*   **User USDA Hardiness Zone:** {user_zone}
*   **Plant Group:** {plant_group}

**Generate basic plant information in JSON format:**

```json
{{
  "plantName": "[Corrected Common Name]",
  "description": "[Brief description of the ornamental plant and its features]",
  "type": "Perennial",
  "seasonality": null,
  "zoneSuitability": "[match OR close OR far]",
  "requirements": {{
    "sun": "[Full Sun OR Partial Shade OR Full Shade]",
    "water": "[Deep weekly OR Consistent moisture OR Drought tolerant]",
    "soil": "[Well-draining, fertile OR Sandy loam OR Rich, organic]",
    "ph": "[6.0-7.0 OR 6.5-7.5 OR Specific range]",
    "spacing": "[Plant spacing requirements - e.g., 18-24 inches apart]",
    "rowSpacing": "[Row spacing distance - e.g., 24-30 inches apart OR N/A for naturalized planting]",
    "bloomTime": "[Spring OR Summer OR Fall OR Multiple seasons]",
    "matureSize": "[Height x Width - e.g., 2-3 feet tall, 2 feet wide]"
  }}
}}
```

**Instructions:**
• Keep `requirements` values extremely concise (1–3 words or compact ranges). No sentences.
• Focus only on basic plant characteristics and growing requirements.
"""

# ORNAMENTAL PERENNIALS - PLANTING PROMPT
ORNAMENTAL_PERENNIALS_PLANTING_PROMPT = """
Act as a Zone-Aware Master Gardener providing planting guidance for ornamental perennials.

**Input Information:**
*   **Plant Name:** {plant_name}
*   **User USDA Hardiness Zone:** {user_zone}
*   **Plant Group:** {plant_group}

**Generate planting instructions in JSON format:**

```json
{{
  "seedStartingMonth": null,
  "plantingMonth": "[Month(s) or range for planting/division; e.g., Apr–May or Sep–Oct]",
  "seed_starting": [],
  "planting": [
    {{
      "step": "[Specific perennial planting action]",
      "tip": "[Helpful hint about soil preparation, depth, spacing, etc.]"
    }}
  ]
}}
```

**Instructions:**
• Use local climate patterns for timing.
• Do not include "Zone" or phrases like "in Zone {user_zone}" anywhere.
• Provide concise month names/ranges only for timing fields.
• Address both establishment (first year) and ongoing maintenance.
• Provide division and propagation timing appropriate for the region.
"""

# ORNAMENTAL PERENNIALS - CARE INSTRUCTIONS PROMPT
ORNAMENTAL_PERENNIALS_CARE_PROMPT = """
Act as a Zone-Aware Master Gardener providing ongoing care instructions for ornamental perennials.

**Input Information:**
*   **Plant Name:** {plant_name}
*   **User USDA Hardiness Zone:** {user_zone}
*   **Plant Group:** {plant_group}

**Generate care instructions organized by priority in JSON format:**

```json
{{
  "care_plan": {{
    "must_do": [
      {{ "text": "[Essential seasonal care tasks]", "when": "[Season-appropriate timing]" }}
    ],
    "good_to_do": [
      {{ "text": "[Beneficial maintenance for plant health]", "when": "[Optimal timing]" }}
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
• Cover bloom care, pruning, deadheading, and division timing.
• Include zone-specific challenges (heat, cold, humidity, pests).
• Organize tasks by priority rather than season. Keep 1–8 total tasks across all priority levels.
"""