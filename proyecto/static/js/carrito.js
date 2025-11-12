/**
 * Gestiona la lógica del carrito de compras almacenado en localStorage.
 */

// --- FUNCIONES PRINCIPALES DEL CARRITO ---

/**
 * Añade un producto al carrito o incrementa su cantidad si ya existe.
 * @param {object} producto - El objeto del producto a añadir.
 */
function añadirCarrito(producto) {
    const productos = obtenerCarrito();
    // Un producto es único por su ID y su talla
    const productoExistente = productos.find(p => p.id === producto.id && p.talla === producto.talla);

    if (productoExistente) {
        productoExistente.cantidad += 1;
    } else {
        // Aseguramos que el precio sea un número flotante
        const precioNumerico = parseFloat(String(producto.precio).replace(",", "."));
        productos.push({ ...producto, precio: precioNumerico, cantidad: 1, talla: producto.talla });
    }

    guardarCarrito(productos);
    actualizarVistaCarrito();
}

/**
 * Incrementa la cantidad de un producto en el carrito.
 * @param {string} id - El ID del producto.
 * @param {string} talla - La talla del producto.
 */
function incrementar(id, talla) {
    const productos = obtenerCarrito();
    const producto = productos.find(p => p.id == id && p.talla === talla);
    if (producto) {
        producto.cantidad += 1;
    }
    guardarCarrito(productos);
    actualizarVistaCarrito();
}

/**
 * Decrementa la cantidad de un producto. Si la cantidad llega a 0, lo elimina.
 * @param {string} id - El ID del producto.
 * @param {string} talla - La talla del producto.
 */
function decrementar(id, talla) {
    let productos = obtenerCarrito();
    const index = productos.findIndex(p => p.id == id && p.talla === talla);

    if (index !== -1) {
        if (productos[index].cantidad > 1) {
            productos[index].cantidad -= 1;
        } else {
            // Si la cantidad es 1, eliminamos el producto
            productos.splice(index, 1);
        }
    }

    guardarCarrito(productos);
    actualizarVistaCarrito();
}

/**
 * Elimina un producto completamente del carrito.
 * @param {string} id - El ID del producto.
 * @param {string} talla - La talla del producto.
 */
function eliminarProducto(id, talla) {
    let productos = obtenerCarrito();
    productos = productos.filter(p => !(p.id == id && p.talla === talla));
    guardarCarrito(productos);
    actualizarVistaCarrito();
}

/**
 * Actualiza la interfaz de usuario del carrito con los datos de localStorage.
 */
function actualizarVistaCarrito() {
    const productos = obtenerCarrito();
    const carritoContenido = document.getElementById('carrito-contenido');
    const botonCarrito = document.getElementById('carritoDropdown');

    carritoContenido.innerHTML = ''; // Limpiar contenido previo
    let totalSuma = 0;

    if (productos.length === 0) {
        carritoContenido.innerHTML = '<p class="text-center text-muted m-0">El carrito está vacío.</p>';
    } else {
        productos.forEach(producto => {
            const subtotal = producto.precio * producto.cantidad;
            totalSuma += subtotal;
            const itemHTML = `
                <div class="producto-item">
                    <div class="producto-info">
                        <strong>${producto.nombre}</strong> (Talla: ${producto.talla})
                        <small>${subtotal.toFixed(2)} €</small>
                    </div>
                    <div class="producto-controles">
                        <button class="btn btn-sm btn-outline-secondary" onclick="incrementar('${producto.id}', '${producto.talla}')">+</button>
                        <span class="cantidad">${producto.cantidad}</span>
                        <button class="btn btn-sm btn-outline-secondary" onclick="decrementar('${producto.id}', '${producto.talla}')">-</button>
                        <button class="btn btn-sm btn-outline-danger ms-2" onclick="eliminarProducto('${producto.id}', '${producto.talla}')">✕</button>
                    </div>
                </div>`;
            carritoContenido.innerHTML += itemHTML;
        });

        carritoContenido.innerHTML += `<hr><div class='text-end fw-bold mb-2'>Total: ${totalSuma.toFixed(2)} €</div>`;
        carritoContenido.innerHTML += `<button class="btn btn-primary w-100">Continuar compra</button>`;
    }

    botonCarrito.textContent = `🛒 Carrito (${productos.length})`;
}

// --- HELPERS ---
const obtenerCarrito = () => JSON.parse(localStorage.getItem('carrito')) || [];
const guardarCarrito = (productos) => localStorage.setItem('carrito', JSON.stringify(productos));

// --- EVENT LISTENERS ---
document.addEventListener('DOMContentLoaded', () => {
    actualizarVistaCarrito();

    // Evita que el menú del carrito se cierre al hacer clic dentro de él
    document.getElementById('carrito-contenido').addEventListener('click', (event) => {
        event.stopPropagation();
    });
});