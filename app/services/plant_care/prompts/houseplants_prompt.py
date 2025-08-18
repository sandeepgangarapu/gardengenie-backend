# HOUSEPLANTS - BASIC INFO PROMPT
HOUSEPLANTS_BASIC_INFO_PROMPT = """
Act as a Master Gardener providing basic information for houseplants.

**Input Information:**
*   **Plant Name:** {plant_name}

**Generate basic plant information in JSON format:**

```json
{{
  "plantName": "[Corrected Common Name]",
  "description": "[Brief description of the houseplant and its characteristics]",
  "type": "Houseplant",
  "seasonality": null,
  "zoneSuitability": null,
  "requirements": {{
    "sun": "[Bright indirect OR Medium light OR Low light]",
    "water": "[Allow top inch to dry OR Keep evenly moist OR Dry between waterings]",
    "soil": "[Well-draining potting mix OR Aroid mix OR Cactus mix]",
    "humidity": "[Average home humidity OK OR Needs higher humidity]",
    "temperature": "[Typical indoor range OR Avoid below 55F]"
  }}
}}
```

**Instructions:**
• Keep `requirements` values extremely concise (1–3 words or compact phrases). No sentences.
• Focus on typical indoor growing conditions and apartment/home constraints.
"""

# HOUSEPLANTS - PLANTING PROMPT
HOUSEPLANTS_PLANTING_PROMPT = """
Act as a Master Gardener providing initial setup guidance for houseplants.

**Input Information:**
*   **Plant Name:** {plant_name}

**Generate initial potting instructions in JSON format:**

```json
{{
  "seedStartingMonth": null,
  "plantingMonth": null,
  "seed_starting": [],
  "planting": [
    {{
      "step": "[Initial potting or repotting guidance]",
      "tip": "[Specific tips for this plant type]"
    }}
  ]
}}
```

**Instructions:**
• Focus on initial setup, potting, and repotting guidance.
• Address plant-specific potting requirements and container needs.
"""

# HOUSEPLANTS - CARE INSTRUCTIONS PROMPT
HOUSEPLANTS_CARE_PROMPT = """
Act as a Master Gardener providing ongoing care instructions for houseplants.

**Input Information:**
*   **Plant Name:** {plant_name}

**Generate care instructions organized by priority in JSON format:**

```json
{{
  "care_plan": {{
    "must_do": [
      {{ "text": "[Essential watering requirements for this plant]", "when": "[Timing/frequency]" }}
    ],
    "good_to_do": [
      {{ "text": "[Beneficial maintenance tasks]", "when": "[When to perform]" }}
    ],
    "optional": []
  }}
}}
```

**Instructions:**
• Each care_plan item has only: text, when (month/range or relative phrase).
• Tasks are organized into must_do (essential), good_to_do (recommended), and optional arrays.
• Include plant-specific watering, fertilizing, repotting, pest monitoring, and pruning advice.
• Address common indoor challenges specific to this houseplant species.
• Organize tasks by priority. Keep 1–8 total tasks across all priority levels.
"""