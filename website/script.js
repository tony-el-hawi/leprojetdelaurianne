// API Configuration
const API_CONFIG = {
    apiId: 'c3hdm1rt47',
    homeAssistantUrl: 'http://192.168.0.61:8123/api/services/light/toggle',
    entityId: 'light.headlight'
};

API_CONFIG.baseUrl = `http://localhost:5080/items`;
API_CONFIG.ordersUrl = `http://localhost:5080/orders`;
API_CONFIG.photoUrl = `http://localhost:5080/`;

// State Management
let clothingItems = [];
let cart = [];
let activeFilters = {
    categories: [],
    colors: [],
    sizes: [],
    search: ''
};
let editMode = false;
let deleteMode = false;
let editingItemId = null;

// Home Assistant Token Management
function getHomeAssistantToken() {
    return localStorage.getItem('homeAssistantToken');
}

function setHomeAssistantToken(token) {
    localStorage.setItem('homeAssistantToken', token);
}

function promptForToken() {
    return null;
}

function updateHomeAssistantToken() {
    const currentToken = getHomeAssistantToken();
    const message = currentToken ? 
        'Modifier votre token Home Assistant:' : 
        'Configurer votre token Home Assistant:';
    
    const token = prompt(message, currentToken || '');
    if (token && token !== currentToken) {
        setHomeAssistantToken(token);
        showToast('Token mis à jour!');
    }
    toggleMenu();
}

// Initialization
async function init() {
    showLoading();
    
    if (!getHomeAssistantToken()) {
        setTimeout(() => {
            promptForToken();
        }, 1000);
    }
    
    await loadItems();
    buildFilterOptions();
    displayItems();
    updateCartDisplay();
    hideLoading();
}

// Data Loading
async function loadItems() {
    try {
        const response = await fetch(API_CONFIG.baseUrl);
        if (response.ok) {
            clothingItems = await response.json();
        } else {
            showToast('Erreur de chargement');
        }
    } catch (error) {
        console.error('Error loading items:', error);
        showToast('Erreur de connexion');
    }
}

// Navigation
function showTab(tabName) {
    // Update nav buttons
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    
    // Update content
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.getElementById(tabName).classList.add('active');
    
    if (tabName === 'panier') {
        updateCartDisplay();
    }
}

// Main Menu
function toggleMenu() {
    const menu = document.getElementById('main-menu');
    const btn = document.getElementById('menu-btn');
    
    if (editMode || deleteMode) {
        resetToNormalMode();
        return;
    }
    
    menu.classList.toggle('open');
    btn.classList.toggle('active');
}

// Search and Filters
function handleSearch() {
    const searchTerm = document.getElementById('search-input').value.toLowerCase();
    activeFilters.search = searchTerm;
    displayItems();
}

function filterByCategory(category) {
    // Update quick filter buttons
    document.querySelectorAll('.quick-filter').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Apply filter
    if (category === 'all') {
        activeFilters.categories = [];
    } else {
        activeFilters.categories = [category];
    }
    displayItems();
}

function openFilters() {
    document.getElementById('filter-modal').classList.add('show');
}

function closeFilters() {
    document.getElementById('filter-modal').classList.remove('show');
}

function buildFilterOptions() {
    const categories = {};
    const colors = {};
    const sizes = {};
    
    clothingItems.forEach(item => {
        categories[item.category] = (categories[item.category] || 0) + 1;
        colors[item.color] = (colors[item.color] || 0) + 1;
        sizes[item.size] = (sizes[item.size] || 0) + 1;
    });
    
    // Build category filters
    const categoryFilters = document.getElementById('category-filters');
    categoryFilters.innerHTML = Object.keys(categories)
        .map(category => `
            <div class="filter-chip ${activeFilters.categories.includes(category) ? 'active' : ''}" 
                 onclick="toggleFilter('categories', '${category}')">
                ${category}
            </div>
        `).join('');
    
    // Build color filters
    const colorFilters = document.getElementById('color-filters');
    colorFilters.innerHTML = Object.keys(colors)
        .map(color => `
            <div class="color-chip ${activeFilters.colors.includes(color) ? 'active' : ''}" 
                 style="background-color: ${getColorHex(color)}"
                 onclick="toggleFilter('colors', '${color}')">
            </div>
        `).join('');
    
    // Build size filters
    const sizeFilters = document.getElementById('size-filters');
    sizeFilters.innerHTML = Object.keys(sizes)
        .map(size => `
            <div class="filter-chip ${activeFilters.sizes.includes(size) ? 'active' : ''}" 
                 onclick="toggleFilter('sizes', '${size}')">
                ${size}
            </div>
        `).join('');
}

function toggleFilter(filterType, value) {
    const index = activeFilters[filterType].indexOf(value);
    if (index > -1) {
        activeFilters[filterType].splice(index, 1);
    } else {
        activeFilters[filterType].push(value);
    }
    buildFilterOptions();
}

function applyFilters() {
    displayItems();
    closeFilters();
    showToast('Filtres appliqués');
}

function resetFilters() {
    activeFilters = { categories: [], colors: [], sizes: [], search: '' };
    document.getElementById('search-input').value = '';
    buildFilterOptions();
    displayItems();
    showToast('Filtres réinitialisés');
}

function getColorHex(colorName) {
    const colorMap = {
        'Rouge': '#FF4757',
        'Bleu': '#3742FA',
        'Vert': '#2ED573',
        'Jaune': '#FFA502',
        'Rose': '#FF6B9D',
        'Blanc': '#F1F2F6',
        'Noir': '#2F3542',
        'Gris': '#A4B0BE',
        'Beige': '#F1C40F',
        'Marron': '#8B4513',
        'Kaki': '#6AB04C',
        'Marine': '#1E3799',
        'Camel': '#D2691E'
    };
    return colorMap[colorName] || '#DDD';
}

function getEmojiForCategory(category) {
    const emojiMap = {
        'Jupes': '👗',
        'Shorts': '🩳',
        'Jeans': '👖',
        'Blouses': '👚',
        'Chemises': '👔'
    };
    return emojiMap[category] || '👕';
}

// Item Display
function displayItems() {
    const grid = document.getElementById('items-grid');
    let filteredItems = clothingItems;
    
    // Apply search filter
    if (activeFilters.search) {
        filteredItems = filteredItems.filter(item => 
            item.name.toLowerCase().includes(activeFilters.search) ||
            item.category.toLowerCase().includes(activeFilters.search) ||
            item.color.toLowerCase().includes(activeFilters.search)
        );
    }
    
    // Apply category filter
    if (activeFilters.categories.length > 0) {
        filteredItems = filteredItems.filter(item => 
            activeFilters.categories.includes(item.category)
        );
    }
    
    // Apply color filter
    if (activeFilters.colors.length > 0) {
        filteredItems = filteredItems.filter(item => 
            activeFilters.colors.includes(item.color)
        );
    }
    
    // Apply size filter
    if (activeFilters.sizes.length > 0) {
        filteredItems = filteredItems.filter(item => 
            activeFilters.sizes.includes(item.size)
        );
    }
    
    if (filteredItems.length === 0) {
        grid.innerHTML = `
            <div class="empty-state" style="grid-column: 1 / -1;">
                <div class="empty-icon">Aucun résultat</div>
                <h3>Aucun article trouvé</h3>
                <p>Essayez de modifier vos filtres</p>
            </div>
        `;
        return;
    }
    
    grid.innerHTML = filteredItems.map(item => {
        const inCart = isInCart(item.id);
        const imageContent = item.photo 
            ? `<img src="${API_CONFIG.photoUrl}${item.photo}" alt="${item.name}">`
            : `<div class="item-placeholder">${item.category.charAt(0)}</div>`;
        
        const cardClass = editMode ? 'item-card edit-mode' : deleteMode ? 'item-card delete-mode' : 'item-card';
        const cardClick = editMode ? `editItem('${item.id}')` : deleteMode ? '' : '';
        
        return `
            <div class="${cardClass}" onclick="${cardClick}">
                <button class="delete-btn ${deleteMode ? 'show' : ''}" onclick="deleteItem('${item.id}'); event.stopPropagation();">×</button>
                <button class="edit-btn-item ${editMode ? 'show' : ''}" onclick="editItem('${item.id}'); event.stopPropagation();">-</button>
                <div class="item-image">${imageContent}</div>
                <div class="item-info">
                    <div class="item-name">${item.name}</div>
                    <div class="item-details">${item.category} • ${item.color} • ${item.size}</div>
                    <button class="add-btn" ${inCart ? 'disabled' : ''} onclick="addToCart('${item.id}'); event.stopPropagation();">
                        ${inCart ? 'Ajouté' : 'Ajouter'}
                    </button>
                </div>
            </div>
        `;
    }).join('');
}

// Cart Management
function isInCart(itemId) {
    return cart.some(item => item.id === itemId);
}

function addToCart(itemId) {
    if (isInCart(itemId) || editMode || deleteMode) return;
    
    const item = clothingItems.find(i => i.id === itemId);
    if (item) {
        cart.push(item);
        updateCartBadge();
        displayItems();
        showToast(`${item.name} ajouté au panier`);
        
        // Haptic feedback on mobile
        if (navigator.vibrate) {
            navigator.vibrate(50);
        }
    }
}

function removeFromCart(itemId) {
    const index = cart.findIndex(item => item.id === itemId);
    if (index > -1) {
        const item = cart[index];
        cart.splice(index, 1);
        updateCartDisplay();
        updateCartBadge();
        displayItems();
        showToast(`${item.name} retiré du panier`);
    }
}

function updateCartBadge() {
    const badge = document.getElementById('cart-badge');
    if (cart.length > 0) {
        badge.textContent = cart.length;
        badge.classList.add('show');
    } else {
        badge.classList.remove('show');
    }
}

function updateCartDisplay() {
    const cartItems = document.getElementById('cart-items');
    const cartEmpty = document.getElementById('cart-empty');
    const cartActions = document.getElementById('cart-actions');
    
    if (cart.length === 0) {
        cartItems.style.display = 'none';
        cartActions.style.display = 'none';
        cartEmpty.style.display = 'block';
    } else {
        cartEmpty.style.display = 'none';
        cartItems.style.display = 'block';
        cartActions.style.display = 'block';
        
        cartItems.innerHTML = cart.map(item => {
            const imageContent = item.photo 
                ? `<img src="${item.photo}" alt="${item.name}" style="width: 100%; height: 100%; object-fit: cover; border-radius: 16px;">`
                : `<div class="item-placeholder">${item.category.charAt(0)}</div>`;
            
            return `
                <div class="cart-item">
                    <div class="cart-item-image">${imageContent}</div>
                    <div class="cart-item-info">
                        <div class="cart-item-name">${item.name}</div>
                        <div class="cart-item-details">${item.category} • ${item.color} • ${item.size}</div>
                    </div>
                    <button class="remove-btn" onclick="removeFromCart('${item.id}')">×</button>
                </div>
            `;
        }).join('');
    }
}

// Admin Functions
function resetToNormalMode() {
    editMode = false;
    deleteMode = false;
    editingItemId = null;
    
    const menuBtn = document.getElementById('menu-btn');
    const mainMenu = document.getElementById('main-menu');
    
    menuBtn.classList.remove('active');
    mainMenu.classList.remove('open');
    
    displayItems();
    showToast('Mode normal activé');
}

function setEditMode() {
    editMode = true;
    deleteMode = false;
    
    const mainMenu = document.getElementById('main-menu');
    mainMenu.classList.remove('open');
    
    displayItems();
    showToast('Mode édition activé');
}

function setDeleteMode() {
    editMode = false;
    deleteMode = true;
    
    const mainMenu = document.getElementById('main-menu');
    mainMenu.classList.remove('open');
    
    displayItems();
    showToast('Mode suppression activé');
}

// Item Management
function showAddItemModal() {
    document.getElementById('add-item-modal').classList.add('show');
    document.getElementById('main-menu').classList.remove('open');
}

function closeAddItemModal() {
    document.getElementById('add-item-modal').classList.remove('show');
    document.getElementById('add-item-form').reset();
    document.getElementById('photo-preview').innerHTML = '';
}

function editItem(itemId) {
    if (!editMode) return;
    
    const item = clothingItems.find(i => i.id === itemId);
    if (item) {
        editingItemId = itemId;
        document.getElementById('edit-item-name').value = item.name;
        document.getElementById('edit-item-category').value = item.category;
        document.getElementById('edit-item-color').value = item.color;
        document.getElementById('edit-item-size').value = item.size;
        
        const preview = document.getElementById('edit-photo-preview');
        if (item.photo) {
            preview.innerHTML = `<img src="${item.photo}" alt="Preview" style="max-width: 100px; border-radius: 8px;">`;
        } else {
            preview.innerHTML = '';
        }
        
        document.getElementById('edit-item-modal').classList.add('show');
    }
}

function closeEditItemModal() {
    document.getElementById('edit-item-modal').classList.remove('show');
    document.getElementById('edit-item-form').reset();
    document.getElementById('edit-photo-preview').innerHTML = '';
    editingItemId = null;
}

async function deleteItem(itemId) {
    if (!deleteMode) return;
    
    const item = clothingItems.find(i => i.id === itemId);
    if (!item) return;
    
    if (confirm(`Êtes-vous sûr de vouloir supprimer "${item.name}" ?`)) {
        try {
            const response = await fetch(`${API_CONFIG.baseUrl}/${itemId}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                await loadItems();
                buildFilterOptions();
                
                // Remove from cart if present
                cart = cart.filter(cartItem => cartItem.id !== itemId);
                updateCartDisplay();
                updateCartBadge();
                
                displayItems();
                showToast(`${item.name} supprimé`);
            } else {
                showToast('Erreur lors de la suppression');
            }
        } catch (error) {
            console.error('Error deleting item:', error);
            showToast('Erreur de connexion');
        }
    }
}



async function addNewItem(event) {
    event.preventDefault();
    
    const name = document.getElementById('item-name').value;
    const category = document.getElementById('item-category').value;
    const color = document.getElementById('item-color').value;
    const size = document.getElementById('item-size').value;
    const photoFile = document.getElementById('item-photo').files[0];
    
    const newItem = {
        name: name,
        category: category,
        emoji: getEmojiForCategory(category),
        color: color,
        size: size,
        photo: photoFile ? await fileToBase64(photoFile) : null
    };
    
    try {
        const response = await fetch(API_CONFIG.baseUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(newItem)
        });
        
        if (response.ok) {
            await loadItems();
            buildFilterOptions();
            closeAddItemModal();
            displayItems();
            showToast(`${name} ajouté au catalogue`);
        } else {
            showToast('Erreur lors de l\'ajout');
        }
    } catch (error) {
        console.error('Error creating item:', error);
        showToast('Erreur de connexion');
    }
}

async function updateItem(event) {
    event.preventDefault();
    if (!editingItemId) return;
    
    const name = document.getElementById('edit-item-name').value;
    const category = document.getElementById('edit-item-category').value;
    const color = document.getElementById('edit-item-color').value;
    const size = document.getElementById('edit-item-size').value;
    const photoFile = document.getElementById('edit-item-photo').files[0];
    
    const updatedItem = {
        name: name,
        category: category,
        emoji: getEmojiForCategory(category),
        color: color,
        size: size,
        photo: photoFile ? await fileToBase64(photoFile) : null
    };
    
    try {
        const response = await fetch(`${API_CONFIG.baseUrl}/${editingItemId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updatedItem)
        });
        
        if (response.ok) {
            await loadItems();
            buildFilterOptions();
            
            // Update cart item if present
            const cartIndex = cart.findIndex(item => item.id === editingItemId);
            if (cartIndex > -1) {
                cart[cartIndex] = { ...cart[cartIndex], ...updatedItem };
                updateCartDisplay();
            }
            
            closeEditItemModal();
            displayItems();
            showToast(`${name} modifié`);
        } else {
            showToast('Erreur lors de la modification');
        }
    } catch (error) {
        console.error('Error updating item:', error);
        showToast('Erreur de connexion');
    }
}

function fileToBase64(file) {
    return new Promise((resolve) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.readAsDataURL(file);
    });
}

// Order Management
async function placeOrder() {
    if (cart.length === 0) return;
    
    showLoading();
    
    try {
        // Save order to database
        const orderResponse = await fetch(API_CONFIG.ordersUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ items: cart })
        });
        
        // Call Home Assistant API
        const token = getHomeAssistantToken();
        if (token) {
            const response = await fetch(API_CONFIG.homeAssistantUrl, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    "entity_id": API_CONFIG.entityId
                })
            });
        }
        
        hideLoading();
        showSuccessModal();
        
        // Haptic feedback
        if (navigator.vibrate) {
            navigator.vibrate([100, 50, 100]);
        }
        
    } catch (error) {
        console.error('Order error:', error);
        hideLoading();
        showToast('Erreur lors de la commande');
    }
}

// Order History
async function showOrderHistory() {
    toggleMenu();
    
    try {
        const response = await fetch(API_CONFIG.ordersUrl);
        if (response.ok) {
            const orders = await response.json();
            displayOrderHistory(orders);
        }
    } catch (error) {
        console.error('Error loading orders:', error);
        showToast('Erreur de chargement');
    }
}

function displayOrderHistory(orders) {
    const modal = document.getElementById('order-history-modal');
    const list = document.getElementById('order-history-list');
    
    if (orders.length === 0) {
        list.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">Historique vide</div>
                <h3>Aucune commande</h3>
                <p>Vos commandes apparaîtront ici</p>
            </div>
        `;
    } else {
        // Sort orders by timestamp (latest first) and take only last 3
        orders.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
        const recentOrders = orders.slice(0, 3);
        
        list.innerHTML = recentOrders.map(order => {
            const date = new Date(order.timestamp).toLocaleString('fr-FR', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
                timeZone: 'Europe/Paris'
            });
            
            const itemsHtml = order.items.map(item => {
                const imageContent = item.photo 
                    ? `<img src="${item.photo}" alt="${item.name}" style="width: 100%; height: 100%; object-fit: cover; border-radius: 4px;">`
                    : `<div class="item-placeholder">${item.category.charAt(0)}</div>`;
                
                return `
                    <div class="order-item-card">
                        <div class="order-item-image">${imageContent}</div>
                        <span>${item.name}</span>
                    </div>
                `;
            }).join('');
            
            return `
                <div class="order-item">
                    <div class="order-header">
                        <span class="order-date">${date}</span>
                        <span class="order-status">Livrée</span>
                    </div>
                    <div class="order-items">${itemsHtml}</div>
                </div>
            `;
        }).join('');
        
        // Add "Voir plus" button if there are more than 3 orders
        if (orders.length > 3) {
            list.innerHTML += `
                <div class="voir-plus-container">
                    <button class="voir-plus-btn" onclick="window.open('orders.html', '_blank')">
                        Voir plus
                    </button>
                </div>
            `;
        }
    }
    
    modal.classList.add('show');
}

function closeOrderHistory() {
    document.getElementById('order-history-modal').classList.remove('show');
}

// Modals
function showSuccessModal() {
    document.getElementById('success-modal').classList.add('show');
}

function closeSuccessModal() {
    document.getElementById('success-modal').classList.remove('show');
    
    // Clear cart and refresh
    cart = [];
    updateCartDisplay();
    updateCartBadge();
    displayItems();
    showTab('catalogue');
}

// UI Helpers
function showLoading() {
    const grid = document.getElementById('items-grid');
    grid.innerHTML = `
        <div class="loading" style="grid-column: 1 / -1;">
            <div class="spinner"></div>
        </div>
    `;
}

function hideLoading() {
    // Loading will be replaced by displayItems()
}

function showToast(message) {
    // Create toast element
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.style.cssText = `
        position: fixed;
        top: 100px;
        left: 50%;
        transform: translateX(-50%) translateY(-20px);
        background: rgba(0,0,0,0.9);
        color: white;
        padding: 14px 24px;
        border-radius: 30px;
        font-size: 14px;
        font-weight: 500;
        z-index: 10000;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
        opacity: 0;
        transition: all 0.3s ease;
    `;
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    // Animate in
    setTimeout(() => {
        toast.style.opacity = '1';
        toast.style.transform = 'translateX(-50%) translateY(0)';
    }, 10);
    
    // Remove after 3 seconds
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(-50%) translateY(-20px)';
        setTimeout(() => {
            if (document.body.contains(toast)) {
                document.body.removeChild(toast);
            }
        }, 300);
    }, 3000);
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    init();
    
    // Form event listeners
    document.getElementById('add-item-form').addEventListener('submit', addNewItem);
    document.getElementById('edit-item-form').addEventListener('submit', updateItem);
    document.getElementById('planifier-form').addEventListener('submit', submitPlanifierForm);
    
    // Photo preview handlers
    document.getElementById('item-photo').addEventListener('change', function(e) {
        const file = e.target.files[0];
        const preview = document.getElementById('photo-preview');
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                preview.innerHTML = `<img src="${e.target.result}" alt="Preview" style="max-width: 100px; border-radius: 8px;">`;
            };
            reader.readAsDataURL(file);
        } else {
            preview.innerHTML = '';
        }
    });
    
    document.getElementById('edit-item-photo').addEventListener('change', function(e) {
        const file = e.target.files[0];
        const preview = document.getElementById('edit-photo-preview');
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                preview.innerHTML = `<img src="${e.target.result}" alt="Preview" style="max-width: 100px; border-radius: 8px;">`;
            };
            reader.readAsDataURL(file);
        } else {
            preview.innerHTML = '';
        }
    });
});

// Close modals when clicking outside
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal')) {
        e.target.classList.remove('show');
    }
    
    // Close menu when clicking outside
    if (!e.target.closest('.menu-btn') && !e.target.closest('.main-menu')) {
        const mainMenu = document.getElementById('main-menu');
        const menuBtn = document.getElementById('menu-btn');
        if (mainMenu.classList.contains('open') && !editMode && !deleteMode) {
            mainMenu.classList.remove('open');
            menuBtn.classList.remove('active');
        }
    }
});

function showPlanifier() {
    // Masquer les autres sections principales
    document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
    document.getElementById('planifier').style.display = 'flex';
    // Masquer le catalogue et le panier
    document.getElementById('catalogue').classList.remove('active');
    document.getElementById('panier').classList.remove('active');
    // Fermer le menu principal
    document.getElementById('main-menu').classList.remove('open');
}

// Pour revenir à la vue catalogue/panier, il faudra masquer planifier
function hidePlanifier() {
    document.getElementById('planifier').style.display = 'none';
    document.getElementById('catalogue').classList.add('active');
}

// Planifier - gestion des événements
let planifierEvents = [
    {
        id: 1,
        date: '2025-07-04',
        desc: 'Rendez-vous coiffeur',
        items: []
    }
];
let selectedPlanifierId = null;
let editingPlanifierId = null;

function renderPlanifier() {
    const listDiv = document.getElementById('planifier-events-list');
    let html = '';
    // Afficher les tenues dans l'ordre d'ajout (plus récent en haut)
    const sortedTenues = [...planifierEvents].reverse();
    sortedTenues.forEach(tenue => {
        html += `
        <div class="planifier-card" data-id="${tenue.id}" onclick="selectPlanifierEvent(${tenue.id})" style="border:${selectedPlanifierId===tenue.id?'2px solid #667eea':'none'};">
            <div class="planifier-card-content">
                <span class="planifier-icon">🖊️</span>
                <div>
                    <div class="planifier-nom" style="font-weight:600;">${tenue.nom}</div>
                    ${tenue.desc ? `<div class="planifier-desc">${tenue.desc}</div>` : ''}
                </div>
            </div>
            <div class="planifier-card-actions">
                <button class="edit-plan-btn" title="Modifier" onclick="event.stopPropagation();openPlanifierForm(${tenue.id})">&#9998;</button>
                <button class="lamp-plan-btn" title="Allumer" onclick="event.stopPropagation();handleLampForTenue(${tenue.id})" style="margin-left:4px;background:none;border:none;padding:0;font-size:20px;">💡</button>
                <button class="delete-plan-btn" title="Supprimer" onclick="event.stopPropagation();deletePlanifierEvent(${tenue.id})" style="margin-left:4px;">&#128465;</button>
            </div>
        </div>
        `;
        if(selectedPlanifierId===tenue.id){
            html += `<div class='planifier-items'><h4>Vêtements associés :</h4>`;
            if(tenue.items.length===0){
                html += `<div style='color:#6c757d;'>Aucun vêtement sélectionné</div>`;
            }else{
                html += tenue.items.map(itemId=>{
                    const item = clothingItems.find(i=>i.id===itemId);
                    if(!item) return '';
                    return `<div class='planifier-item'>${item.name} <button onclick='removeItemFromEvent(${tenue.id},"${itemId}");event.stopPropagation();' style='margin-left:8px;'>×</button></div>`;
                }).join('');
            }
            html += `<button class='btn-primary' style='margin-top:10px;' onclick='event.stopPropagation();showCatalogueForEvent(${tenue.id})'>Ajouter/modifier les vêtements</button></div>`;
        }
    });
    listDiv.innerHTML = html;
}

function openPlanifierForm(id=null){
    const modal = document.getElementById('planifier-form-modal');
    const form = document.getElementById('planifier-form');
    const title = document.getElementById('planifier-form-title');
    const itemsDiv = document.getElementById('planifier-items-select');
    editingPlanifierId = id;
    let selectedItems = [];
    if(id){
        const tenue = planifierEvents.find(e=>e.id===id);
        if(tenue){
            document.getElementById('planifier-nom').value = tenue.nom;
            document.getElementById('planifier-desc').value = tenue.desc || '';
            selectedItems = tenue.items || [];
            title.textContent = 'Modifier la tenue';
        }
    }else{
        form.reset();
        title.textContent = 'Créer une tenue';
        editingPlanifierId = null;
        selectedItems = [];
    }
    // Générer la liste des vêtements du catalogue avec checkbox, groupés par catégorie
    let html = '';
    if(clothingItems.length === 0){
        html += '<div style="color:#888;">Aucun vêtement dans le catalogue</div>';
    }else{
        const categories = {};
        clothingItems.forEach(item => {
            if (!categories[item.category]) categories[item.category] = [];
            categories[item.category].push(item);
        });
        html += '<div style="max-height:180px;overflow:auto;">';
        Object.keys(categories).forEach(cat => {
            html += `<div style='margin-bottom:10px;'><div style='font-weight:600;margin-bottom:4px;'>${cat}</div><div style='display:flex;flex-wrap:wrap;gap:8px;'>`;
            categories[cat].forEach(item => {
                html += `
                    <label style='display:flex;flex-direction:column;align-items:center;width:90px;cursor:pointer;'>
                        <input type='checkbox' name='planifier-items' value='${item.id}' ${selectedItems.includes(item.id)?'checked':''} style='margin-bottom:4px;'>
                        ${item.photo ? `<img src='${item.photo}' alt='${item.name}' style='width:70px;height:70px;object-fit:cover;border-radius:8px;margin-bottom:4px;'>` : `<div style='width:70px;height:70px;background:#eee;border-radius:8px;margin-bottom:4px;display:flex;align-items:center;justify-content:center;'>${item.category.charAt(0)}</div>`}
                        <span style='font-size:13px;text-align:center;'>${item.name}</span>
                    </label>
                `;
            });
            html += '</div></div>';
        });
        html += '</div>';
    }
    itemsDiv.innerHTML = html;
    modal.classList.add('show');
}

function closePlanifierForm(){
    document.getElementById('planifier-form-modal').classList.remove('show');
    editingPlanifierId = null;
}

function submitPlanifierForm(e){
    e.preventDefault();
    const nom = document.getElementById('planifier-nom').value.trim();
    const desc = document.getElementById('planifier-desc').value;
    const checked = Array.from(document.querySelectorAll("#planifier-items-select input[name='planifier-items']:checked")).map(cb=>cb.value);
    // Vérifier unicité du nom
    let isDuplicate = false;
    if(editingPlanifierId){
        isDuplicate = planifierEvents.some(t => t.nom === nom && t.id !== editingPlanifierId);
    }else{
        isDuplicate = planifierEvents.some(t => t.nom === nom);
    }
    if(isDuplicate){
        showToast('Ce nom de tenue est déjà utilisé. Veuillez en choisir un autre.');
        document.getElementById('planifier-nom').focus();
        return;
    }
    if(editingPlanifierId){
        const tenue = planifierEvents.find(e=>e.id===editingPlanifierId);
        if(tenue){
            tenue.nom = nom;
            tenue.desc = desc;
            tenue.items = checked;
        }
    }else{
        const newId = planifierEvents.length ? Math.max(...planifierEvents.map(e => e.id)) + 1 : 1;
        planifierEvents.push({ id: newId, nom, desc, items: checked });
    }
    closePlanifierForm();
    renderPlanifier();
    editingPlanifierId = null;
}

function deletePlanifierEvent(id) {
    const idx = planifierEvents.findIndex(e => e.id === id);
    if (idx === -1) return;
    const tenue = planifierEvents[idx];
    if (confirm(`Supprimer la tenue « ${tenue.nom} » ?`)) {
        planifierEvents.splice(idx, 1);
        if (selectedPlanifierId === id) selectedPlanifierId = null;
        renderPlanifier();
        showToast('Tenue supprimée');
    }
}

// Affichage initial de la section planifier
if (document.getElementById('planifier-events-list')) {
    renderPlanifier();
}