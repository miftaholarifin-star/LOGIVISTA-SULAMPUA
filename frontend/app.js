const API_BASE = "http://127.0.0.1:8000";

const priceSample = [
  { source: "Sumber sintetis A", date: "2026-01-05", region: "Jailolo", commodity: "Beras medium", unit: "kg", price: 14800 },
  { source: "Sumber sintetis A", date: "2026-01-05", region: "Sahu", commodity: "Beras medium", unit: "kg", price: 16200 },
  { source: "Sumber sintetis A", date: "2026-01-05", region: "Ibu", commodity: "Beras medium", unit: "kg", price: 17100 },
  { source: "Sumber sintetis B", date: "2026-01-12", region: "Jailolo", commodity: "Beras medium", unit: "kg", price: 15100 },
  { source: "Sumber sintetis B", date: "2026-01-12", region: "Sahu", commodity: "Beras medium", unit: "kg", price: 16500 },
  { source: "Sumber sintetis B", date: "2026-01-12", region: "Ibu", commodity: "Beras medium", unit: "kg", price: 17600 },
];

const networkSample = [
  { source_node: "Pelabuhan Agregat", target_node: "Hub Jailolo", distance_km: 18, lead_time_hours: 2.2, frequency_per_week: 4, mode: "laut", active: true },
  { source_node: "Hub Jailolo", target_node: "Pasar Sahu", distance_km: 31, lead_time_hours: 1.6, frequency_per_week: 3, mode: "darat", active: true },
  { source_node: "Hub Jailolo", target_node: "Pasar Ibu", distance_km: 47, lead_time_hours: 2.4, frequency_per_week: 2, mode: "darat", active: true },
  { source_node: "Pasar Sahu", target_node: "Pasar Ibu", distance_km: 42, lead_time_hours: 2.8, frequency_per_week: 1, mode: "darat", active: true },
];

const elements = {
  status: document.querySelector("#api-status"),
  context: document.querySelector("#result-context"),
  json: document.querySelector("#result-json"),
  labels: [1, 2, 3, 4].map((number) => document.querySelector(`#metric-${["one", "two", "three", "four"][number - 1]}-label`)),
  values: [1, 2, 3, 4].map((number) => document.querySelector(`#metric-${["one", "two", "three", "four"][number - 1]}`)),
};

async function request(path, body) {
  const response = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || `HTTP ${response.status}`);
  }
  return data;
}

function setMetrics(labels, values, context, data) {
  labels.forEach((label, index) => { elements.labels[index].textContent = label; });
  values.forEach((value, index) => { elements.values[index].textContent = value; });
  elements.context.textContent = context;
  elements.json.textContent = JSON.stringify(data, null, 2);
}

function showError(error) {
  setMetrics(
    ["Status", "Modul", "Respons", "Tindakan"],
    ["GAGAL", "API", "422/500", "PERIKSA DATA"],
    "Analisis gagal",
    { error: error.message },
  );
}

async function checkApi() {
  try {
    const response = await fetch(`${API_BASE}/health`);
    if (!response.ok) throw new Error("API tidak merespons");
    const data = await response.json();
    elements.status.textContent = `API aktif · v${data.version}`;
    elements.status.className = "api-status online";
  } catch (_error) {
    elements.status.textContent = "API belum aktif";
    elements.status.className = "api-status offline";
  }
}

document.querySelector("#analyze-price").addEventListener("click", async (event) => {
  const button = event.currentTarget;
  button.disabled = true;
  button.textContent = "Menganalisis…";
  try {
    const result = await request("/api/v1/analysis/prices", {
      observations: priceSample,
      cv_threshold: Number(document.querySelector("#cv-threshold").value),
      pdi_threshold: Number(document.querySelector("#pdi-threshold").value),
      persist: false,
    });
    setMetrics(
      ["CV Populasi", "PDI v0.1", "Wilayah", "Status"],
      [`${result.cv_percent.toFixed(2)}%`, `${result.pdi_v01_percent.toFixed(2)}%`, result.region_count, result.status.replaceAll("_", " ")],
      `${result.commodity} · ${result.traceability.period_start} s.d. ${result.traceability.period_end}`,
      result,
    );
  } catch (error) {
    showError(error);
  } finally {
    button.disabled = false;
    button.textContent = "Analisis Data Harga Contoh";
  }
});

document.querySelector("#analyze-network").addEventListener("click", async (event) => {
  const button = event.currentTarget;
  button.disabled = true;
  button.textContent = "Menganalisis…";
  try {
    const result = await request("/api/v1/analysis/network", {
      routes: networkSample,
      persist: false,
    });
    setMetrics(
      ["Rute Aktif", "Simpul", "Komponen", "Peringatan"],
      [result.active_route_count, result.node_count, result.component_count, result.warnings.length],
      "Jaringan distribusi contoh anonim",
      result,
    );
  } catch (error) {
    showError(error);
  } finally {
    button.disabled = false;
    button.textContent = "Analisis Jaringan Contoh";
  }
});

checkApi();
