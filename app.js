const allChecks = Array.from(document.querySelectorAll('input[type="checkbox"]'));
const scoreEl = document.getElementById('score');
const levelEl = document.getElementById('risk-level');
const recommendationsEl = document.getElementById('recommendations');
const copyBtn = document.getElementById('copy-btn');
const resetBtn = document.getElementById('reset-btn');
const actionLog = document.getElementById('action-log');

const guidance = {
  low: [
    'Complete incident report with clear pattern history details.',
    'Offer specialist domestic abuse referral before leaving scene.',
    'Provide safety planning advice and re-contact route.'
  ],
  medium: [
    'Complete safeguarding referral during shift and flag repeat history.',
    'Discuss immediate relocation options and emergency contacts.',
    'Brief supervisor for same-day review of risk and protective options.'
  ],
  high: [
    'Prioritise arrest and robust evidential case building where lawful.',
    'Escalate for multi-agency safeguarding/MARAC-equivalent referral.',
    'Consider urgent protective orders and enhanced patrol reassurance.'
  ],
  critical: [
    'Treat as highest-risk domestic abuse case requiring immediate supervisor oversight.',
    'Urgent safeguarding for victim and children with crisis accommodation options.',
    'Fast-track specialist unit involvement and immediate legal protection pathways.'
  ]
};

function determineRisk(score, hasCriticalFlag, highFlagCount) {
  if (hasCriticalFlag || score >= 28) return 'critical';
  if (score >= 18 || highFlagCount >= 2) return 'high';
  if (score >= 9) return 'medium';
  return 'low';
}

function renderRecommendations(level) {
  const title = level.charAt(0).toUpperCase() + level.slice(1);
  recommendationsEl.innerHTML = `<strong>${title} priority actions</strong>`;
  const list = document.createElement('ul');
  guidance[level].forEach((item) => {
    const li = document.createElement('li');
    li.textContent = item;
    list.appendChild(li);
  });
  recommendationsEl.appendChild(list);
}

function updateRisk() {
  let score = 0;
  let hasCriticalFlag = false;
  let highFlagCount = 0;

  allChecks.forEach((check) => {
    if (!check.checked) return;

    const points = Number(check.dataset.points || 0);
    score += points;

    if (check.dataset.priority === 'critical') hasCriticalFlag = true;
    if (check.dataset.priority === 'high' || points >= 7) highFlagCount += 1;
  });

  const level = determineRisk(score, hasCriticalFlag, highFlagCount);
  const levelLabels = {
    low: 'Standard Risk',
    medium: 'Medium Risk',
    high: 'High Risk',
    critical: 'Critical Risk'
  };

  scoreEl.textContent = String(score);
  levelEl.textContent = levelLabels[level];
  levelEl.className = `risk-level ${level}`;
  renderRecommendations(level);
}

copyBtn.addEventListener('click', async () => {
  const checked = allChecks
    .filter((check) => check.checked)
    .map((check) => `- ${check.parentElement.textContent.trim()}`)
    .join('\n') || '- None selected';

  const summary = [
    `Risk score: ${scoreEl.textContent}`,
    `Risk level: ${levelEl.textContent}`,
    'Selected indicators:',
    checked,
    'Action log:',
    actionLog.value.trim() || 'No additional notes entered.'
  ].join('\n');

  await navigator.clipboard.writeText(summary);
  copyBtn.textContent = 'Copied';
  setTimeout(() => {
    copyBtn.textContent = 'Copy Summary';
  }, 1200);
});

resetBtn.addEventListener('click', () => {
  allChecks.forEach((check) => {
    check.checked = false;
  });
  actionLog.value = '';
  updateRisk();
});

allChecks.forEach((check) => {
  check.addEventListener('change', updateRisk);
});

updateRisk();
