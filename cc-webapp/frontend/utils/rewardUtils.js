// cc-webapp/frontend/utils/rewardUtils.js

/**
 * IMPORTANT NOTE:
 * This client-side gacha logic is a simplification for this subtask.
 * In a real-world application, gacha mechanics (determining the reward)
 * should be handled by the backend to ensure security and prevent manipulation.
 * This would typically involve the frontend calling a backend endpoint (e.g., POST /api/games/gacha/pull),
 * which then uses the backend's reward_utils.py::spin_gacha function.
 */

// Export GACHA_ITEMS_CLIENT for testing purposes
export const GACHA_ITEMS_CLIENT = [
    // { type: "REWARD_TYPE", details_if_any, weight: X, make_item: (template) => ({ ...item_details }) }
    {
        type: "COIN",
        details: { value_range: [10, 100] },
        weight: 60, // Increased weight for coins
        make_item: (r) => ({
            type: "COIN",
            amount: Math.floor(Math.random() * (r.details.value_range[1] - r.details.value_range[0] + 1)) + r.details.value_range[0]
        })
    },
    {
        type: "CONTENT_UNLOCK",
        details: { stage: 1 },
        weight: 15, // Adjusted weights
        make_item: (r) => ({ type: "CONTENT_UNLOCK", stage: r.details.stage })
    },
    {
        type: "CONTENT_UNLOCK",
        details: { stage: 2 },
        weight: 10,
        make_item: (r) => ({ type: "CONTENT_UNLOCK", stage: r.details.stage })
    },
    {
        type: "CONTENT_UNLOCK",
        details: { stage: 3 },
        weight: 5,
        make_item: (r) => ({ type: "CONTENT_UNLOCK", stage: r.details.stage })
    },
    {
        type: "BADGE",
        details: { badge_name: "EPIC_PULL" }, // Changed badge name for variety
        weight: 10,
        make_item: (r) => ({ type: "BADGE", badge_name: r.details.badge_name })
    }
]; // Total weight = 100

export const spinGachaClient = async (userId) => {
  console.log(`[spinGachaClient] User ${userId} is spinning the client-side gacha...`);

  // Simulate network delay as if this were a real API call
  await new Promise(resolve => setTimeout(resolve, 200 + Math.random() * 300));

  const totalWeight = GACHA_ITEMS_CLIENT.reduce((sum, item) => sum + item.weight, 0);
  let randomWeight = Math.random() * totalWeight;
  let chosenItemTemplate;

  for (const item of GACHA_ITEMS_CLIENT) {
    if (randomWeight < item.weight) {
      chosenItemTemplate = item;
      break;
    }
    randomWeight -= item.weight;
  }

  // Fallback if something goes wrong with weight calculation (should not happen if weights are positive)
  if (!chosenItemTemplate) {
    console.warn("[spinGachaClient] Gacha choice fallback triggered. Check weights.");
    chosenItemTemplate = GACHA_ITEMS_CLIENT.find(item => item.type === "COIN") || GACHA_ITEMS_CLIENT[0];
  }

  const finalItem = chosenItemTemplate.make_item(chosenItemTemplate);
  console.log(`[spinGachaClient] User ${userId} won:`, finalItem);
  return finalItem;
};

// Renamed from calculateRewardClient and implemented as per test spec (synchronous)
export const calculateReward = (streak_count) => {
  // Logic based on test spec: Min probability 10% for 0 streak. Max 40%.
  // Probability = min(0.10 + streak_count * 0.01, 0.40)
  const probability = Math.min(0.10 + streak_count * 0.01, 0.40);
  console.log(`[calculateReward] Streak: ${streak_count}, Calculated Probability: ${probability.toFixed(2)}`);
  const result = Math.random() < probability;
  console.log(`[calculateReward] Math.random() vs Probability: ${result ? 'Success (random < prob)' : 'Failure (random >= prob)'}`);
  return result;
};
