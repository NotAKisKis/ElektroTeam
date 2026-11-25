// ============================================================
// Единственное место, где фронтенд знает, откуда берутся данные.
// Этап 1: USE_MOCK = true  (данные в браузере, БД не нужна)
// Этап 2: USE_MOCK = false (запросы к FastAPI)
// ============================================================
const CONFIG = {
  USE_MOCK: true,
  API_BASE: "http://127.0.0.1:8000",
  CURRENCY: "PLN",
  LOCALE: "pl-PL",
};

// ---------- Helpers ----------
function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (ch) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  }[ch]));
}

function formatPrice(value) {
  return new Intl.NumberFormat(CONFIG.LOCALE, {
    style: "currency",
    currency: CONFIG.CURRENCY,
  }).format((Number(value) || 0) / 100);
}

// ---------- Mock data ----------
const MOCK_CATEGORIES = [
  { id: 1, name: "TV" },
  { id: 2, name: "Phones" },
  { id: 3, name: "Drones" },
  { id: 4, name: "Headphones" },
];

const MOCK_SEED = [
  { id: 1, name: 'TV 55" 4K Ultra HD', description: "55-inch 4K display, HDR, smart TV apps.", price_grosz: 219900, stock: 12, category_id: 1, category_name: "TV", image_url: "/static/img/tv.png" },
  { id: 2, name: 'TV 70" 4K Smart', description: "70-inch 4K display, 120 Hz panel.", price_grosz: 399900, stock: 5, category_id: 1, category_name: "TV", image_url: "/static/img/tv.png" },
  { id: 3, name: "Smartphone Pro 256 GB", description: "6.1-inch OLED, triple camera, 5G.", price_grosz: 429900, stock: 8, category_id: 2, category_name: "Phones", image_url: "/static/img/phones.png" },
  { id: 4, name: "Smartphone Lite 128 GB", description: "6.5-inch display, dual camera.", price_grosz: 159900, stock: 20, category_id: 2, category_name: "Phones", image_url: "/static/img/phones.png" },
  { id: 5, name: "Camera drone 4K", description: "4K camera, 3-axis gimbal.", price_grosz: 249900, stock: 4, category_id: 3, category_name: "Drones", image_url: "/static/img/drones.png" },
  { id: 6, name: "Mini drone for beginners", description: "Under 250 g, altitude hold.", price_grosz: 59900, stock: 0, category_id: 3, category_name: "Drones", image_url: "/static/img/drones.png" },
  { id: 7, name: "Wireless noise-cancelling headphones", description: "Over-ear, 40 hours of battery.", price_grosz: 129900, stock: 15, category_id: 4, category_name: "Headphones", image_url: "/static/img/headphones.png" },
  { id: 8, name: "Studio headphones", description: "Closed-back, detachable cable.", price_grosz: 45900, stock: 9, category_id: 4, category_name: "Headphones", image_url: "/static/img/headphones.png" },
];

function categoryName(id) {
  const c = MOCK_CATEGORIES.find((c) => c.id === Number(id));
  return c ? c.name : "";
}

const MOCK_KEY = "elektroteam_mock_v3";
const delay = (ms = 250) => new Promise((resolve) => setTimeout(resolve, ms));

function mockLoad() {
  try {
    const raw = localStorage.getItem(MOCK_KEY);
    if (raw) return JSON.parse(raw);
  } catch (e) { /* storage unavailable: fall back to seed */ }
  return JSON.parse(JSON.stringify(MOCK_SEED));
}

function mockSave(list) {
  try { localStorage.setItem(MOCK_KEY, JSON.stringify(list)); } catch (e) { /* ignore */ }
}



function notFound() {
  const err = new Error("HTTP 404");
  err.status = 404;
  return err;
}

// ---------- Real API (FastAPI) ----------
async function request(path, options = {}) {
  const res = await fetch(CONFIG.API_BASE + path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const err = new Error(`HTTP ${res.status}`);
    err.status = res.status;
    throw err;
  }
  return res.status === 204 ? null : res.json();
}

// The real API returns only category_id, so the name is added here
async function addCategoryNames(items) {
  const cats = await request("/api/categories");
  const names = new Map(cats.map((c) => [c.id, c.name]));
  return items.map((p) => ({ ...p, category_name: names.get(p.category_id) || "" }));
}

// ---------- Public API used by all pages ----------
const api = {
  async getCategories() {
    if (CONFIG.USE_MOCK) { await delay(); return MOCK_CATEGORIES; }
    return request("/api/categories");
  },
  
  async getProducts() {
    if (CONFIG.USE_MOCK) { await delay(); return mockLoad(); }
    return addCategoryNames(await request("/api/products"));
  },

  async getProduct(id) {
    if (CONFIG.USE_MOCK) {
      await delay();
      const found = mockLoad().find((p) => p.id === Number(id));
      if (!found) throw notFound();
      return found;
    }
    const [p] = await addCategoryNames([await request(`/api/products/${id}`)]);
    return p;
  },

  async createProduct(data) {
    if (CONFIG.USE_MOCK) {
      await delay();
      const list = mockLoad();
      const id = list.reduce((max, p) => Math.max(max, p.id), 0) + 1;
      const created = { ...data, id, category_name: categoryName(data.category_id) };
      list.push(created);
      mockSave(list);
      return created;
    }
    return request("/api/products", { method: "POST", body: JSON.stringify(data) });
  },

  async updateProduct(id, data) {
    if (CONFIG.USE_MOCK) {
      await delay();
      const list = mockLoad();
      const i = list.findIndex((p) => p.id === Number(id));
      if (i === -1) throw notFound();
      list[i] = { ...list[i], ...data, id: Number(id), category_name: categoryName(data.category_id) };
      mockSave(list);
      return list[i];
    }
    return request(`/api/products/${id}`, { method: "PUT", body: JSON.stringify(data) });
  },

  async deleteProduct(id) {
    if (CONFIG.USE_MOCK) {
      await delay();
      mockSave(mockLoad().filter((p) => p.id !== Number(id)));
      return null;
    }
    return request(`/api/products/${id}`, { method: "DELETE" });
  },
};
