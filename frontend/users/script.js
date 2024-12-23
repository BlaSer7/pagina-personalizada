// Inicializar el mapa
function initMap() {
    const location = { lat: -18.4965278, lng: -64.1054444 };
    const map = new google.maps.Map(document.getElementById('map'), {
        zoom: 15,
        center: location,
    });
    const marker = new google.maps.Marker({
        position: location,
        map: map,
    });
}

// Carrito de compras
const cart = [];
const cartCount = document.getElementById("cart-count");
const cartModal = document.getElementById("cart-modal");
const cartItems = document.getElementById("cart-items");
const cartTotal = document.getElementById("cart-total");
const closeCart = document.getElementById("close-cart");

document.querySelectorAll(".add-to-cart-btn").forEach(button => {
    button.addEventListener("click", () => {
        const product = button.dataset.product;
        const price = parseFloat(button.dataset.price);

        addToCart(product, price);
    });
});

function addToCart(product, price) {
    const existingItem = cart.find(item => item.product === product);

    if (existingItem) {
        existingItem.quantity++;
    } else {
        cart.push({ product, price, quantity: 1 });
    }

    updateCart();
}

function removeFromCart(product) {
    const itemIndex = cart.findIndex(item => item.product === product);

    if (itemIndex !== -1) {
        const item = cart[itemIndex];
        if (item.quantity > 1) {
            item.quantity--;
        } else {
            cart.splice(itemIndex, 1);
        }
    }

    updateCart();
}

function updateCart() {
    cartCount.textContent = cart.reduce((acc, item) => acc + item.quantity, 0);

    cartItems.innerHTML = "";
    let total = 0;

    cart.forEach(item => {
        const li = document.createElement("li");
        li.innerHTML = `
            ${item.product} - $${item.price} x ${item.quantity} = $${(item.price * item.quantity).toFixed(2)}
            <button class="remove-btn" data-product="${item.product}">Eliminar</button>
        `;
        cartItems.appendChild(li);

        total += item.price * item.quantity;
    });

    cartTotal.textContent = total.toFixed(2);

    // Añadir eventos a los botones de eliminar
    document.querySelectorAll(".remove-btn").forEach(button => {
        button.addEventListener("click", () => {
            const product = button.dataset.product;
            removeFromCart(product);
        });
    });
}

document.getElementById("cart-icon").addEventListener("click", () => {
    cartModal.style.display = "block";
});

closeCart.addEventListener("click", () => {
    cartModal.style.display = "none";
});

// Llamar al mapa y carrito cuando la página cargue
window.onload = () => {
    initMap();
};
