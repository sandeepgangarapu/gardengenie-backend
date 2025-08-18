# FRUIT TREES - BASIC INFO PROMPT
FRUIT_TREES_BASIC_INFO_PROMPT = """
Act as a Zone-Aware Master Gardener providing basic information for fruit trees.

**Input Information:**
*   **Plant Name:** {plant_name}
*   **User USDA Hardiness Zone:** {user_zone}
*   **Plant Group:** {plant_group}

**Generate basic plant information in JSON format:**

```json
{{
  "plantName": "[Corrected Common Name]",
  "description": "[Brief description of the fruit tree and its fruit]",
  "type": "Perennial",
  "seasonality": null,
  "zoneSuitability": "[match OR close OR far]",
  "requirements": {{
    "sun": "[Full Sun OR Partial Shade OR Full Shade]",
    "water": "[Deep weekly OR Consistent moisture OR Moderate]",
    "soil": "[Well-draining, fertile OR Sandy loam OR Rich, organic]",
    "ph": "[6.0-7.0 OR 6.5-7.5 OR Specific range]",
    "spacing": "[Tree spacing requirements - e.g., 15-20 feet apart]",
    "pollination": "[Self-fertile OR Needs pollinator OR Cross-pollination helpful]",
    "rootstock": "[Standard OR Semi-dwarf OR Dwarf OR Variety-specific]"
  }}
}}
```

**Instructions:**
• Keep `requirements` values extremely concise (1–3 words or compact ranges). No sentences.
• Focus only on basic plant characteristics and growing requirements.
"""

# FRUIT TREES - PLANTING PROMPT
FRUIT_TREES_PLANTING_PROMPT = """
Act as a Zone-Aware Master Gardener providing planting guidance for fruit trees.

**Input Information:**
*   **Plant Name:** {plant_name}
*   **User USDA Hardiness Zone:** {user_zone}
*   **Plant Group:** {plant_group}

**Generate planting instructions in JSON format:**

```json
{{
  "seedStartingMonth": null,
  "plantingMonth": "[Month(s) or range for planting; e.g., Mar–Apr for bare-root or Oct–Nov in mild climates]",
  "seed_starting": [],
  "planting": [
    {{
      "step": "[Specific tree planting action]",
      "tip": "[Helpful hint about hole preparation, root handling, etc.]"
    }}
  ]
}}
```

**Instructions:**
• Use local frost dates and growing season for timing.
• Do not include "Zone" or phrases like "in Zone {user_zone}" anywhere.
• Address pollination requirements and compatible varieties for the region.
"""

# FRUIT TREES - CARE INSTRUCTIONS PROMPT
FRUIT_TREES_CARE_PROMPT = """
Act as a Zone-Aware Master Gardener providing ongoing care instructions for fruit trees.

**Input Information:**
*   **Plant Name:** {plant_name}
*   **User USDA Hardiness Zone:** {user_zone}
*   **Plant Group:** {plant_group}

**Generate care instructions organized by priority in JSON format:**

```json
{{
  "care_plan": {{
    "must_do": [
      {{ "text": "[Essential tree care and maintenance tasks]", "when": "[Season-appropriate timing]" }}
    ],
    "good_to_do": [
      {{ "text": "[Beneficial maintenance for tree health]", "when": "[Optimal timing]" }}
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
• Include pruning guidance, harvest timing, and storage techniques for the fruit type.
• Include integrated pest and disease management for fruit production.
• Organize tasks by priority rather than season. Keep 1–8 total tasks across all priority levels.
"""