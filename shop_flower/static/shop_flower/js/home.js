document.addEventListener("DOMContentLoaded", () => {

  /* =========================
     CART STATE
  ========================= */
  let cart = JSON.parse(sessionStorage.getItem("cart")) || {};

  /* =========================
     UTIL
  ========================= */
  function saveCart() {
    sessionStorage.setItem("cart", JSON.stringify(cart));
  }

  function updateBadge() {
    const total = Object.values(cart).reduce((s, i) => s + i.qty, 0);
    const badge = document.querySelector(".cart-badge");
    if (badge) badge.innerText = total;
  }

  /* =========================
     ADD TO CART
  ========================= */
  document.querySelectorAll(".btn-add-cart").forEach(btn => {
    btn.addEventListener("click", () => {
      const box = btn.closest(".cart-action");
      if (!box) return;

      const id = box.dataset.id;

      if (!cart[id]) {
        cart[id] = {
          id: id,
          name: box.dataset.name,
          price: parseFloat(box.dataset.price),
          qty: 1,
          image: box.dataset.image
        };
      }

      saveCart();
      renderQtyControl(box, cart[id].qty);
      syncCartUI();
    });
  });

  /* =========================
     RENDER QTY CONTROL
  ========================= */
  function renderQtyControl(box, qty) {
    box.innerHTML = `
      <div class="d-flex justify-content-center align-items-center gap-2">
        <button class="btn btn-outline-secondary btn-minus">−</button>
        <input type="number"
               class="form-control text-center qty-input"
               value="${qty}"
               min="1"
               style="width:70px">
        <button class="btn btn-outline-secondary btn-plus">+</button>
        <button class="btn btn-outline-danger btn-remove">🗑</button>
      </div>
    `;

    bindQtyEvents(box);
  }

  /* =========================
     QTY EVENTS
  ========================= */
  function bindQtyEvents(box) {
    const id = box.dataset.id;

    box.querySelector(".btn-plus").onclick = () => {
      cart[id].qty++;
      saveCart();
      box.querySelector(".qty-input").value = cart[id].qty;
      syncCartUI();
    };

    box.querySelector(".btn-minus").onclick = () => {
      if (cart[id].qty > 1) {
        cart[id].qty--;
        saveCart();
        box.querySelector(".qty-input").value = cart[id].qty;
        syncCartUI();
      }
    };

    box.querySelector(".qty-input").onchange = e => {
      let v = parseInt(e.target.value);
      if (isNaN(v) || v < 1) v = 1;
      cart[id].qty = v;
      saveCart();
      syncCartUI();
    };

    box.querySelector(".btn-remove").onclick = () => {
      showDeleteModal(id, box);
    };
  }

  /* =========================
     SYNC CARD ON RELOAD
  ========================= */
  function syncAllCards() {
  document.querySelectorAll(".cart-action").forEach(box => {
    const id = box.dataset.id;
    if (cart[id]) {
      renderQtyControl(box, cart[id].qty);
    } else {
      // reset thành nút thêm
      box.innerHTML = `
        <button class="btn btn-danger rounded-pill fw-bold w-100 btn-add-cart">
          🛒 Thêm vào giỏ
        </button>
      `;
      // gắn lại event cho nút mới
      const newBtn = box.querySelector(".btn-add-cart");
      if (newBtn) {
        newBtn.addEventListener("click", () => {
          cart[id] = {
            id,
            name: box.dataset.name,
            price: parseFloat(box.dataset.price),
            qty: 1,
            image: box.dataset.image
          };
          saveCart();
          renderQtyControl(box, 1);
          syncCartUI();
        });
      }
    }
  });
}


  /* =========================
     DELETE CONFIRM MODAL
  ========================= */
  function showDeleteModal(id, box) {
  const modalEl = document.getElementById("modal-xoa");
  if (!modalEl) return;

  const modal = new bootstrap.Modal(modalEl);
  const confirmBtn = document.getElementById("btn-confirm-delete");

  confirmBtn.onclick = () => {
    delete cart[id];
    saveCart();

    // reset UI card
    box.innerHTML = `
      <button class="btn btn-danger rounded-pill fw-bold w-100 btn-add-cart">
        🛒 Thêm vào giỏ
      </button>
    `;

    // gán lại event cho nút mới
    box.querySelector(".btn-add-cart").addEventListener("click", () => {
      cart[id] = {
        id,
        name: box.dataset.name,
        price: parseFloat(box.dataset.price),
        qty: 1,
        image: box.dataset.image
      };
      saveCart();
      renderQtyControl(box, 1);
      syncCartUI();
    });

    syncCartUI();
    renderCartModal(); // cập nhật modal giỏ hàng
    modal.hide();
  };

  modal.show();
}


  /* =========================
     CART MODAL RENDER
  ========================= */
  const cartModal = document.getElementById("modal-giohang");
  if (cartModal) {
    cartModal.addEventListener("show.bs.modal", () => {
      renderCartModal();
    });
  }

function syncCartUI() {
  updateBadge();
  renderCartModal();
  // gọi syncAllCards() (hàm bạn đã có) để đồng bộ cards trên home
  syncAllCards();
}

// bind sự kiện + / - / input / remove trong modal
function bindCartModalEvents() {

  const rows = document.querySelectorAll(
    "#cart-items div[data-id]"
  );

  rows.forEach(row => {

    const id = row.dataset.id;

    const btnPlus = row.querySelector(".btn-plus");
    const btnMinus = row.querySelector(".btn-minus");
    const inputQty = row.querySelector(".qty-input");
    const btnRemove = row.querySelector(".btn-remove");

    if (btnPlus) {
      btnPlus.onclick = () => {
        cart[id].qty++;
        saveCart();
        syncCartUI();
      };
    }

    if (btnMinus) {
      btnMinus.onclick = () => {
        if (cart[id].qty > 1) {
          cart[id].qty--;
          saveCart();
          syncCartUI();
        }
      };
    }

    if (inputQty) {
      inputQty.onchange = e => {
        let v = parseInt(e.target.value);
        if (isNaN(v) || v < 1) v = 1;
        cart[id].qty = v;
        saveCart();
        syncCartUI();
      };
    }

    if (btnRemove) {
      btnRemove.onclick = () => {
        delete cart[id];
        saveCart();
        syncCartUI();
      };
    }

  });
}



function renderCartModal() {

  const cartBox = document.getElementById("cart-items");
  if (!cartBox) return;

  if (Object.keys(cart).length === 0) {
    cartBox.innerHTML = `<p class="text-center">🛒 Giỏ hàng trống</p>`;
    return;
  }

  let html = "";

  Object.values(cart).forEach(item => {
    html += `
      <div class="d-flex align-items-center justify-content-between mb-3 border-bottom pb-2"
           data-id="${item.id}">
        
        <div class="d-flex align-items-center gap-3">
          <img src="${item.image || '/static/shop_flower/images/no-image.png'}"
               style="width:60px;height:60px;object-fit:cover;border-radius:6px">
          <div>
            <strong>${item.name}</strong><br>
            <small>${item.price.toLocaleString()} VND</small>
          </div>
        </div>

        <div class="d-flex align-items-center gap-2">
          <button class="btn btn-outline-secondary btn-minus">−</button>

          <input type="number"
                 class="form-control text-center qty-input"
                 value="${item.qty}"
                 min="1"
                 style="width:60px">

          <button class="btn btn-outline-secondary btn-plus">+</button>

          <button class="btn btn-outline-danger btn-remove">🗑</button>
        </div>

      </div>
    `;
  });

  // ✅ CHỈ render phần item
  cartBox.innerHTML = html;

  // ✅ bind event
  bindCartModalEvents();
}


  /* =========================
     INIT
  ========================= */
  updateBadge();
  syncAllCards();

});
