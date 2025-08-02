HOUSEPLANTS_PROMPT = """
Act as a Zone-Aware Master Gardener providing comprehensive indoor plant care guidance.

**Plant Name:** {plant_name}
**Context:** Indoor houseplant care with seasonal awareness

**Generate a detailed JSON response following this EXACT schema:**

```json
{{
  "plantName": "[Corrected Common Name]",
  "description": "[Brief description of the houseplant and its characteristics]",
  "type": "[Annual OR Perennial]",
  "seasonality": null,
  "zoneSuitability": null,
  "requirements": {{
    "light": "[Bright Light OR Medium Light OR Low Light]",
    "water": "[Deep weekly OR Light frequent OR Allow to dry between waterings]",
    "humidity": "[High (60%+) OR Medium (40-60%) OR Low (30-40%)]",
    "temperature": "[65-75°F OR 60-70°F OR 70-80°F]",
    "soil": "[Well-draining potting mix OR Succulent mix OR Specific requirements]",
    "fertilizer": "[Monthly liquid OR Slow-release OR Minimal]"
  }},
  "seed_starting": [],
  "planting": [],
  "care_plan": [
    {{
      "task": "[Specific care task - e.g., 'Increase watering frequency']",
      "description": "[Detailed explanation of how and why to perform this task]",
      "priority": "[critical OR important OR beneficial]",
      "timing": {{
        "type": "seasonal",
        "season": "spring",
        "months": ["March", "April", "May"]
      }},
      "frequency": "[Weekly OR Bi-weekly OR Monthly OR As needed]",
      "tips": "[Helpful tip or warning about this task]"
    }},
    {{
      "task": "[Another care task - e.g., 'Monitor for pest activity']",
      "description": "[Detailed explanation]",
      "priority": "[critical OR important OR beneficial]",
      "timing": {{
        "type": "recurring",
        "frequency": "monthly",
        "year_round": true
      }},
      "frequency": "Monthly",
      "tips": "[Helpful tip]"
    }}
  ]
}}
```

**CRUCIAL INSTRUCTIONS:**
1. Create multiple, distinct task objects in care_plan - do not combine actions
2. Include tasks for: watering adjustments, fertilizing, repotting, pest monitoring, pruning, humidity management
3. Provide comprehensive, step-by-step guidance in descriptions
4. Use structured timing objects with clear seasonal or recurring patterns
5. Include practical tips for apartment/home growing conditions
6. Address common indoor plant challenges specific to this species
"""