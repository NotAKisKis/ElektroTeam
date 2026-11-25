(async function () {
  const rows = document.getElementById("rows");
  const status = document.getElementById("status");
  const dialog = document.getElementById("product-dialog");
  const dialogTitle = document.getElementById("dialog-title");
  const form = document.getElementById("product-form");
  const formError = document.getElementById("form-error");
  const saveBtn = document.getElementById("save-btn");
  let products = [];
  let editingId = null;

  function setStatus(text) {
    status.textContent = text;
    status.hidden = !text;
  }

  function render() {
    rows.innerHTML = products.map((p) => `
      <tr>
        <td>${p.id}</td>
        <td>${escapeHtml(p.name)}</td>
        <td>${escapeHtml(p.category_name || "")}</td>
        <td>${formatPrice(p.price_grosz)}</td>
        <td>${p.stock}</td>
        <td class="actions">
          <button type="button" class="btn btn-ghost" data-action="edit" data-id="${p.id}">Edit</button>
          <button type="button" class="btn btn-danger" data-action="delete" data-id="${p.id}">Delete</button>
        </td>
      </tr>`).join("");
    if (!products.length) setStatus("No products yet. Use “Add product” to create the first one.");
  }

  async function load() {
    setStatus("Loading products…");
    try {
      products = await api.getProducts();
      setStatus("");
      render();
    } catch (e) {
      products = [];
      rows.innerHTML = "";
      setStatus("Could not load products. Check that the API is running and reload the page.");
    }
  }

  function openForm(p) {
    editingId = p ? p.id : null;
    dialogTitle.textContent = p ? "Edit product" : "Add product";
    form.reset();
    formError.textContent = "";
    const f = form.elements;
    if (p) {
      f["name"].value = p.name;
      f["category_id"].value = p.category_id;
      f["price"].value = p.price_grosz / 100;
      f["image_url"].value = p.image_url || "";
      f["description"].value = p.description || "";
      f["stock"].value = p.stock;
    }
    dialog.showModal();
    f["name"].focus();
  }

  function readForm() {
    const f = form.elements;
    return {
      name: f["name"].value.trim(),
      category_id: Number(f["category_id"].value),
      price_grosz: Math.round(Number(f["price"].value) * 100),
      stock: Number(f["stock"].value),
      image_url: f["image_url"].value.trim() || null,
      description: f["description"].value.trim() || null,
    };
  }

  function validate(data) {
    if (!data.name) return "Enter a product name.";
    if (!data.category_id) return "Choose a category.";
    if (!Number.isFinite(data.price_grosz) || data.price_grosz <= 0) return "Price must be greater than 0.";
    if (!Number.isInteger(data.stock) || data.stock < 0) return "Stock must be a whole number, 0 or more.";
    return "";
  }

  document.getElementById("add-btn").addEventListener("click", () => openForm(null));
  document.getElementById("cancel-btn").addEventListener("click", () => dialog.close());

  rows.addEventListener("click", async (e) => {
    const btn = e.target.closest("button[data-action]");
    if (!btn) return;
    const id = Number(btn.dataset.id);
    const p = products.find((item) => item.id === id);
    if (!p) return;

    if (btn.dataset.action === "edit") {
      openForm(p);
    } else if (btn.dataset.action === "delete") {
      if (!confirm(`Delete “${p.name}”? This cannot be undone.`)) return;
      try {
        await api.deleteProduct(id);
        await load();
      } catch (err) {
        setStatus("Could not delete the product. Try again.");
      }
    }
  });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const data = readForm();
    const problem = validate(data);
    if (problem) { formError.textContent = problem; return; }

    saveBtn.disabled = true;
    try {
      if (editingId === null) {
        await api.createProduct(data);
      } else {
        // PUT replaces all fields: send the current discount back so it is not reset
        const current = products.find((p) => p.id === editingId);
        const keep = current && current.discount_type
          ? { discount_type: current.discount_type, discount_value: current.discount_value }
          : {};
        await api.updateProduct(editingId, { ...data, ...keep });
      }
      dialog.close();
      await load();
    } catch (err) {
      formError.textContent = "Could not save the product. Try again.";
    } finally {
      saveBtn.disabled = false;
    }
  });

  try {
    const cats = await api.getCategories();
    form.elements["category_id"].innerHTML =
      cats.map((c) => `<option value="${c.id}">${escapeHtml(c.name)}</option>`).join("");
  } catch (e) {
    setStatus("Could not load categories.");
  }

  await load();
})();
