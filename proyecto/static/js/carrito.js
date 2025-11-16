/**
 * Gestiona la lógica del carrito de compras almacenado en localStorage.
 */

// --- FUNCIONES PRINCIPALES DEL CARRITO ---

/**
 * Añade un producto al carrito o incrementa su cantidad si ya existe.
 */
function añadirCarrito(producto) {
    const productos = obtenerCarrito();

    const productoExistente = productos.find(
        p => p.id === producto.id &&
             p.talla === producto.talla &&
             p.color === producto.color &&
             p.texto === producto.texto
    );

    if (productoExistente) {
        productoExistente.cantidad += 1;
    } else {
        const precioNumerico = parseFloat(String(producto.precio).replace(",", "."));
        productos.push({ ...producto, precio: precioNumerico, cantidad: 1 });
    }

    guardarCarrito(productos);
    actualizarVistaCarrito();
}

/**
 * Incrementa la cantidad del producto
 */
function incrementar(productoEntrada) {
    const productos = obtenerCarrito();
    const producto = productos.find(
        p => p.id === productoEntrada.id &&
             p.talla === productoEntrada.talla &&
             p.color === productoEntrada.color &&
             p.texto === productoEntrada.texto
             && p.imagen === productoEntrada.imagen
    );

    if (producto) producto.cantidad += 1;

    guardarCarrito(productos);
    actualizarVistaCarrito();
    if(renderCarrito){
        renderCarrito()
    }
}

/**
 * Reduce la cantidad del producto
 */
function decrementar(productoEntrada) {
    let productos = obtenerCarrito();
    const index = productos.findIndex(
        p => p.id === productoEntrada.id &&
             p.talla === productoEntrada.talla &&
             p.color === productoEntrada.color &&
             p.texto === productoEntrada.texto
             && p.imagen === productoEntrada.imagen
    );

    if (index !== -1) {
        if (productos[index].cantidad > 1) {
            productos[index].cantidad--;
        } else {
            productos.splice(index, 1);
        }
    }

    guardarCarrito(productos);
    actualizarVistaCarrito();
}

/**
 * Elimina un producto del carrito
 */
function eliminarProducto(productoEntrada) {
    let productos = obtenerCarrito();
    productos = productos.filter(
        p => !(p.id === productoEntrada.id &&
               p.talla === productoEntrada.talla &&
               p.color === productoEntrada.color &&
               p.texto === productoEntrada.texto)
               && p.imagen === productoEntrada.imagen
    );

    guardarCarrito(productos);
    actualizarVistaCarrito();
}

/**
 * Actualiza la interfaz del carrito
 */
function actualizarVistaCarrito() {
    const productos = obtenerCarrito();
    const carritoContenido = document.getElementById('carrito-contenido');
    const botonCarrito = document.getElementById('carritoDropdown');

    carritoContenido.innerHTML = '';
    let totalSuma = 0;

    if (productos.length === 0) {
        carritoContenido.innerHTML = '<p class="text-center text-muted m-0">El carrito está vacío.</p>';
    } else {
        productos.forEach((producto, index) => {
            const subtotal = producto.precio * producto.cantidad;
            totalSuma += subtotal;

            

            const itemHTML = `
            <div class="producto-item d-flex align-items-center gap-2" data-index="${index}">
        
                <div class="producto-info flex-grow-1">
                    <strong>${producto.nombre}</strong><br>
        
                    <small>Talla: ${producto.talla}</small><br>
                    <small>Color: ${producto.color}</small><br>
        
                    <small>Imagen: ${producto.imagen}</small><br>
        
                    ${producto.texto ? `<small>Texto: "${producto.texto}"</small><br>` : ""}
        
                    <small class="fw-bold">${subtotal.toFixed(2)} €</small>
                </div>
        
                <div class="producto-controles text-end">
                    <button class="btn btn-sm btn-outline-secondary btn-sumar" data-index="${index}">+</button>
                    <span class="cantidad">${producto.cantidad}</span>
                    <button class="btn btn-sm btn-outline-secondary btn-restar" data-index="${index}">-</button>
                    <button class="btn btn-sm btn-outline-danger ms-2 btn-eliminar" data-index="${index}">✕</button>
                </div>
        
            </div>
        `;
        

            carritoContenido.innerHTML += itemHTML;
        });

        carritoContenido.innerHTML += `
            <hr>
            <div class='text-end fw-bold mb-2'>Total: ${totalSuma.toFixed(2)} €</div>
            <a class="btn btn-primary w-100" href="/pedidos">Continuar compra</button>
        `;
    }

    botonCarrito.textContent = `🛒 Carrito (${productos.length})`;
}

/**
 * Delegación de eventos para botones del carrito
 */
document.addEventListener('click', (e) => {
    if (e.target.matches('.btn-sumar')) {
        const index = e.target.dataset.index;
        const productos = obtenerCarrito();
        incrementar(productos[index]);
        if(renderCarrito){
            renderCarrito()
        }
    }

    if (e.target.matches('.btn-restar')) {
        const index = e.target.dataset.index;
        const productos = obtenerCarrito();
        decrementar(productos[index]);
    }

    if (e.target.matches('.btn-eliminar')) {
        const index = e.target.dataset.index;
        const productos = obtenerCarrito();
        eliminarProducto(productos[index]);
    }
});
function renderCarrito(){
    const productos = obtenerCarrito();
    const lista = document.getElementById("lista-productos");
    if(!lista){
        return ;
    }
    lista.innerHTML = "";
    let total = 0;

    if (productos.length === 0) {
        lista.innerHTML = "<p class='text-muted'>No hay productos en el carrito.</p>";
        return;
    }

    productos.forEach((producto, index) => {
        const subtotal = producto.precio * producto.cantidad;
        total += subtotal;

        lista.innerHTML += `
            <div class="producto-item d-flex justify-content-between align-items-center" data-index="${index}">
                
                <div class="mini-info">
                    <strong>${producto.nombre}</strong>
                    <small>Talla: ${producto.talla}</small>
                    <small>Color: ${producto.color}</small>
                    ${producto.imagen ? `<small>Imagen: ${producto.imagen}</small>` : ""}
                    ${producto.texto ? `<small>Texto: "${producto.texto}"</small>` : ""}
                    <small class="fw-bold">${subtotal.toFixed(2)} €</small>
                </div>

                <div class="text-end">
                     <button class="btn btn-sm btn-outline-secondary btn-sumar-pedido" data-index="${index}">+</button>
            <span class="cantidad">${producto.cantidad}</span>
            <button class="btn btn-sm btn-outline-secondary btn-restar-pedido" data-index="${index}">-</button>
            <button class="btn btn-sm btn-outline-danger ms-2 btn-eliminar-pedido" data-index="${index}">✕</button>
                </div>

            </div>
        `;
    });

    lista.innerHTML += `
        <hr>
        <div class="text-end fw-bold">TOTAL: ${total.toFixed(2)} €</div>
    `;

}
// --- HELPERS ---
const obtenerCarrito = () => JSON.parse(localStorage.getItem('carrito')) || [];
const guardarCarrito = (productos) => localStorage.setItem('carrito', JSON.stringify(productos));

// --- INICIALIZACIÓN ---
document.addEventListener('DOMContentLoaded', actualizarVistaCarrito);

