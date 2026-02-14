const hotelRatePerNight = {
  budget: 120,
  mid: 220,
  luxury: 420,
};

const interestActivities = {
  beaches: ["South Beach morning", "Key Biscayne sunset", "Lummus Park walk"],
  food: ["Little Havana food tour", "Wynwood brunch", "Cuban coffee crawl"],
  nightlife: ["Rooftop in Brickell", "Salsa night in Calle Ocho", "Ocean Drive bars"],
  culture: ["Pérez Art Museum", "Vizcaya Museum", "Art Deco District tour"],
  outdoors: ["Everglades day trip", "Paddleboarding at Oleta", "Biking Venetian Causeway"],
  shopping: ["Design District afternoon", "Lincoln Road shopping", "Bayside Marketplace"],
};

const checklistItems = [
  "Passport/ID + travel documents",
  "Swimwear and flip-flops",
  "Lightweight outfits",
  "Sunscreen (high SPF)",
  "Reusable water bottle",
  "Phone charger + power bank",
  "Rain layer (short tropical showers)",
];

function getSelectedInterests() {
  return [...document.querySelectorAll('.chips input[type="checkbox"]:checked')].map(
    (item) => item.value
  );
}

function buildItinerary(days, interests) {
  const picks = interests.length ? interests : ["beaches", "food"];
  const itinerary = [];

  for (let day = 1; day <= days; day += 1) {
    const interest = picks[(day - 1) % picks.length];
    const options = interestActivities[interest];
    const activity = options[(day - 1) % options.length];
    itinerary.push(`Day ${day}: ${activity}`);
  }

  return itinerary;
}

function generatePlan(event) {
  event.preventDefault();

  const travelers = Number(document.getElementById("travelers").value);
  const days = Number(document.getElementById("days").value);
  const budget = Number(document.getElementById("budget").value);
  const hotelTier = document.getElementById("hotel-tier").value;
  const interests = getSelectedInterests();

  const estimatedHotel = hotelRatePerNight[hotelTier] * (days - 1);
  const estimatedFood = travelers * days * 55;
  const estimatedActivities = travelers * days * 45;
  const estimatedTransport = days * 30;
  const estimatedTotal = estimatedHotel + estimatedFood + estimatedActivities + estimatedTransport;
  const dailyBudget = Math.round(budget / days);
  const budgetStatus =
    budget >= estimatedTotal
      ? "✅ Your budget looks comfortable for this plan."
      : "⚠️ Budget may be tight. Consider fewer paid activities or a lower hotel tier.";

  const summary = document.getElementById("summary");
  summary.innerHTML = `
    <p><strong>Travelers:</strong> ${travelers} &nbsp;|&nbsp; <strong>Days:</strong> ${days}</p>
    <p><strong>Daily budget:</strong> $${dailyBudget} per day</p>
    <p><strong>Estimated trip cost:</strong> $${estimatedTotal}</p>
    <p>${budgetStatus}</p>
  `;

  const itinerary = buildItinerary(days, interests);
  document.getElementById("itinerary").innerHTML = itinerary.map((dayPlan) => `<li>${dayPlan}</li>`).join("");
  document.getElementById("checklist").innerHTML = checklistItems.map((item) => `<li>${item}</li>`).join("");

  document.getElementById("results").classList.remove("hidden");
}

document.getElementById("trip-form").addEventListener("submit", generatePlan);
