const clamp = (value, min, max) => Math.max(min, Math.min(max, value));
const formatBytes = (bytes) => bytes < 1024 ? `${Math.round(bytes)} B` : `${(bytes / 1024).toFixed(1)} KB`;

const root = document.documentElement;
const themeToggle = document.querySelector('#theme-toggle');
const storedTheme = localStorage.getItem('tisa-theme');
if (storedTheme) root.dataset.theme = storedTheme;

function syncThemeButton() {
  const dark = root.dataset.theme === 'dark';
  themeToggle.setAttribute('aria-pressed', String(dark));
  themeToggle.setAttribute('aria-label', dark ? 'Switch to light theme' : 'Switch to dark theme');
}
syncThemeButton();
themeToggle.addEventListener('click', () => {
  root.dataset.theme = root.dataset.theme === 'dark' ? 'light' : 'dark';
  localStorage.setItem('tisa-theme', root.dataset.theme);
  syncThemeButton();
});

const tabs = [...document.querySelectorAll('[role="tab"]')];
const panels = [...document.querySelectorAll('[role="tabpanel"]')];
function activatePanel(name, moveFocus = false) {
  tabs.forEach((tab) => {
    const active = tab.dataset.panel === name;
    tab.setAttribute('aria-selected', String(active));
    tab.tabIndex = active ? 0 : -1;
    if (active && moveFocus) tab.focus();
  });
  panels.forEach((panel) => { panel.hidden = panel.id !== `panel-${name}`; });
}
tabs.forEach((tab, index) => {
  tab.addEventListener('click', () => activatePanel(tab.dataset.panel));
  tab.addEventListener('keydown', (event) => {
    if (!['ArrowLeft', 'ArrowRight'].includes(event.key)) return;
    event.preventDefault();
    const direction = event.key === 'ArrowRight' ? 1 : -1;
    const next = (index + direction + tabs.length) % tabs.length;
    activatePanel(tabs[next].dataset.panel, true);
  });
});

document.querySelectorAll('.demo-trigger').forEach((button) => {
  button.addEventListener('click', () => {
    activatePanel(button.dataset.demo);
    document.querySelector('#lab').scrollIntoView({ behavior: 'smooth' });
  });
});

const qoeInputs = ['throughput', 'rtt', 'rebuffer', 'valence'].map((id) => document.querySelector(`#qoe-${id}`));
function updateQoe() {
  const [throughput, rtt, rebuffer, valence] = qoeInputs.map((input) => Number(input.value));
  const score = clamp(2.65 + .085 * throughput - .0045 * rtt - .48 * rebuffer + .45 * valence, 1, 5);
  document.querySelector('#qoe-throughput-out').textContent = `${throughput.toFixed(1)} Mbps`;
  document.querySelector('#qoe-rtt-out').textContent = `${Math.round(rtt)} ms`;
  document.querySelector('#qoe-rebuffer-out').textContent = `${rebuffer.toFixed(1)} s`;
  document.querySelector('#qoe-valence-out').textContent = `${valence >= 0 ? '+' : ''}${valence.toFixed(2)}`;
  document.querySelector('#qoe-score').textContent = score.toFixed(2);
  document.querySelector('#qoe-meter').style.width = `${score / 5 * 100}%`;
  const driver = rebuffer > 2 ? 'Rebuffering is the strongest negative driver.' : rtt > 160 ? 'High latency is suppressing the estimate.' : throughput < 4 ? 'Limited throughput is constraining playback quality.' : 'Network and playback conditions support a stable estimate.';
  document.querySelector('#qoe-explain').textContent = driver;
}
qoeInputs.forEach((input) => input.addEventListener('input', updateQoe));
updateQoe();

const cipherInputs = ['rate', 'rtt', 'burst'].map((id) => document.querySelector(`#cipher-${id}`));
function updateCipher() {
  const [rate, rtt, burst] = cipherInputs.map((input) => Number(input.value));
  const estimatedBandwidth = rate / .48;
  const startup = clamp(.58 + .0115 * rtt + 2 / Math.max(estimatedBandwidth, .5) + burst * .58, .25, 6);
  const stall = clamp((5 - estimatedBandwidth) * .17 + burst * 1.65, 0, 5);
  const adjusted = rate * (1 - .06 * burst);
  const label = adjusted < 2.15 ? 'low' : adjusted < 5.25 ? 'medium' : 'high';
  document.querySelector('#cipher-rate-out').textContent = `${rate.toFixed(1)} Mbps`;
  document.querySelector('#cipher-rtt-out').textContent = `${Math.round(rtt)} ms`;
  document.querySelector('#cipher-burst-out').textContent = burst.toFixed(2);
  document.querySelector('#cipher-startup').textContent = `${startup.toFixed(2)} s`;
  document.querySelector('#cipher-stall').textContent = `${stall.toFixed(2)} s`;
  document.querySelector('#cipher-class').textContent = label;
}
cipherInputs.forEach((input) => input.addEventListener('input', updateCipher));
updateCipher();

const fedInputs = ['clients', 'rounds', 'bits'].map((id) => document.querySelector(`#fed-${id}`));
function updateFed() {
  const [clients, rounds, bits] = fedInputs.map((input) => Number(input.value));
  const active = clients * .92;
  const bytes = active * rounds * 4 * bits / 8;
  const reduction = 1 - bits / 32;
  const quality = .46 + 2.1 / Math.sqrt(rounds) + .18 / Math.sqrt(clients);
  document.querySelector('#fed-clients-out').textContent = String(clients);
  document.querySelector('#fed-rounds-out').textContent = String(rounds);
  document.querySelector('#fed-bits-out').textContent = `${bits} bit`;
  document.querySelector('#fed-bytes').textContent = formatBytes(bytes);
  document.querySelector('#fed-reduction').textContent = `${Math.round(reduction * 100)}%`;
  document.querySelector('#fed-participation').textContent = active.toFixed(1);
  document.querySelector('#fed-quality').textContent = quality.toFixed(2);
}
fedInputs.forEach((input) => input.addEventListener('input', updateFed));
updateFed();

const socFixtures = [
  ['benign', 'host-12', 'session pattern within baseline'],
  ['alert', 'host-04', 'failed-authentication burst'],
  ['benign', 'host-09', 'normal port diversity'],
  ['review', 'host-15', 'confidence near threshold'],
  ['alert', 'host-02', 'scan-like port fan-out'],
  ['benign', 'host-06', 'expected service traffic'],
  ['review', 'host-13', 'outbound ratio shifted'],
  ['benign', 'host-01', 'stable packet rate']
];
let replayCount = 0;
document.querySelector('#soc-replay').addEventListener('click', () => {
  replayCount += 1;
  const events = Array.from({ length: 5 }, (_, index) => socFixtures[(replayCount * 3 + index) % socFixtures.length]);
  document.querySelector('#soc-events').innerHTML = events.map(([kind, host, note]) => `<li><span class="${kind === 'alert' ? 'alert' : ''}">${kind}</span><b>${host}</b><em>${note}</em></li>`).join('');
  const alerts = events.filter(([kind]) => kind === 'alert').length;
  document.querySelector('#soc-alerts').textContent = String(alerts);
  document.querySelector('#soc-clock').textContent = `T+00:${String(replayCount * 5).padStart(2, '0')}`;
  document.querySelector('#soc-drift').textContent = replayCount % 3 === 0 ? 'review' : 'stable';
});

const copyButton = document.querySelector('#copy-email');
copyButton.addEventListener('click', async () => {
  try {
    await navigator.clipboard.writeText('meetme.tisa@gmail.com');
    copyButton.textContent = 'Copied';
  } catch {
    copyButton.textContent = 'meetme.tisa@gmail.com';
  }
  window.setTimeout(() => { copyButton.textContent = 'Copy email'; }, 1800);
});
