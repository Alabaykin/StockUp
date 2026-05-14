/* ═══════════════════════════════════════════
   StockUp — Frontend Application Logic
   ═══════════════════════════════════════════ */

const API_BASE = "/api/v1";

// ── State ──
let currentUser = null;
let products = [];
let categories = [];
let editingProductId = null;

// ── Telegram Web App ──
const tg = window.Telegram?.WebApp;

function getInitData() {
    if (tg && tg.initData) return tg.initData;
    return "dev_mode"; // fallback for local dev
}

// ── API helpers ──
async function api(method, path, body = null) {
    const headers = {
        "Content-Type": "application/json",
        "x-tg-init-data": getInitData(),
    };
    const opts = { method, headers };
    if (body) opts.body = JSON.stringify(body);

    const res = await fetch(`${API_BASE}${path}`, opts);
    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `HTTP ${res.status}`);
    }
    return res.json();
}

// ── DOM helpers ──
const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

function showScreen(id) {
    $$(".screen").forEach((s) => s.classList.remove("active"));
    $(`#${id}`).classList.add("active");
}

function showModal(id) {
    $(`#${id}`).classList.remove("hidden");
}

function hideModal(id) {
    $(`#${id}`).classList.add("hidden");
}

function toast(msg) {
    let el = $(".toast");
    if (!el) {
        el = document.createElement("div");
        el.className = "toast";
        document.body.appendChild(el);
    }
    el.textContent = msg;
    el.classList.add("show");
    setTimeout(() => el.classList.remove("show"), 2500);
}

// ── Render Products ──
function renderProducts() {
    const list = $("#product-list");
    const empty = $("#empty-products");

    if (products.length === 0) {
        list.innerHTML = "";
        empty.classList.remove("hidden");
        return;
    }

    empty.classList.add("hidden");
    list.innerHTML = products
        .map(
            (p) => `
        <div class="product-card" data-id="${p.id}">
            <div class="product-emoji">${p.emoji || "📦"}</div>
            <div class="product-details">
                <div class="product-name">${escHtml(p.name)}</div>
                <div class="product-meta">
                    ${p.category_id ? `<span class="category-badge">${escHtml(categories.find(c => c.id === p.category_id)?.name || "")}</span>` : ""}
                    ${p.description ? escHtml(p.description) : ""}
                </div>
            </div>
            <button class="btn-sub ${p.is_subscribed ? 'active' : ''}" data-id="${p.id}" title="Notify when out of stock">
                ${p.is_subscribed ? '🔔' : '🔕'}
            </button>
            <div class="product-qty">
                <button class="qty-btn" data-action="dec" data-id="${p.id}">−</button>
                <div>
                    <span class="qty-value">${formatQty(p.quantity)}</span>
                    <span class="qty-unit">${p.unit || ""}</span>
                </div>
                <button class="qty-btn" data-action="inc" data-id="${p.id}">+</button>
            </div>
        </div>`
        )
        .join("");

    // Long-press to edit / delete
    list.querySelectorAll(".product-card").forEach((card) => {
        card.addEventListener("click", (e) => {
            // Don't trigger if clicking qty buttons
            if (e.target.closest(".qty-btn") || e.target.closest(".btn-sub")) return;
            openEditProduct(card.dataset.id);
        });
    });

    // Sub buttons
    list.querySelectorAll(".btn-sub").forEach((btn) => {
        btn.addEventListener("click", (e) => {
            e.stopPropagation();
            toggleSubscription(btn.dataset.id);
        });
    });

    // Qty buttons
    list.querySelectorAll(".qty-btn").forEach((btn) => {
        btn.addEventListener("click", (e) => {
            e.stopPropagation();
            handleQtyChange(btn.dataset.id, btn.dataset.action);
        });
    });
}

function escHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
}

function formatQty(q) {
    if (q === null || q === undefined) return "0";
    return Number.isInteger(q) ? q.toString() : q.toFixed(1);
}

// ── Quantity change ──
async function handleQtyChange(productId, action) {
    const product = products.find((p) => p.id === productId);
    if (!product) return;

    let newQty = action === "inc" ? product.quantity + 1 : product.quantity - 1;
    if (newQty < 0) newQty = 0;

    try {
        const updated = await api("PUT", `/products/${productId}`, {
            quantity: newQty,
        });
        const idx = products.findIndex((p) => p.id === productId);
        if (idx !== -1) products[idx] = updated;
        renderProducts();
    } catch (err) {
        toast("Error: " + err.message);
    }
}

// ── Toggle Subscription ──
async function toggleSubscription(productId) {
    try {
        const res = await api("POST", "/subscriptions/toggle", { product_id: productId });
        const product = products.find(p => p.id === productId);
        if (product) {
            product.is_subscribed = (res.status === "subscribed");
            renderProducts();
            toast(res.status === "subscribed" ? "Subscribed to alerts" : "Unsubscribed");
        }
    } catch (err) {
        toast("Failed to toggle subscription");
    }
}

// ── Open modal to add product ──
function openAddProduct() {
    editingProductId = null;
    $("#modal-product-title").textContent = "Add Product";
    $("#btn-save-product").innerHTML = '<span class="btn-icon">💾</span> Save';
    $("#form-product").reset();
    $("#select-category").value = "";
    $("#input-qty").value = "1";
    showModal("modal-product");
    setTimeout(() => $("#input-name").focus(), 200);
}

// ── Open modal to edit product ──
function openEditProduct(productId) {
    const product = products.find((p) => p.id === productId);
    if (!product) return;

    editingProductId = productId;
    $("#modal-product-title").textContent = "Edit Product";
    $("#btn-save-product").innerHTML = '<span class="btn-icon">💾</span> Update';
    $("#input-name").value = product.name;
    $("#input-qty").value = product.quantity;
    $("#input-unit").value = product.unit || "pcs";
    $("#input-desc").value = product.description || "";
    $("#select-category").value = product.category_id || "";
    showModal("modal-product");
}

// ── Save product (create or update) ──
async function saveProduct(e) {
    e.preventDefault();

    const body = {
        name: $("#input-name").value.trim(),
        quantity: parseFloat($("#input-qty").value) || 0,
        unit: $("#input-unit").value,
        description: $("#input-desc").value.trim() || null,
        category_id: $("#select-category").value || null
    };

    if (!body.name) {
        toast("Please enter a product name");
        return;
    }

    try {
        if (editingProductId) {
            const updated = await api("PUT", `/products/${editingProductId}`, body);
            const idx = products.findIndex((p) => p.id === editingProductId);
            if (idx !== -1) products[idx] = updated;
            toast("Product updated ✓");
        } else {
            const created = await api("POST", "/products/", body);
            products.push(created);
            toast(`${created.emoji || "📦"} ${created.name} added!`);
        }
        renderProducts();
        hideModal("modal-product");
    } catch (err) {
        toast("Error: " + err.message);
    }
}

// ── Delete product ──
async function deleteProduct(productId) {
    try {
        await api("DELETE", `/products/${productId}`);
        products = products.filter((p) => p.id !== productId);
        renderProducts();
        hideModal("modal-product");
        toast("Product deleted");
    } catch (err) {
        toast("Error: " + err.message);
    }
}

// ── Family actions ──
async function createFamily() {
    try {
        const family = await api("POST", "/family/create");
        toast("Family created! Code: " + family.invite_code);
        await loadApp();
    } catch (err) {
        toast("Error: " + err.message);
    }
}

async function joinFamily(e) {
    e.preventDefault();
    const code = $("#input-invite-code").value.trim();
    if (!code) return;

    try {
        await api("POST", "/family/join", { invite_code: code });
        toast("Joined family! ✓");
        hideModal("modal-join");
        await loadApp();
    } catch (err) {
        toast("Error: " + err.message);
    }
}

// ── Language change ──
async function changeLanguage(lang) {
    try {
        await api("PUT", "/user/language", { language: lang });
        toast("Language updated to " + (lang === "en" ? "English" : "Русский"));
    } catch (err) {
        toast("Error: " + err.message);
    }
}

// ── Load application ──
async function loadApp() {
    console.log("Starting loadApp...");
    showScreen("screen-loading");
    const loaderText = $(".loader-text");
    if (loaderText) loaderText.textContent = "Loading user profile...";

    try {
        // 1. Get user profile
        console.log("Fetching user profile...");
        currentUser = await api("GET", "/user/me");
        console.log("User profile loaded:", currentUser);

        if (loaderText) loaderText.textContent = "Loading family data...";

        // 2. Try to get family
        let family = null;
        try {
            console.log("Fetching family info...");
            family = await api("GET", "/family/me");
            console.log("Family info loaded:", family);
        } catch (e) {
            console.log("User has no family yet or error:", e.message);
        }

        if (!family) {
            console.log("Showing no-family screen");
            showScreen("screen-no-family");
            return;
        }

        if (loaderText) loaderText.textContent = "Loading products...";

        // 3. Set UI info
        $("#family-info").textContent = `Invite code: ${family.invite_code}`;
        $("#invite-code-display").textContent = family.invite_code;
        $("#select-lang").value = currentUser.language || "en";

        // 4. Load products and categories
        console.log("Fetching products & categories...");
        const [prodList, catList] = await Promise.all([
            api("GET", "/products/"),
            api("GET", "/categories/")
        ]);
        products = prodList;
        categories = catList;
        
        console.log("Data loaded:", products.length, "products,", categories.length, "categories");
        renderProducts();
        renderCategorySelect();

        showScreen("screen-products");
    } catch (err) {
        console.error("Failed to load app:", err);
        if (loaderText) {
            loaderText.innerHTML = `<span style="color:var(--destructive)">Error: ${err.message}</span><br>Retrying in 3s...`;
        }
        toast("Connection error: " + err.message);
        setTimeout(loadApp, 3000);
    }
}

function renderCategorySelect() {
    const select = $("#select-category");
    const val = select.value;
    select.innerHTML = '<option value="">No category</option>' + 
        categories.map(c => `<option value="${c.id}">${escHtml(c.name)}</option>`).join("");
    select.value = val;
}

// ── Event Listeners ──
document.addEventListener("DOMContentLoaded", () => {
    // Category management
    const btnAddCat = $("#btn-add-category");
    if (btnAddCat) {
        btnAddCat.onclick = async () => {
            const name = prompt("Enter new category name:");
            if (!name) return;
            try {
                const newCat = await api("POST", "/categories/", { name });
                categories.push(newCat);
                renderCategorySelect();
                $("#select-category").value = newCat.id;
            } catch (err) {
                toast("Failed to create category");
            }
        };
    }
    // Init Telegram Web App
    if (tg) {
        tg.ready();
        tg.expand();
    }

    // Family buttons
    $("#btn-create-family").addEventListener("click", createFamily);
    $("#btn-join-family").addEventListener("click", () => showModal("modal-join"));

    // Product form
    $("#form-product").addEventListener("submit", saveProduct);
    $("#btn-add-product").addEventListener("click", openAddProduct);

    // Join form
    $("#form-join").addEventListener("submit", joinFamily);

    // Settings
    $("#btn-settings").addEventListener("click", () => showModal("modal-settings"));
    $("#btn-close-settings").addEventListener("click", () => hideModal("modal-settings"));
    $("#btn-copy-code").addEventListener("click", () => {
        const code = $("#invite-code-display").textContent;
        navigator.clipboard?.writeText(code);
        toast("Code copied! " + code);
    });

    // Language selector
    $("#select-lang").addEventListener("change", (e) => {
        changeLanguage(e.target.value);
    });

    // Close modals on backdrop click
    $$(".modal-backdrop").forEach((bd) => {
        bd.addEventListener("click", () => {
            bd.closest(".modal").classList.add("hidden");
        });
    });

    // Start app
    loadApp();
});
