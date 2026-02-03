function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + "=")) {
                cookieValue = decodeURIComponent(
                    cookie.substring(name.length + 1)
                );
                break;
            }
        }
    }
    return cookieValue;
}

let cart = {};

window.addToCart = function (flowerId) {
    fetch(`/cart/add/${flowerId}/`, {
        method: "POST",
        headers: {
            "X-CSRFToken": getCookie("csrftoken")
        }
    })
    .then(res => res.json())
    .then(() => {
        loadCartFromServer();
    });
};

  function loadCartFromServer() {
  fetch("/cart/get/")
    .then(res => res.json())
    .then(data => {
      cart = {};
      data.items.forEach(i => {
        cart[i.id] = i;
      });
      syncUI();
    });
}


  function addToCart(id) {
  fetch(`/cart/add/${id}/`, {
    method: "POST",
    headers: {
      "X-CSRFToken": getCookie("csrftoken")
    }
  }).then(() => loadCartFromServer());
}


  function saveCart() {
    sessionStorage.setItem("cart", JSON.stringify(cart));
  }

  function updateBadge() {
    const total = Object.values(cart).reduce((s, i) => s + i.qty, 0);
    const badge = document.querySelector(".cart-badge");
    if (badge) badge.innerText = total;
  }

  /* =========================
     RENDER CART MODAL
  ========================= */
  function renderCartModal() {
    const box = document.getElementById("cart-items");
    if (!box) return;

    if (Object.keys(cart).length === 0) {
      box.innerHTML = "<p class='text-center'>🛒 Giỏ hàng trống</p>";
      return;
    }

    let html = "";

    Object.values(cart).forEach(item => {
      html += `
        <div class="d-flex align-items-center justify-content-between mb-3 border-bottom pb-2"
             data-id="${item.id}">
          
          <div class="d-flex align-items-center gap-3">
            <img src="${item.image}"
                 style="width:60px;height:60px;object-fit:cover;border-radius:6px">

            <div>
              <strong>${item.name}</strong><br>
              <small>${item.price.toLocaleString()} VND</small>
            </div>
          </div>

          <div class="d-flex align-items-center gap-2">
            <button class="btn btn-outline-secondary btn-minus">−</button>
            <input type="number" class="form-control text-center qty-input"
                   value="${item.qty}" min="1" style="width:60px">
            <button class="btn btn-outline-secondary btn-plus">+</button>
            <button class="btn btn-outline-danger btn-remove">🗑</button>
          </div>
        </div>
      `;
    });

    box.innerHTML = html;
    bindCartModalEvents();
  }

  /* =========================
     EVENTS TRONG MODAL
  ========================= */
  function bindCartModalEvents() {
    document.querySelectorAll("#cart-items > div").forEach(row => {
      const id = row.dataset.id;

      row.querySelector(".btn-plus").onclick = () => {
        cart[id].qty++;
        fetch("/cart/update/", {
          method: "POST",
          headers: {
            "X-CSRFToken": getCookie("csrftoken"),
            "Content-Type": "application/x-www-form-urlencoded"
          },
          body: `id=${id}&qty=${cart[id].qty}`
        });
        syncUI();
      };

      row.querySelector(".btn-minus").onclick = () => {
        if (cart[id].qty > 1) {
          cart[id].qty--;
          saveCart();
          syncUI();
        }
      };

      row.querySelector(".qty-input").onchange = e => {
        let v = parseInt(e.target.value);
        if (isNaN(v) || v < 1) v = 1;
        cart[id].qty = v;
        saveCart();
        syncUI();
      };

      row.querySelector(".btn-remove").onclick = () => {
        delete cart[id];
        fetch("/cart/remove/", {
          method: "POST",
          headers: {
            "X-CSRFToken": getCookie("csrftoken"),
            "Content-Type": "application/x-www-form-urlencoded"
          },
          body: `id=${id}`
        });
        syncUI();
      };
    });
  }

  /* =========================
     SYNC TOÀN BỘ UI
  ========================= */
  function syncUI() {
    updateBadge();
    renderCartModal();
    syncCardsOnHome();
  }

  function syncCardsOnHome() {
    document.querySelectorAll(".cart-action").forEach(box => {
      const id = box.dataset.id;
      if (cart[id]) {
        renderQtyControl(box, cart[id].qty);
      } else {
        box.innerHTML = `
          <button class="btn btn-danger rounded-pill fw-bold w-100 btn-add-cart">
            🛒 Thêm vào giỏ
          </button>
        `;
      }
    });
  }

  /* =========================
     MODAL OPEN
  ========================= */
  const modal = document.getElementById("modal-giohang");
  if (modal) {
    modal.addEventListener("show.bs.modal", renderCartModal);
  }

  updateBadge();

