import streamlit as st
import pandas as pd
from datetime import datetime
import json
import re

# Page configuration
st.set_page_config(
    page_title="GenZHub - Fashion E-commerce",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        color: white;
        font-size: 3rem;
        font-weight: 700;
    }
    
    .product-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .product-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.15);
    }
    
    .product-image {
        width: 100%;
        height: 250px;
        object-fit: cover;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    
    .price-tag {
        font-size: 1.8rem;
        color: #FF6B35;
        font-weight: 700;
        margin: 0.5rem 0;
    }
    
    .original-price {
        text-decoration: line-through;
        color: #999;
        font-size: 1.2rem;
        margin-right: 10px;
    }
    
    .discount-badge {
        background: #FF6B35;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 1rem;
    }
    
    .category-header {
        background: linear-gradient(45deg, #4ECDC4, #44A08D);
        color: white;
        padding: 1rem 2rem;
        border-radius: 25px;
        font-size: 1.8rem;
        font-weight: 600;
        margin: 2rem 0 1rem 0;
        text-align: center;
    }
    
    .user-info-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
    }
    
    .cart-item {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #4ECDC4;
    }
    
    .rating {
        color: #FFD700;
        font-size: 1.2rem;
    }
    
    .btn-primary {
        background: linear-gradient(45deg, #667eea, #764ba2) !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 0.7rem 2rem !important;
        font-weight: 600 !important;
    }
    
    .btn-secondary {
        background: linear-gradient(45deg, #FF6B35, #F7931E) !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 0.7rem 2rem !important;
        font-weight: 600 !important;
        color: white !important;
    }
    
    .sidebar .stSelectbox label {
        font-weight: 600;
        color: #333;
    }
    
    .footer {
        background: #2c3e50;
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin-top: 3rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def initialize_session_state():
    if 'user_logged_in' not in st.session_state:
        st.session_state.user_logged_in = False
    if 'user_info' not in st.session_state:
        st.session_state.user_info = {}
    if 'cart' not in st.session_state:
        st.session_state.cart = []
    if 'orders' not in st.session_state:
        st.session_state.orders = []

initialize_session_state()

# Product database with image URLs (using placeholder images)
products_database = {
    "Boys Jeans": {
        "Bell Bottom": [
            {
                "id": 1,
                "name": "Vintage Bell Bottom Jeans",
                "price": 2499,
                "original_price": 3999,
                "description": "Classic 70s inspired bell bottom jeans with authentic vintage wash and flared legs",
                "image": "https://www.qarotmen.com/products/bell-bottom-pants-in-white?srsltid=AfmBOoopgIJKPLRAOdDYPkgg1U3gTuxYQ-Z9QjWdL6vkEt0kA2c4v1w5.jpg",
                "rating": 4.5,
                "sizes": ["S", "M", "L", "XL"],
                "colors": ["Blue", "Black", "Grey"],
                "in_stock": True
            },
            {
                "id": 2,
                "name": "Korean Fit",
                "price": 1999,
                "original_price": 2999,
                "description": "Korean jeans with premium and perfect flare",
                "image": "https://offduty.in/products/men-semi-formal-straight-fit-korean-pants?variant=41485209469025&country=IN&currency=INR&utm_medium=product_sync&utm_source=google&utm_content=sag_organic&utm_campaign=sag_organic&srsltid=AfmBOooaHtl2lf_L5e8Sk2ur3jiA9r879nkiR4GXbpbPbNL_AlPwKME5e84",
                "rating": 4.3,
                "sizes": ["S", "M", "L", "XL"],
                "colors": ["Dark Blue", "Light Blue"],
                "in_stock": True
            }
        ],
        "Loose fit": [
            {
                "id": 3,
                "name": "Loose fit trousers",
                "price": 1999,
                "original_price": 3999,
                "description": "Most loved bottom wear by Gen Z",
                "image": "https://atiire.in/products/korean-baggy-loose-fit-pants-for-men-by-atiire?variant=41572270571604",
                "rating": 4.6,
                "sizes": ["S", "M", "L", "XL", "XXL"],
                "colors": ["Olive", "Black", "Khaki"],
                "in_stock": True
            }
        ],
        "Relaxed Fit": [
            {
                "id": 4,
                "name": "Relaxed Loose Fit Jeans",
                "price": 1999,
                "original_price": 3999,
                "description": "Comfortable loose fit jeans perfect for casual everyday wear",
                "image": "https://www.belowthebelt.com/products/big-guy-baggy-jeans",
                "rating": 4.4,
                "sizes": ["S", "M", "L", "XL"],
                "colors": ["Blue", "Black", "White"],
                "in_stock": True
            }
        ],
        "Straight Fit": [
            {
                "id": 5,
                "name": "Classic Straight Jeans",
                "price": 1499,
                "original_price": 2999,
                "description": "Timeless straight fit jeans in premium indigo denim",
                "image": "https://www.urbanofashion.com/products/urbano-fashion-mens-ice-blue-loose-baggy-fit-washed-jeans-non-stretchable-jeanlswhsk-iceblue?variant=49691933212988&utm_source=adyogi&utm_medium=google-performancemax&utm_campaign=%7B%7Bcampaign.name%7D%7D--%7B%7Bcampaign.id%7D%7D--%7B%7Bcampaign_id%7D%7D-22293376928&utm_content=-&gad_source=1&gad_campaignid=22297130626&gbraid=0AAAAAqi-DqueHdUqLnJKHj4ziU2su_OZK&gclid=Cj0KCQjw-4XFBhCBARIsAAdNOktjmDz6yADD3PXuNQJZVCfDD1m8L2sEgX7WHSZx3hOexk9itb07QI4aAnLsEALw_wcBp",
                "rating": 4.7,
                "sizes": ["S", "M", "L", "XL"],
                "colors": ["Indigo", "Black", "Grey"],
                "in_stock": True
            }
        ]
    },
    "Boys Tops": [
        {
            "id": 6,
            "name": "Blue Stripe Linen Shirt",
            "price": 999,
            "original_price": 1499,
            "description": "Classic aura with omfortable cotton fabric",
            "image": "https://www.myntra.com/shirts/powerlook/powerlook-men-micro-checks-checked-casual-shirt/30203386/buy?utm_source=dms_google&utm_medium=dms_pmax_cpc&utm_campaign=dms_google_pmax_cpc_Myntra_Top_D2C_Brands_SOK_New&keyword=&matchtype=&target=&placement=&gad_source=1&gad_campaignid=22398654717&gbraid=0AAAAADoxBh6idjtHLVHgfsEZrpteztmAd&gclid=Cj0KCQjw-4XFBhCBARIsAAdNOkuEolAmki89LJrMCVtF_bTPkarHdhIBVXNFdWXJMJ0gFrgcDO7up2saAlddEALw_wcB",
            "rating": 4.2,
            "sizes": ["S", "M", "L", "XL"],
            "colors": ["Black", "White", "Navy"],
            "in_stock": True
        },
        {
            "id": 7,
            "name": "Semi-Formal Blazer",
            "price": 2499,
            "original_price": 3299,
            "description": "Comfortable blazer perfect for layering and street style",
            "image": "https://www.westside.com/products/wes-formals-beige-slim-fit-blazer-300973274?variant=43895469572149#gallery-3",
            "rating": 4.5,
            "sizes": ["M", "L", "XL", "XXL"],
            "colors": ["Black", "Grey", "Navy"],
            "in_stock": True
        }
    ],
    "Girls Jeans": {
        "Bell Bottom": [
            {
                "id": 8,
                "name": "Blue Bell Bottom Jeans",
                "price": 2199,
                "original_price": 4199,
                "description": "Feminine bell bottom jeans ",
                "image": "https://offduty.in/products/dark-blue-high-waist-flare-boot-cut-jeans?variant=31252909326433&country=IN&currency=INR&utm_medium=product_sync&utm_source=google&utm_content=sag_organic&utm_campaign=sag_organic&srsltid=AfmBOoqUU4rKJLd7Mci4cY-I-C5BD7Ny2yhjjP-DWmPyMWI3GU4iNHCL3OI",
                "rating": 4.4,
                "sizes": ["XS", "S", "M", "L"],
                "colors": ["Blue", "Light Blue", "White"],
                "in_stock": True
            }
        ],
        "Loose Fit Jeans": [
            {
                "id": 9,
                "name": "Loose Straight Fit Jeans",
                "price": 2500,
                "original_price": 4299,
                "description": " Gen Zee Loves these",
                "image": "https://offduty.in/products/copper-blue-loose-straight-fit-jeans?variant=41784415354977&country=IN&currency=INR&utm_medium=product_sync&utm_source=google&utm_content=sag_organic&utm_campaign=sag_organic&srsltid=AfmBOoo7kB0vGM3yfUj0SQo0IB18uIh3RcNdDmmmpJ-7zmqjyiK9tQcBiv4",
                "rating": 4.3,
                "sizes": ["XS", "S", "M", "L"],
                "colors": ["Pink", "Lavender", "White"],
                "in_stock": True
            }
        ],
        "Loose Fit": [
            {
                "id": 10,
                "name": "Boyfriend Jeans",
                "price": 2799,
                "original_price": 3699,
                "description": "Relaxed boyfriend jeans",
                "image": "https://www.bewakoof.com/p/womens-light-blue-high-waist-denim?utm_source=google&utm_medium=cpc&ps_id=1307000&$ios_passive_deepview=false&tag=jeans&nsbp=true#zoom",
                "rating": 4.6,
                "sizes": ["XS", "S", "M", "L"],
                "colors": ["Blue", "Light Blue", "Black"],
                "in_stock": True
            }
        ],
        "Straight Fit": [
            {
                "id": 11,
                "name": "Straight Jeans",
                "price": 2000,
                "original_price": 3799,
                "description": "Flattering straight jeans with perfect fit",
                "image": "https://offduty.in/products/wash-out-regular-blue-stretch-tailored-straight-leg-jeans?srsltid=AfmBOorWcQKJ5FLdOaYyxDpHdU0O1nb4yjU1DfKYVCUtc8T8DYH7HOl2",
                "rating": 4.8,
                "sizes": ["XS", "S", "M", "L"],
                "colors": ["Dark Blue", "Black", "Grey"],
                "in_stock": True
            }
        ]
    },
    "Girls Tops": [
        {
            "id": 12,
            "name": "Hot Bodycon ",
            "price": 1999,
            "original_price": 2999,
            "description": "Stylish bodycon dress with flattering fit and trendy design",
            "image": "https://newme.asia/product/purple-fit-and-flare-maxi-dress-2#fullScreenImg",
            "rating": 4.1,
            "sizes": ["XS", "S", "M", "L"],
            "colors": ["Pink", "White", "Black"],
            "in_stock": True
        },
        {
            "id": 13,
            "name": "Floral Crop Top",
            "price": 999,
            "original_price": 1999,
            "description": "Elegant floral crop top perfect for casual and formal occasions",
            "image": "https://littleboxindia.com/products/floral-print-tie-front-bell-sleeve-mesh-crop-top?variant=50779661173023&country=IN&currency=INR&utm_medium=product_sync&utm_source=google&utm_content=sag_organic&utm_campaign=sag_organic&gad_source=1&gad_campaignid=18011734208&gbraid=0AAAAAoiHIsdXjvEhNSXb-j7VwwNyFVt1V&gclid=Cj0KCQjw-4XFBhCBARIsAAdNOkuMIdPxZvaG39BlVVl3cZpfkMTd6_VmLWYyysE_9HEZGAJBC0uTTUsaAtNyEALw_wcB",
            "rating": 4.5,
            "sizes": ["XS", "S", "M", "L"],
            "colors": ["Floral Blue", "Floral Pink", "White"],
            "in_stock": True
        }
    ]
}

# Utility functions
def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    pattern = r'^[+]?[\d\s\-\(\)]{10,15}$'
    return re.match(pattern, phone) is not None

def add_to_cart(product):
    # Check if product already exists in cart
    for item in st.session_state.cart:
        if item['id'] == product['id'] and item['size'] == product.get('size', 'M') and item['color'] == product.get('color', product['colors'][0]):
            item['quantity'] += 1
            return
    
    # Add new item to cart
    cart_item = product.copy()
    cart_item['quantity'] = 1
    cart_item['size'] = product.get('size', 'M')
    cart_item['color'] = product.get('color', product['colors'][0])
    st.session_state.cart.append(cart_item)

def calculate_cart_total():
    total = 0
    for item in st.session_state.cart:
        total += item['price'] * item['quantity']
    return total

def display_product_card(product, category, subcategory=None):
    discount = int(((product['original_price'] - product['price']) / product['original_price']) * 100)
    
    with st.container():
        st.markdown(f"""
        <div class="product-card">
            <img src="{product['image']}" class="product-image" alt="{product['name']}">
            <div class="discount-badge">{discount}% OFF</div>
            <h3>{product['name']}</h3>
            <div class="rating">{'⭐' * int(product['rating'])} {product['rating']}/5</div>
            <p>{product['description']}</p>
            <div>
                <span class="original-price">₹{product['original_price']}</span>
                <span class="price-tag">₹{product['price']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            size = st.selectbox("Size", product['sizes'], key=f"size_{product['id']}")
        with col2:
            color = st.selectbox("Color", product['colors'], key=f"color_{product['id']}")
        with col3:
            quantity = st.selectbox("Qty", [1, 2, 3, 4, 5], key=f"qty_{product['id']}")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"Add to Cart", key=f"cart_{product['id']}", type="primary"):
                product_copy = product.copy()
                product_copy['size'] = size
                product_copy['color'] = color
                product_copy['quantity'] = quantity
                for _ in range(quantity):
                    add_to_cart(product_copy)
                st.success(f"Added {product['name']} to cart!")
        
        with col2:
            if st.button(f"Buy Now", key=f"buy_{product['id']}", type="secondary"):
                product_copy = product.copy()
                product_copy['size'] = size
                product_copy['color'] = color
                product_copy['quantity'] = quantity
                st.session_state.cart = [product_copy]
                st.session_state.page = "Checkout"
                st.rerun()

# User Authentication
def show_login_signup():
    st.markdown('<h1 class="main-header">👕 Welcome to GenZHub</h1>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        st.subheader("Login to Your Account")
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            
            if submitted:
                # Simple validation (in real app, use proper authentication)
                if email and password:
                    st.session_state.user_logged_in = True
                    st.session_state.user_info = {"email": email}
                    st.success("Logged in successfully!")
                    st.rerun()
                else:
                    st.error("Please fill all fields")
    
    with tab2:
        st.subheader("Create New Account")
        with st.form("signup_form"):
            col1, col2 = st.columns(2)
            with col1:
                first_name = st.text_input("First Name")
                email = st.text_input("Email")
                phone = st.text_input("Phone Number")
            with col2:
                last_name = st.text_input("Last Name")
                password = st.text_input("Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
            
            address = st.text_area("Address")
            
            submitted = st.form_submit_button("Create Account")
            
            if submitted:
                if all([first_name, last_name, email, phone, address, password, confirm_password]):
                    if not validate_email(email):
                        st.error("Please enter a valid email address")
                    elif not validate_phone(phone):
                        st.error("Please enter a valid phone number")
                    elif password != confirm_password:
                        st.error("Passwords don't match")
                    else:
                        st.session_state.user_logged_in = True
                        st.session_state.user_info = {
                            "first_name": first_name,
                            "last_name": last_name,
                            "email": email,
                            "phone": phone,
                            "address": address
                        }
                        st.success("Account created successfully!")
                        st.rerun()
                else:
                    st.error("Please fill all fields")

# Main App
if not st.session_state.user_logged_in:
    show_login_signup()
else:
    # Header
    st.markdown('<h1 class="main-header">🛒 GenZHub - Fashion Store</h1>', unsafe_allow_html=True)
    
    # Top bar with user info and cart
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.write(f"Welcome, {st.session_state.user_info.get('first_name', 'User')}!")
    with col2:
        cart_count = len(st.session_state.cart)
        if st.button(f"🛒 Cart ({cart_count})", key="cart_button"):
            st.session_state.page = "Cart"
            st.rerun()
    with col3:
        if st.button("Logout"):
            st.session_state.user_logged_in = False
            st.session_state.cart = []
            st.rerun()
    
    # Sidebar Navigation
    st.sidebar.title("🛍️ Shop Categories")
    page = st.sidebar.selectbox(
        "Navigate",
        ["Home", "Boys Jeans", "Boys Tops", "Girls Jeans", "Girls Tops", "Cart", "My Orders", "Profile"]
    )
    
    # Filters in sidebar
    if "Jeans" in page or page == "Home":
        st.sidebar.subheader("🔍 Filters")
        price_range = st.sidebar.slider("Price Range (₹)", 500, 5000, (1000, 4000))
        selected_sizes = st.sidebar.multiselect("Size", ["XS", "S", "M", "L", "XL", "XXL"])
        sort_by = st.sidebar.selectbox("Sort By", ["Price: Low to High", "Price: High to Low", "Rating", "Newest"])
    
    # Page content
    if page == "Home":
        st.markdown("## 🎉 Welcome to GenZHub!")
        st.write("Your ultimate destination for trendy Gen-Z fashion. Discover the latest styles in jeans and tops!")
        
        # Featured products
        st.markdown('<div class="category-header">✨ Featured Products</div>', unsafe_allow_html=True)
        
        featured_products = [
            products_database["Boys Jeans"]["Bell Bottom"][0],
            products_database["Girls Jeans"]["Loose Fit"][0],
            products_database["Boys Tops"][0],
            products_database["Girls Tops"][0]
        ]
        
        cols = st.columns(2)
        for idx, product in enumerate(featured_products[:2]):
            with cols[idx]:
                display_product_card(product, "Featured")
        
        # Categories showcase
        st.markdown('<div class="category-header">🛍️ Shop by Category</div>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        categories = [
            ("👦 Boys Jeans", "boys-jeans"),
            ("👕 Boys Tops", "boys-tops"),
            ("👧 Girls Jeans", "girls-jeans"),
            ("👚 Girls Tops", "girls-tops")
        ]
        
        for idx, (cat_name, cat_key) in enumerate(categories):
            with [col1, col2, col3, col4][idx]:
                st.markdown(f"""
                <div class="product-card" style="text-align: center; min-height: 200px; display: flex; flex-direction: column; justify-content: center;">
                    <h3>{cat_name}</h3>
                    <p>Discover amazing collection</p>
                </div>
                """, unsafe_allow_html=True)
    
    elif page == "Boys Jeans":
        st.markdown('<div class="category-header">👖 Boys Jeans Collection</div>', unsafe_allow_html=True)
        
        for subcategory, products in products_database["Boys Jeans"].items():
            st.markdown(f"### {subcategory} Jeans")
            cols = st.columns(2)
            for idx, product in enumerate(products):
                # Apply filters
                if product['price'] < price_range[0] or product['price'] > price_range[1]:
                    continue
                if selected_sizes and not any(size in product['sizes'] for size in selected_sizes):
                    continue
                
                with cols[idx % 2]:
                    display_product_card(product, "Boys Jeans", subcategory)
    
    elif page == "Boys Tops":
        st.markdown('<div class="category-header">👕 Boys Tops Collection</div>', unsafe_allow_html=True)
        
        cols = st.columns(2)
        for idx, product in enumerate(products_database["Boys Tops"]):
            with cols[idx % 2]:
                display_product_card(product, "Boys Tops")
    
    elif page == "Girls Jeans":
        st.markdown('<div class="category-header">👖 Girls Jeans Collection</div>', unsafe_allow_html=True)
        
        for subcategory, products in products_database["Girls Jeans"].items():
            st.markdown(f"### {subcategory} Jeans")
            cols = st.columns(2)
            for idx, product in enumerate(products):
                # Apply filters
                if product['price'] < price_range[0] or product['price'] > price_range[1]:
                    continue
                if selected_sizes and not any(size in product['sizes'] for size in selected_sizes):
                    continue
                
                with cols[idx % 2]:
                    display_product_card(product, "Girls Jeans", subcategory)
    
    elif page == "Girls Tops":
        st.markdown('<div class="category-header">👚 Girls Tops Collection</div>', unsafe_allow_html=True)
        
        cols = st.columns(2)
        for idx, product in enumerate(products_database["Girls Tops"]):
            with cols[idx % 2]:
                display_product_card(product, "Girls Tops")
    
    elif page == "Cart":
        st.markdown('<div class="category-header">🛒 Your Shopping Cart</div>', unsafe_allow_html=True)
        
        if st.session_state.cart:
            for idx, item in enumerate(st.session_state.cart):
                st.markdown(f"""
                <div class="cart-item">
                    <div style="display: flex; align-items: center;">
                        <img src="{item['image']}" style="width: 80px; height: 80px; object-fit: cover; border-radius: 8px; margin-right: 1rem;">
                        <div style="flex-grow: 1;">
                            <h4>{item['name']}</h4>
                            <p>Size: {item['size']} | Color: {item['color']} | Qty: {item['quantity']}</p>
                            <p style="font-weight: 600; color: #FF6B35;">₹{item['price'] * item['quantity']}</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns([1, 1, 1])
                with col1:
                    if st.button("➕", key=f"inc_{idx}"):
                        st.session_state.cart[idx]['quantity'] += 1
                        st.rerun()
                with col2:
                    if st.button("➖", key=f"dec_{idx}") and item['quantity'] > 1:
                        st.session_state.cart[idx]['quantity'] -= 1
                        st.rerun()
                with col3:
                    if st.button("🗑️ Remove", key=f"remove_{idx}"):
                        st.session_state.cart.pop(idx)
                        st.rerun()
            
            # Cart summary
            total = calculate_cart_total()
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"### Total: ₹{total}")
            with col2:
                if st.button("🛒 Proceed to Checkout", type="primary"):
                    st.session_state.page = "Checkout"
                    st.rerun()
        else:
            st.write("Your cart is empty. Start shopping to add items!")
            if st.button("Continue Shopping"):
                st.session_state.page = "Home"
                st.rerun()
    
    elif page == "Profile":
        st.markdown('<div class="category-header">👤 My Profile</div>', unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="user-info-card">
            <h3>User Information</h3>
            <p><strong>Name:</strong> {st.session_state.user_info.get('first_name', '')} {st.session_state.user_info.get('last_name', '')}</p>
            <p><strong>Email:</strong> {st.session_state.user_info.get('email', '')}</p>
            <p><strong>Phone:</strong> {st.session_state.user_info.get('phone', '')}</p>
            <p><strong>Address:</strong> {st.session_state.user_info.get('address', '')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.subheader("Update Profile")
        with st.form("update_profile"):
            col1, col2 = st.columns(2)
            with col1:
                new_first_name = st.text_input("First Name", value=st.session_state.user_info.get('first_name', ''))
                new_email = st.text_input("Email", value=st.session_state.user_info.get('email', ''))
            with col2:
                new_last_name = st.text_input("Last Name", value=st.session_state.user_info.get('last_name', ''))
                new_phone = st.text_input("Phone", value=st.session_state.user_info.get('phone', ''))
            
            new_address = st.text_area("Address", value=st.session_state.user_info.get('address', ''))
            
            if st.form_submit_button("Update Profile"):
                st.session_state.user_info.update({
                    'first_name': new_first_name,
                    'last_name': new_last_name,
                    'email': new_email,
                    'phone': new_phone,
                    'address': new_address
                })
                st.success("Profile updated successfully!")
                st.rerun()
    
    elif page == "My Orders":
        st.markdown('<div class="category-header">📦 My Orders</div>', unsafe_allow_html=True)
        
        if st.session_state.orders:
            for idx, order in enumerate(st.session_state.orders):
                st.markdown(f"""
                <div class="cart-item">
                    <h4>Order #{order['order_id']}</h4>
                    <p><strong>Date:</strong> {order['date']}</p>
                    <p><strong>Total:</strong> ₹{order['total']}</p>
                    <p><strong>Status:</strong> <span style="color: green; font-weight: 600;">{order['status']}</span></p>
                    <p><strong>Items:</strong> {order['item_count']} items</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.write("You haven't placed any orders yet.")
            if st.button("Start Shopping"):
                st.session_state.page = "Home"
                st.rerun()

    # Checkout process
    if hasattr(st.session_state, 'page') and st.session_state.page == "Checkout":
        st.markdown('<div class="category-header">💳 Checkout</div>', unsafe_allow_html=True)
        
        if st.session_state.cart:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("Order Summary")
                total = 0
                for item in st.session_state.cart:
                    st.write(f"{item['name']} - Size: {item['size']}, Color: {item['color']}, Qty: {item['quantity']} - ₹{item['price'] * item['quantity']}")
                    total += item['price'] * item['quantity']
                
                st.markdown("---")
                shipping = 99 if total < 1999 else 0
                tax = int(total * 0.18)
                final_total = total + shipping + tax
                
                st.write(f"Subtotal: ₹{total}")
                st.write(f"Shipping: ₹{shipping} {'(Free shipping on orders above ₹1999)' if shipping == 0 else ''}")
                st.write(f"Tax (18%): ₹{tax}")
                st.markdown(f"**Total: ₹{final_total}**")
            
            with col2:
                st.subheader("Delivery Address")
                st.markdown(f"""
                <div class="user-info-card">
                    <p><strong>{st.session_state.user_info.get('first_name', '')} {st.session_state.user_info.get('last_name', '')}</strong></p>
                    <p>{st.session_state.user_info.get('address', '')}</p>
                    <p>Phone: {st.session_state.user_info.get('phone', '')}</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.subheader("Payment Method")
                payment_method = st.radio("Select Payment Method", 
                                       ["Credit/Debit Card", "UPI", "Net Banking", "Cash on Delivery"])
                
                if payment_method == "Credit/Debit Card":
                    with st.form("card_payment"):
                        card_number = st.text_input("Card Number", placeholder="1234 5678 9012 3456")
                        col1, col2 = st.columns(2)
                        with col1:
                            expiry = st.text_input("MM/YY", placeholder="12/25")
                        with col2:
                            cvv = st.text_input("CVV", placeholder="123", type="password")
                        card_name = st.text_input("Cardholder Name")
                        
                        if st.form_submit_button("Place Order", type="primary"):
                            if all([card_number, expiry, cvv, card_name]):
                                # Process order
                                order = {
                                    "order_id": f"GZ{datetime.now().strftime('%Y%m%d%H%M%S')}",
                                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                    "total": final_total,
                                    "status": "Order Confirmed",
                                    "item_count": len(st.session_state.cart),
                                    "items": st.session_state.cart.copy()
                                }
                                st.session_state.orders.append(order)
                                st.session_state.cart = []
                                
                                st.success(f"🎉 Order placed successfully! Order ID: {order['order_id']}")
                                st.balloons()
                                
                                if st.button("Continue Shopping"):
                                    st.session_state.page = "Home"
                                    st.rerun()
                            else:
                                st.error("Please fill all card details")
                
                elif payment_method == "UPI":
                    with st.form("upi_payment"):
                        upi_id = st.text_input("UPI ID", placeholder="yourname@paytm")
                        if st.form_submit_button("Pay with UPI", type="primary"):
                            if upi_id:
                                order = {
                                    "order_id": f"GZ{datetime.now().strftime('%Y%m%d%H%M%S')}",
                                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                    "total": final_total,
                                    "status": "Order Confirmed",
                                    "item_count": len(st.session_state.cart),
                                    "items": st.session_state.cart.copy()
                                }
                                st.session_state.orders.append(order)
                                st.session_state.cart = []
                                
                                st.success(f"🎉 Order placed successfully! Order ID: {order['order_id']}")
                                st.balloons()
                                
                                if st.button("Continue Shopping"):
                                    st.session_state.page = "Home"
                                    st.rerun()
                            else:
                                st.error("Please enter UPI ID")
                
                elif payment_method == "Cash on Delivery":
                    st.info("You will pay ₹{} when the order is delivered.".format(final_total))
                    if st.button("Confirm Order", type="primary"):
                        order = {
                            "order_id": f"GZ{datetime.now().strftime('%Y%m%d%H%M%S')}",
                            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "total": final_total,
                            "status": "Order Confirmed - COD",
                            "item_count": len(st.session_state.cart),
                            "items": st.session_state.cart.copy()
                        }
                        st.session_state.orders.append(order)
                        st.session_state.cart = []
                        
                        st.success(f"🎉 Order placed successfully! Order ID: {order['order_id']}")
                        st.balloons()
                        
                        if st.button("Continue Shopping"):
                            st.session_state.page = "Home"
                            st.rerun()
        
        # Back to cart button
        if st.button("← Back to Cart"):
            st.session_state.page = "Cart"
            st.rerun()

    # Footer
    st.markdown("""
    <div class="footer">
        <h3>GenZHub - Fashion for the New Generation</h3>
        <div style="display: flex; justify-content: center; gap: 2rem; margin: 1rem 0;">
            <div>
                <h4>Quick Links</h4>
                <p>About Us</p>
                <p>Contact</p>
                <p>Size Guide</p>
                <p>Return Policy</p>
            </div>
            <div>
                <h4>Customer Service</h4>
                <p>📞 1800-123-4567</p>
                <p>📧 support@genzhub.com</p>
                <p>🕒 24/7 Support</p>
            </div>
            <div>
                <h4>Follow Us</h4>
                <p>📱 @genzhub</p>
                <p>📘 Facebook</p>
                <p>📷 Instagram</p>
                <p>🐦 Twitter</p>
            </div>
        </div>
        <p>© 2024 GenZHub. All rights reserved. | Privacy Policy | Terms of Service</p>
    </div>
    """, unsafe_allow_html=True)