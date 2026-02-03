const btnOrder = document.getElementById("btn-order");

btnOrder.addEventListener("click", function () {

    const name = document.getElementById("name").value.trim();
    const phone = document.getElementById("phone").value.trim();
    const email = document.getElementById("email").value.trim();
    const address = document.getElementById("address").value.trim();

    let isValid = true;

    clearErrors();

    // ---------- NAME ----------
    if (name.length < 2) {
        showError("name", "Họ tên phải ít nhất 2 ký tự");
        isValid = false;
    }

    // ---------- PHONE ----------
    const phoneRegex = /^0\d{9}$/;
    if (!phoneRegex.test(phone)) {
        showError("phone", "Số điện thoại phải gồm 10 số và bắt đầu bằng 0");
        isValid = false;
    }

    // ---------- EMAIL ----------
    if (email !== "") {
        const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        if (!emailRegex.test(email)) {
            showError("email", "Email không hợp lệ");
            isValid = false;
        }
    }

    // ---------- ADDRESS ----------
    if (address.length < 10) {
        showError("address", "Địa chỉ phải tối thiểu 10 ký tự");
        isValid = false;
    }

    if (!isValid) return;

    // ✅ nếu OK thì checkout
    checkout();
});

function showError(field, message) {
    const el = document.getElementById("err-" + field);
    el.innerText = message;
    el.classList.remove("d-none");
}

function clearErrors() {
    document.querySelectorAll(".text-danger").forEach(e => {
        e.classList.add("d-none");
    });
}

function checkout() {

    const data = {
        name: document.getElementById("name").value.trim(),
        phone: document.getElementById("phone").value.trim(),
        email: document.getElementById("email").value.trim(),
        address: document.getElementById("address").value.trim(),
        note: document.getElementById("note").value.trim(),
        cart: cart,
    };

    fetch("/checkout/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken
        },
        body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(data => {
        alert("🎉 Đặt hàng thành công!");
        localStorage.removeItem("cart");
        window.location.href = "/";
    });
}
