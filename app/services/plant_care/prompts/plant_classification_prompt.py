PLANT_CLASSIFICATION_PROMPT = """
Determine whether the input "{plant_name}" refers to a plant. If it is a plant, classify it into a care category.

Respond with ONLY a JSON object in this exact format:

{
  "is_plant": true/false,
  "plant_group": "Vegetables" | "Herbs" | "Fruit Trees" | "Flowering Shrubs" | "Perennial Flowers" | "Annual Flowers" | "Ornamental Trees" | "Houseplants" | "Succulents" | "Bulbs" | "Native Plants" | null,
  "message": "If not a plant, a brief reason; if a plant, you may return a short confirmation"
}

Guidelines:
- Set "is_plant" to true only if the input clearly refers to a living plant (houseplant, tree, shrub, flower, vegetable, herb, succulent, bulb, etc.).
- If "is_plant" is false, set "plant_group" to null and provide a brief helpful message explaining why (e.g., "This appears to be an appliance, not a plant.").
- If "is_plant" is true, set "plant_group" to one of the following:
  - "Vegetables": Annual edible plants grown for food (tomatoes, lettuce, peppers, carrots, etc.)
  - "Herbs": Annual and perennial plants grown for culinary or medicinal use (basil, rosemary, mint, etc.)
  - "Fruit Trees": Long-term fruit-producing trees and shrubs (apple, citrus, berry bushes, etc.)
  - "Flowering Shrubs": Perennial woody ornamental plants (roses, hydrangeas, azaleas, etc.)
  - "Perennial Flowers": Long-term flowering plants (hostas, daylilies, peonies, etc.)
  - "Annual Flowers": Single-season flowering plants (marigolds, petunias, impatiens, etc.)
  - "Ornamental Trees": Non-fruit bearing trees for landscaping (maples, oaks, dogwoods, etc.)
  - "Houseplants": Plants typically grown indoors (fiddle leaf fig, pothos, etc.)
  - "Succulents": Water-storing plants including cacti (echeveria, jade plants, aloe, etc.)
  - "Bulbs": Underground storage organs with seasonal cycles (tulips, daffodils, gladiolus, etc.)
  - "Native Plants": Plants indigenous to specific regions (varies by location)

Input: {plant_name}
Response:"""