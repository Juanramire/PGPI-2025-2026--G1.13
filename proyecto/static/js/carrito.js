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

    // Normalizar precios a números (aceptamos coma como separador)
    const precioNumericoRaw = producto.precio !== undefined ? parseFloat(String(producto.precio).toString().replace(",", ".")) : 0;
    const precioOfertaNumericoRaw = producto.precio_oferta !== undefined && producto.precio_oferta !== null && producto.precio_oferta !== ''
        ? parseFloat(String(producto.precio_oferta).toString().replace(",", "."))
        : null;

    // Redondear a 2 decimales y almacenar como Number (no string)
    const precioNumerico = Number((isNaN(precioNumericoRaw) ? 0 : precioNumericoRaw).toFixed(2));
    const precioOfertaNumerico = precioOfertaNumericoRaw !== null && !isNaN(precioOfertaNumericoRaw)
        ? Number(precioOfertaNumericoRaw.toFixed(2))
        : null;

    if (productoExistente) {
        productoExistente.cantidad += 1;
        // Asegurar que el precio y precio_oferta estén guardados como números con 2 decimales
        productoExistente.precio = Number((Number(productoExistente.precio) || 0).toFixed(2));
        if (precioOfertaNumerico !== null) productoExistente.precio_oferta = Number(precioOfertaNumerico.toFixed(2));
    } else {
        productos.push({ ...producto, precio: precioNumerico, precio_oferta: precioOfertaNumerico, cantidad: 1 });
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
        let subtotalOriginal = 0;
        let subtotalWithOffer = 0;
        let descuentoGlobal = 0;
        productos.forEach((producto, index) => {
            const precioOriginal = Number(producto.precio);
            const precioUnit = producto.precio_oferta ? Number(producto.precio_oferta) : precioOriginal;
            const cantidad = Number(producto.cantidad || 1);
            const subtotal = precioUnit * cantidad;
            totalSuma += subtotal;
            subtotalWithOffer += subtotal;
            subtotalOriginal += precioOriginal * cantidad;
            let ahorroItem = 0;
            if (producto.precio_oferta) {
                ahorroItem = (precioOriginal - Number(producto.precio_oferta)) * cantidad;
                descuentoGlobal += ahorroItem;
            }

            const precioShow = producto.precio_oferta ? `<span class="text-danger">${Number(producto.precio_oferta).toFixed(2)} €</span> <small class="text-muted text-decoration-line-through">${precioOriginal.toFixed(2)} €</small>` : `${precioOriginal.toFixed(2)} €`;

            const itemHTML = `
            <div class="producto-item d-flex align-items-center gap-2" data-index="${index}">
        
                <div class="producto-info flex-grow-1">
                    <strong>${producto.nombre}</strong><br>
        
                    <small>Talla: ${producto.talla}</small><br>
                    <small>Color: ${producto.color}</small><br>
                    ${producto.imagen ? `   
                    <small>Imagen: ${producto.imagen}</small><br>
                    ` : ""}
                    ${producto.texto ? `<small>Texto: "${producto.texto}"</small><br>` : ""}
        
                    <small class="fw-bold">${subtotal.toFixed(2)} €</small>
                    ${ahorroItem > 0 ? `<div class="small text-success"> Ahorro: ${ahorroItem.toFixed(2)} €</div>` : ''}
                    <div class="small text-muted"> Precio unidad: ${precioShow}</div>
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

        // Coste inventado del pedido (envío)
        const costeEnvio = subtotalWithOffer >= 50 ? 0 : 4.99;
        const totalFinal = subtotalWithOffer + costeEnvio;

        carritoContenido.innerHTML += `
            <hr>
            <div class='text-end'>
                <div>Subtotal (original): ${subtotalOriginal.toFixed(2)} €</div>
                <div>Descuento: ${descuentoGlobal.toFixed(2)} €</div>
                <div>Coste pedido: ${costeEnvio.toFixed(2)} €</div>
                <div class='fw-bold fs-5'>Total: ${totalFinal.toFixed(2)} €</div>
            </div>
            <a class="btn btn-primary w-100 mt-2" href="/pedidos">Continuar compra</a>
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
        const precioUnit = producto.precio_oferta ? Number(producto.precio_oferta) : Number(producto.precio);
        const cantidad = Number(producto.cantidad || 1);
        const subtotal = precioUnit * cantidad;
        total += subtotal;

        let ahorroItem = 0;
        if (producto.precio_oferta) {
            ahorroItem = (Number(producto.precio) - Number(producto.precio_oferta)) * cantidad;
        }

        lista.innerHTML += `
            <div class="producto-item d-flex justify-content-between align-items-center" data-index="${index}">
                
                <div class="mini-info">
                    <strong>${producto.nombre}</strong>
                    <small>Talla: ${producto.talla}</small>
                    <small>Color: ${producto.color}</small>
                    ${producto.imagen ? `<small>Imagen: ${producto.imagen}</small>` : ""}
                    ${producto.texto ? `<small>Texto: "${producto.texto}"</small>` : ""}
                    <small class="fw-bold">${subtotal.toFixed(2)} €</small>
                    ${ahorroItem > 0 ? `<div class="small text-success">Ahorro: ${ahorroItem.toFixed(2)} €</div>` : ''}
                    <div class="small text-muted">Precio unidad: ${producto.precio_oferta ? Number(producto.precio_oferta).toFixed(2) : Number(producto.precio).toFixed(2)} €</div>
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
const vaciarCarrito = () => {
    localStorage.removeItem('carrito');
    actualizarVistaCarrito();
};
window.vaciarCarrito = vaciarCarrito;

// --- INICIALIZACIÓN ---
document.addEventListener('DOMContentLoaded', actualizarVistaCarrito);

