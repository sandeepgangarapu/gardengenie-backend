PLANT_IDENTIFICATION_PROMPT = """
Analyze this image and determine if it contains a plant, tree, shrub, or any gardening-related vegetation.

Respond with a JSON object in this exact format:

{
  "is_plant": true/false,
  "common_name": "Common name of the plant" or null,
  "confidence": "high/medium/low" or null,
  "message": "Descriptive message about what you see"
}

Guidelines:
- Set "is_plant" to true only if the image clearly shows a living plant, tree, shrub, flower, or gardening vegetation
- If it's a plant, provide the most accurate common name you can identify
- Set confidence based on how certain you are of the identification:
  - "high": Very confident in the identification
  - "medium": Fairly confident but could be similar species
  - "low": Uncertain, could be multiple possibilities
- If not a plant, set common_name and confidence to null
- Always provide a helpful message describing what you observe

Examples of what counts as plants: houseplants, garden plants, trees, shrubs, flowers, vegetables, herbs, succulents, etc.
Examples of what doesn't count: artificial plants, plant-printed items, drawings of plants, dead/dried plants unless clearly identifiable.
"""