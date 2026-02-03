document.addEventListener("DOMContentLoaded", () => {

    const BASE_PRICES = [
        349000,
        549000,
        899000,
        1299000,
        2199000
    ];

    const cards = document.querySelectorAll(".flower-card");

    cards.forEach((card, index) => {

        const price = parseInt(card.dataset.price);
        const stock = parseInt(card.dataset.stock);

        // ❌ hết hàng
        if (stock === 0) return;

        // =====================
        // TÌM GIÁ GỐC
        // =====================
        let original = null;

        for (let base of BASE_PRICES) {
            if (price < base) {
                original = base;
                break;
            }
        }

        if (!original) return;

        // =====================
        // TÍNH % GIẢM
        // =====================
        const percent = Math.round(
            (original - price) / original * 100
        );

        if (percent <= 0) return;

        // =====================
        // BADGE %
        // =====================
        const badge = document.createElement("div");
        badge.className = "discount-percent";
        badge.innerHTML = `-${percent}<span>%</span>`;
        card.appendChild(badge);

        // =====================
        // GIÁ GỐC (GẠCH)
        // =====================
        const priceBlock = card.querySelector(".card-body .price")

        if (priceBlock) {
            priceBlock.innerHTML = `
                <div class="old-price">
                    ${formatMoney(original)} VND
                </div>
                <div class="new-price">
                    ${formatMoney(price)} VND
                </div>
            `;
        }

        // =====================
        // HOT cho 6 card đầu
        // =====================
        if (index < 6) {
            const hot = document.createElement("div");
            hot.className = "hot-badge";
            hot.innerText = "🔥 HOT";
            card.appendChild(hot);
        }

    });
});

function formatMoney(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
}
