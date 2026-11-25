(async function () {
  const root = document.getElementById("product");
  const status = document.getElementById("status");
  const id = root.dataset.id;

  function setStatus(text) {
    status.textContent = text;
    status.hidden = !text;
  }

  setStatus("Loading product…");
  try {
    const p = await api.getProduct(id);
    document.title = p.name;
    document.getElementById("product-name").textContent = p.name;
    document.getElementById("product-category").textContent = p.category_name || "";
    document.getElementById("product-price").textContent = formatPrice(p.price_grosz);
    document.getElementById("product-description").textContent = p.description || "";

    const stock = document.getElementById("product-stock");
    stock.textContent = p.stock > 0 ? "In stock" : "Out of stock";
    stock.classList.toggle("badge-off", !(p.stock > 0));

    const media = document.getElementById("product-media");
    if (p.image_url) {
      const img = document.createElement("img");
      img.src = p.image_url;
      img.alt = p.name;
      media.appendChild(img);
    } else {
      media.innerHTML = `<span class="placeholder" aria-hidden="true">${escapeHtml(String(p.name).charAt(0))}</span>`;
    }

    setStatus("");
    root.hidden = false;
  } catch (e) {
    setStatus(e.status === 404
      ? "This product does not exist or was removed."
      : "Could not load the product. Check that the API is running and reload the page.");
  }
})();
