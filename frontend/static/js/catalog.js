(async function () {
  const grid = document.getElementById("grid");
  const status = document.getElementById("status");
  const search = document.getElementById("search");
  const chips = document.getElementById("chips");
  let products = [];
  let activeCategory = new URLSearchParams(location.search).get("category") || "";

  function setStatus(text) {
    status.textContent = text;
    status.hidden = !text;
  }

  function cardHtml(p) {
    const media = p.image_url
      ? `<img src="${escapeHtml(p.image_url)}" alt="" loading="lazy">`
      : `<span class="placeholder" aria-hidden="true">${escapeHtml(String(p.name).charAt(0))}</span>`;
    return `
      <li>
        <a class="card" href="/product/${p.id}">
          <div class="card-media">${media}</div>
          <div class="card-body">
            <h2 class="card-title">${escapeHtml(p.name)}</h2>
            <p class="card-meta">${escapeHtml(p.category_name || "")}</p>
            <p class="card-price">${formatPrice(p.price_grosz)}</p>
            ${p.stock > 0 ? "" : '<p class="card-flag">Out of stock</p>'}
          </div>
        </a>
      </li>`;
  }

  function renderChips() {
    const cats = [...new Set(products.map((p) => p.category_name).filter(Boolean))].sort();
    chips.innerHTML = ["", ...cats].map((c) =>
      `<button type="button" class="chip" data-cat="${escapeHtml(c)}" aria-pressed="${c === activeCategory}">${c ? escapeHtml(c) : "All"}</button>`
    ).join("");
  }

  function render() {
    const q = search.value.trim().toLowerCase();
    const list = products.filter((p) =>
      (!activeCategory || p.category_name === activeCategory) &&
      (!q || p.name.toLowerCase().includes(q) || (p.description || "").toLowerCase().includes(q))
    );
    grid.innerHTML = list.map(cardHtml).join("");
    setStatus(list.length ? "" : "No products match. Clear the search or pick another category.");
  }

  chips.addEventListener("click", (e) => {
    const btn = e.target.closest("button[data-cat]");
    if (!btn) return;
    activeCategory = btn.dataset.cat;
    renderChips();
    render();
  });
  search.addEventListener("input", render);
  if (location.hash === "#search") search.focus();

  setStatus("Loading products…");
  try {
    products = await api.getProducts();
    if (!products.length) {
      setStatus("The shop is empty. Add the first product in the admin panel.");
    } else {
      renderChips();
      render();
    }
  } catch (e) {
    setStatus("Could not load products. Check that the API is running and reload the page.");
  }
})();
