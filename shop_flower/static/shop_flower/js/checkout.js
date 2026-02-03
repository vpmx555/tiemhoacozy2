document.addEventListener("DOMContentLoaded", () => {

  const cart = JSON.parse(sessionStorage.getItem("cart")) || {};

  const cartBox = document.getElementById("checkout-cart");
  const totalBox = document.getElementById("checkout-total");
  const btnOrder = document.getElementById("btn-order");

  let total = 0;

  /* =============================
     RENDER CART
  ============================== */
  function renderCart() {

      if (Object.keys(cart).length === 0) {
          cartBox.innerHTML = `
              <tr>
                  <td colspan="5" class="text-center py-4">
                      🛒 Giỏ hàng trống
                  </td>
              </tr>
          `;
          btnOrder.disabled = true;
          totalBox.innerText = "0";
          return;
      }

      let html = "";
      total = 0;

      Object.values(cart).forEach(item => {

          const sum = item.price * item.qty;
          total += sum;

          html += `
              <tr class="align-middle">
                  <td>
                      <img 
                          src="${item.image}" 
                          alt="${item.name}"
                          style="
                              width:70px;
                              height:70px;
                              object-fit:cover;
                              border-radius:8px;
                          "
                      >
                  </td>

                  <td>${item.name}</td>

                  <td>${item.price.toLocaleString()} VND</td>

                  <td>${item.qty}</td>

                  <td>${sum.toLocaleString()} VND</td>
              </tr>
          `;
      });

      cartBox.innerHTML = html;
      totalBox.innerText = total.toLocaleString();
  }


  renderCart();

 /* =============================
   SUBMIT ORDER — NEW FLOW
============================== */
btnOrder.addEventListener("click", () => {

    if (Object.keys(cart).length === 0) {
        alert("Giỏ hàng đang trống");
        return;
    }

    const name = document.getElementById("name").value.trim();
    const phone = document.getElementById("phone").value.trim();
    const email = document.getElementById("email").value.trim();
    const address = document.getElementById("address").value.trim();
    const note = document.getElementById("note").value.trim();

    const phoneRegex = /^0\d{9}$/;
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    /* =============================
       VALIDATE
    ============================== */
    if (name.length < 2) {
        alert("Tên không hợp lệ");
        return;
    }

    if (!phoneRegex.test(phone)) {
        alert("Số điện thoại không hợp lệ");
        return;
    }

    if (email && !emailRegex.test(email)) {
        alert("Email không hợp lệ");
        return;
    }

    if (address.length < 10) {
        alert("Địa chỉ giao hàng quá ngắn");
        return;
    }

    /* =============================
       BUILD CART PAYLOAD
    ============================== */

    const cartPayload = [];

    Object.entries(cart).forEach(([flowerId, item]) => {
        cartPayload.push({
            flower_id: Number(flowerId),
            quantity: Number(item.qty)
        });
    });

    /* =============================
       FINAL PAYLOAD
    ============================== */

    const payload = {
        customer: {
            name: name,
            phone: phone,
            email: email,
            address: address,
            note: note
        },

        cart: cartPayload,

        voucher: selectedVoucher
            ? selectedVoucher.code
            : null
    };

    /* =============================
       SUBMIT
    ============================== */
    console.log(payload)
    btnOrder.disabled = true;
    btnOrder.innerText = "⏳ Đang gửi đơn hàng...";

    fetch("/checkout/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken
        },
        body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(data => {

        if (!data.success) {
            throw new Error(data.message || "Checkout failed");
        }

        // xoá cart frontend
        sessionStorage.removeItem("cart");

        // redirect
        window.location.href =
            `/order/${data.order_id}/pending/`;
    })
    .catch(err => {
        alert(err.message || "Có lỗi xảy ra");
        btnOrder.disabled = false;
        btnOrder.innerText = "✅ Đặt hàng";
    });
});



});


let selectedVoucher = null;

function selectVoucher(type) {

    const voucherText = document.getElementById("selected-voucher");

    if (type === "freeship") {
        selectedVoucher = {
            code: "FREESHIP",
            type: "freeship"
        };

        voucherText.innerText = "Freeship";
    }

    if (type === "discount10") {
        selectedVoucher = {
            code: "DISCOUNT10",
            type: "percent",
            value: 10
        };

        voucherText.innerText = "Giảm 10%";
    }

    voucherText.classList.remove("d-none");

    // đóng modal
    const modal = bootstrap.Modal.getInstance(
        document.getElementById("voucherModal")
    );
    modal.hide();
}
