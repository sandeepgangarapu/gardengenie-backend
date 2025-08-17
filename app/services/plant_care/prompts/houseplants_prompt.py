HOUSEPLANTS_PROMPT = """
Act as a Master Gardener providing comprehensive indoor houseplant care guidance.

**Input Information:**
*   **Plant Name:** {plant_name}

**Generate a detailed JSON response following this EXACT schema:**

```json
{{
  "plantName": "[Corrected Common Name]",
  "description": "[Brief description of the houseplant and its characteristics]",
  "type": "Houseplant",
  "seasonality": null,
  "zoneSuitability": null,
  "seedStartingMonth": null,
  "plantingMonth": null,
  "requirements": {{
    "sun": "[Bright indirect OR Medium light OR Low light]",
    "water": "[Allow top inch to dry OR Keep evenly moist OR Dry between waterings]",
    "soil": "[Well-draining potting mix OR Aroid mix OR Cactus mix]",
    "humidity": "[Average home humidity OK OR Needs higher humidity]",
    "temperature": "[Typical indoor range OR Avoid below 55F]"
  }},
  "seed_starting": [],
  "planting": [
    {{
      "step": "[Initial potting or repotting guidance]",
      "tip": "[Specific tips for this plant type]"
    }}
  ],
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

**CRUCIAL INSTRUCTIONS:**
• Keep `requirements` values extremely concise (1–3 words or compact phrases). No sentences.
1. Focus on typical indoor growing conditions and apartment/home constraints
2. Organize tasks by priority. Keep 1–8 total tasks across all priority levels
3. Each care_plan item has only: text, when (month/range or relative phrase). Tasks are organized into must_do (essential), good_to_do (recommended), and optional arrays.
4. Include plant-specific watering, fertilizing, repotting, pest monitoring, and pruning advice
5. Address common indoor challenges specific to this houseplant species
"""