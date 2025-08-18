import streamlit as st
import pandas as pd
from datetime import datetime
import json
import re
import base64
import os
from PIL import Image
import io

# Page configuration
st.set_page_config(
    page_title="GenZHub - Fashion E-commerce",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with enhanced styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2rem;
        color: white;
        font-size: 3.5rem;
        font-weight: 700;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    .product-card {
        background: white;
        border-radius: 20px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
        transition: all 0.3s ease;
        overflow: hidden;
    }
    
    .product-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.15);
        border-color: #667eea;
    }
    
    .product-image {
        width: 100%;
        height: 280px;
        object-fit: cover;
        border-radius: 15px;
        margin-bottom: 1rem;
        transition: transform 0.3s ease;
    }
    
    .product-image:hover {
        transform: scale(1.05);
    }
    
    .price-tag {
        font-size: 2rem;
        color: #FF6B35;
        font-weight: 700;
        margin: 0.5rem 0;
    }
    
    .original-price {
        text-decoration: line-through;
        color: #999;
        font-size: 1.3rem;
        margin-right: 10px;
    }
    
    .discount-badge {
        background: linear-gradient(45deg, #FF6B35, #F7931E);
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 25px;
        font-size: 0.9rem;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 1rem;
        position: absolute;
        top: 15px;
        right: 15px;
        z-index: 10;
    }
    
    .category-header {
        background: linear-gradient(45deg, #4ECDC4, #44A08D);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 30px;
        font-size: 2rem;
        font-weight: 600;
        margin: 2rem 0 1rem 0;
        text-align: center;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    .user-info-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 20px;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .cart-item {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 5px solid #4ECDC4;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    }
    
    .rating {
        color: #FFD700;
        font-size: 1.3rem;
        margin: 0.5rem 0;
    }
    
    .top-bar {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .stats-card {
        background: linear-gradient(135deg, #4ECDC4 0%, #44A08D 100%);
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin: 0.5rem;
    }
    
    .footer {
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
        color: white;
        padding: 3rem 2rem;
        border-radius: 20px;
        margin-top: 3rem;
        text-align: center;
    }
    
    .search-bar {
        background: white;
        border-radius: 25px;
        padding: 0.5rem 1.5rem;
        border: 2px solid #e0e0e0;
        font-size: 1rem;
        width: 100%;
        margin: 1rem 0;
    }
    
    .notification {
        background: linear-gradient(45deg, #FF6B35, #F7931E);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Utility functions for image handling
def load_local_image(image_path):
    """Load local image and convert to base64"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        return None
    except Exception as e:
        st.error(f"Error loading image: {e}")
        return None

def get_image_url(image_path_or_url):
    """Handle both local images and online URLs"""
    if image_path_or_url.startswith(('http://', 'https://')):
        return image_path_or_url
    else:
        # Try to load local image
        base64_image = load_local_image(image_path_or_url)
        if base64_image:
            # Detect image format
            img_format = "jpeg"
            if image_path_or_url.lower().endswith('.png'):
                img_format = "png"
            elif image_path_or_url.lower().endswith('.webp'):
                img_format = "webp"
            
            return f"data:image/{img_format};base64,{base64_image}"
        else:
            # Fallback to placeholder
            return "https://via.placeholder.com/400x400/667eea/ffffff?text=GenZHub+Product"

def optimize_uploaded_image(uploaded_file, max_size=(400, 400)):
    """Optimize uploaded images"""
    try:
        img = Image.open(uploaded_file)
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=85, optimize=True)
        return base64.b64encode(buffer.getvalue()).decode()
    except Exception as e:
        st.error(f"Error processing image: {e}")
        return None

# Validation functions
def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    pattern = r'^[+]?[\d\s\-\(\)]{10,15}$'
    return re.match(pattern, phone) is not None

def validate_name(name):
    return len(name.strip()) >= 2 and name.replace(' ', '').isalpha()

# Initialize session state
def initialize_session_state():
    defaults = {
        'user_logged_in': False,
        'user_info': {},
        'cart': [],
        'orders': [],
        'wishlist': [],
        'current_page': 'Home',
        'search_query': '',
        'admin_mode': False
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

initialize_session_state()

# Enhanced product database with local image paths
products_database = {
    "Boys Jeans": {
        "Bell Bottom": [
            {
                "id": 1,
                "name": "Vintage Bell Bottom Jeans",
                "price": 1999,
                "original_price": 2999,
                "description": "Classic 70s inspired bell bottom jeans with authentic vintage wash and flared legs",
                "image": "https://github.com/harshjethava1035-ai/GenZHub/blob/5c53d33a295a0250aa336d001d10dec33022872f/Bell.jpg",
                "rating": 4.5,
                "sizes": ["S", "M", "L", "XL"],
                "colors": ["Blue", "Black", "Grey"],
                "in_stock": True,
                "tags": ["vintage", "retro", "flared", "denim"]
            },
            {
                "id": 2,
                "name": "Korean Bell Bottom Jeans",
                "price": 1999,
                "original_price": 2999,
                "description": "https://github.com/harshjethava1035-ai/GenZHub/blob/5c53d33a295a0250aa336d001d10dec33022872f/Korean.jpg",
                "image": "images/Korean.jpg",
                "rating": 4.3,
                "sizes": ["S", "M", "L", "XL"],
                "colors": ["Dark Blue", "Light Blue"],
                "in_stock": True,
                "tags": ["modern", "stylish", "premium"]
            }
        ],
        "Loose Fit": [
            {
                "id": 3,
                "name": "Loose fit trousers",
                "price": 1499,
                "original_price": 2999,
                "description": "ost loved bottom wear by Gen Z",
                "image": "https://github.com/harshjethava1035-ai/GenZHub/blob/5c53d33a295a0250aa336d001d10dec33022872f/Loose.jpg"
                "",
                "rating": 4.6,
                "sizes": ["S", "M", "L", "XL", "XXL"],
                "colors": ["Olive", "Black", "Khaki"],
                "in_stock": True,
                "tags": ["cargo", "functional", "outdoor", "utility"]
            },
            
        ],
        "Relaxed": [
            {
                "id": 5,
                "name": "Relaxed Fit Jeans",
                "price": 2499,
                "original_price": 3299,
                "description": "Comfortable loose fit jeans perfect for casual everyday wear and street style.",
                "image": "https://github.com/harshjethava1035-ai/GenZHub/blob/main/Loose.jpg#:~:text=README.md-,Relaxed,-.jpg",
                "rating": 4.4,
                "sizes": ["S", "M", "L", "XL"],
                "colors": ["Blue", "Black", "White"],
                "in_stock": True,
                "tags": ["comfortable", "casual", "streetwear"]
            },
            
        ],
        "Straight Fit": [
            {
                "id": 7,
                "name": "https://github.com/harshjethava1035-ai/GenZHub/blob/main/Straight.jpg#:~:text=Straight.-,jpg,-StraightFit.jpg",
                "price": 2299,
                "original_price": 2999,
                "description": "Timeless straight fit jeans in premium indigo denim. Perfect for any occasion.",
                "image": "images/Straight.jpg",
                "rating": 4.7,
                "sizes": ["S", "M", "L", "XL"],
                "colors": ["Indigo", "Black", "Grey"],
                "in_stock": True,
                "tags": ["classic", "timeless", "versatile"]
            },
            
        ]
    },
    "Boys Tops": [
        {
            "id": 9,
            "name": "Blue Stripe Linen Shirt",
            "price": 999,
            "original_price": 1499,
            "description": "Classic aura with omfortable cotton fabric",
            "image": "https://github.com/harshjethava1035-ai/GenZHub/blob/main/Blue.jpg#:~:text=Blue.-,jpg,-Bodycon.jpg",
            "rating": 4.2,
            "sizes": ["S", "M", "L", "XL"],
            "colors": ["Black", "White", "Navy"],
            "in_stock": True,
            "tags": ["graphic", "trendy", "cotton"]
        },
        {
            "id": 10,
            "name": "Semi-Formal Blazer",
            "price": 3999,
            "original_price": 5999,
            "description": "Comfortable blazer perfect for layering and street style",
            "image": "https://github.com/harshjethava1035-ai/GenZHub/blob/main/Blazer.jpg#:~:text=Bell.jpg-,Blazer,-.jpg",
            "rating": 4.5,
            "sizes": ["M", "L", "XL", "XXL"],
            "colors": ["Black", "Grey", "Navy"],
            "in_stock": True,
            "tags": ["oversized", "hoodie", "streetwear"]
        },
        
    ],
    "Girls Jeans": {
        "Bell Bottom": [
            {
                "id": 12,
                "name": "Blue Bell Bottom Jeans",
                "price": 3199,
                "original_price": 4199,
                "description": "Feminine bell bottom jeans",
                "image": "https://github.com/harshjethava1035-ai/GenZHub/blob/main/Dark%20Blue.jpg#:~:text=Dark%20Blue.-,jpg,-GenZHub.app.py",
                "rating": 4.4,
                "sizes": ["XS", "S", "M", "L"],
                "colors": ["Blue", "Light Blue", "White"],
                "in_stock": True,
                "tags": ["floral", "feminine", "embroidery"]
            },
            
        ],
        "Loose Fit Jeans": [
            {
                "id": 14,
                "name": "Loose Straight Fit Jeans",
                "price": 2499,
                "original_price": 4299,
                "description": "Gen Zee Loves these",
                "image": "https://github.com/harshjethava1035-ai/GenZHub/blob/main/LooseFit.jpg#:~:text=Loose.jpg-,LooseFit,-.jpg",
                "rating": 4.3,
                "sizes": ["XS", "S", "M", "L"],
                "colors": ["Pink", "Lavender", "White"],
                "in_stock": True,
                "tags": ["pink", "cargo", "functional"]
            },
            
        ],
        "Boyfriend Fit": [
            {
                "id": 16,
                "name": "Boyfriend Jeans",
                "price": 2799,
                "original_price": 3699,
                "description": "Relaxed boyfriend jeans with perfectly vintage wash.",
                "image": "https://github.com/harshjethava1035-ai/GenZHub/blob/main/RelaxedFit.jpg#:~:text=Relaxed.jpg-,RelaxedFit,-.jpg",
                "rating": 4.6,
                "sizes": ["XS", "S", "M", "L"],
                "colors": ["Blue", "Light Blue", "Black"],
                "in_stock": True,
                "tags": ["boyfriend", "relaxed", "vintage"]
            },
           
        ],
        "Straight Fit": [
            {
                "id": 18,
                "name": "Straight Jeans",
                "price": 1999,
                "original_price": 3799,
                "description": "Flattering straight jeans with perfect fit",
                "image": "https://github.com/harshjethava1035-ai/GenZHub/blob/main/StraightFit.jpg#:~:text=Straight.jpg-,StraightFit,-.jpg",
                "rating": 4.8,
                "sizes": ["XS", "S", "M", "L"],
                "colors": ["Dark Blue", "Black", "Grey"],
                "in_stock": True,
                "tags": ["high-waist", "flattering", "premium"]
            },
            
        ]
    },
    "Girls Tops": [
        {
            "id": 20,
            "name": " Hot Bodycon ",
            "price": 1999,
            "original_price": 2999,
            "description": "Stylish bodycon dress with flattering fit and trendy design",
            "image": "https://github.com/harshjethava1035-ai/GenZHub/blob/main/Bodycon.jpg#:~:text=Blue.jpg-,Bodycon,-.jpg",
            "rating": 4.1,
            "sizes": ["XS", "S", "M", "L"],
            "colors": ["Pink", "White", "Black"],
            "in_stock": True,
            "tags": ["crop-top", "summer", "trendy"]
        },
        {
            "id": 21,
            "name": "Floral Crop Top",
            "price": 999,
            "original_price": 1999,
            "description": "Elegant floral crop top perfect for casual outings and special occasions.",
            "image": "https://github.com/harshjethava1035-ai/GenZHub/blob/main/Crop.jpg#:~:text=Bodycon.jpg-,Crop,-.jpg",
            "rating": 4.5,
            "sizes": ["XS", "S", "M", "L"],
            "colors": ["Floral Blue", "Floral Pink", "White"],
            "in_stock": True,
            "tags": ["floral", "elegant", "blouse"]
        },
      
    ]
}

# Cart management functions
def add_to_cart(product, size, color, quantity=1):
    # Check if product already exists in cart with same specifications
    for item in st.session_state.cart:
        if (item['id'] == product['id'] and 
            item['size'] == size and 
            item['color'] == color):
            item['quantity'] += quantity
            return True
    
    # Add new item to cart
    cart_item = product.copy()
    cart_item['quantity'] = quantity
    cart_item['size'] = size
    cart_item['color'] = color
    cart_item['added_date'] = datetime.now().strftime("%Y-%m-%d %H:%M")
    st.session_state.cart.append(cart_item)
    return True

def remove_from_cart(index):
    if 0 <= index < len(st.session_state.cart):
        st.session_state.cart.pop(index)

def update_cart_quantity(index, new_quantity):
    if 0 <= index < len(st.session_state.cart):
        if new_quantity <= 0:
            remove_from_cart(index)
        else:
            st.session_state.cart[index]['quantity'] = new_quantity

def calculate_cart_total():
    total = sum(item['price'] * item['quantity'] for item in st.session_state.cart)
    return total

def get_cart_count():
    return sum(item['quantity'] for item in st.session_state.cart)

# Search functionality
def search_products(query):
    results = []
    query_lower = query.lower()
    
    for category, subcategories in products_database.items():
        if isinstance(subcategories, dict):
            for subcategory, products in subcategories.items():
                for product in products:
                    if (query_lower in product['name'].lower() or 
                        query_lower in product['description'].lower() or
                        any(query_lower in tag for tag in product.get('tags', []))):
                        results.append(product)
        else:
            for product in subcategories:
                if (query_lower in product['name'].lower() or 
                    query_lower in product['description'].lower() or
                    any(query_lower in tag for tag in product.get('tags', []))):
                    results.append(product)
    
    return results

# Enhanced product display function
def display_product_card(product, category, subcategory=None):
    discount = int(((product['original_price'] - product['price']) / product['original_price']) * 100)
    image_url = get_image_url(product['image'])
    
    with st.container():
        st.markdown(f"""
        <div class="product-card" style="position: relative;">
            <div class="discount-badge">{discount}% OFF</div>
            <img src="{image_url}" class="product-image" alt="{product['name']}" 
                 onerror="this.src='https://via.placeholder.com/400x400/667eea/ffffff?text=GenZHub+Product'">
            <h3 style="color: #333; margin: 1rem 0 0.5rem 0;">{product['name']}</h3>
            <div class="rating">{'⭐' * int(product['rating'])} {product['rating']}/5</div>
            <p style="color: #666; font-size: 0.95rem; line-height: 1.4;">{product['description']}</p>
            <div style="margin: 1rem 0;">
                <span class="original-price">₹{product['original_price']}</span>
                <span class="price-tag">₹{product['price']}</span>
            </div>
            <div style="margin: 1rem 0;">
                <small style="color: #4ECDC4; font-weight: 600;">
                    Available in: {', '.join(product['colors'][:3])}{'...' if len(product['colors']) > 3 else ''}
                </small>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Product options
        col1, col2, col3 = st.columns(3)
        with col1:
            size = st.selectbox("Size", product['sizes'], key=f"size_{product['id']}")
        with col2:
            color = st.selectbox("Color", product['colors'], key=f"color_{product['id']}")
        with col3:
            quantity = st.selectbox("Qty", [1, 2, 3, 4, 5], key=f"qty_{product['id']}")
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button(f"🛒 Add to Cart", key=f"cart_{product['id']}", type="primary"):
                add_to_cart(product, size, color, quantity)
                st.success(f"Added {quantity}x {product['name']} to cart!")
                st.rerun()
        
        with col2:
            if st.button(f"💝 Wishlist", key=f"wish_{product['id']}"):
                if product['id'] not in [item['id'] for item in st.session_state.wishlist]:
                    st.session_state.wishlist.append(product)
                    st.success("Added to wishlist!")
                else:
                    st.info("Already in wishlist!")
        
        with col3:
            if st.button(f"⚡ Buy Now", key=f"buy_{product['id']}", type="secondary"):
                st.session_state.cart = []
                add_to_cart(product, size, color, quantity)
                st.session_state.current_page = "Checkout"
                st.rerun()

# User authentication functions
def show_login_signup():
    st.markdown('<h1 class="main-header">🛍️ Welcome to GenZHub</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.3rem; color: #666; margin-bottom: 2rem;">Your Ultimate Fashion Destination for Generation Z</p>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔑 Login", "📝 Sign Up"])
    
    with tab1:
        st.markdown("### Login to Your Account")
        with st.form("login_form", clear_on_submit=True):
            email = st.text_input("📧 Email Address", placeholder="Enter your email")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
            remember_me = st.checkbox("Remember me")
            
            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("Login", type="primary")
            with col2:
                forgot_password = st.form_submit_button("Forgot Password?")
            
            if submitted:
                if email and password:
                    if validate_email(email):
                        st.session_state.user_logged_in = True
                        st.session_state.user_info = {"email": email, "name": "User"}
                        st.success("🎉 Logged in successfully!")
                        st.rerun()
                    else:
                        st.error("Please enter a valid email address")
                else:
                    st.error("Please fill all fields")
            
            if forgot_password:
                st.info("Password reset link sent to your email!")
    
    with tab2:
        st.markdown("### Create Your GenZHub Account")
        with st.form("signup_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                first_name = st.text_input("👤 First Name", placeholder="Enter first name")
                email = st.text_input("📧 Email Address", placeholder="Enter email")
                phone = st.text_input("📱 Phone Number", placeholder="+91 12345 67890")
            with col2:
                last_name = st.text_input("👤 Last Name", placeholder="Enter last name")
                password = st.text_input("🔒 Password", type="password", placeholder="Create password")
                confirm_password = st.text_input("🔒 Confirm Password", type="password", placeholder="Confirm password")
            
            address = st.text_area("🏠 Complete Address", placeholder="Enter your complete address with pincode")
            
            col1, col2 = st.columns(2)
            with col1:
                age = st.number_input("Age", min_value=13, max_value=100, value=20)
            with col2:
                gender = st.selectbox("Gender", ["Male", "Female", "Other", "Prefer not to say"])
            
            terms = st.checkbox("I agree to Terms & Conditions and Privacy Policy")
            newsletter = st.checkbox("Subscribe to GenZHub newsletter for latest updates")
            
            submitted = st.form_submit_button("Create Account", type="primary")
            
            if submitted:
                # Validation
                errors = []
                if not validate_name(first_name):
                    errors.append("First name must be at least 2 characters")
                if not validate_name(last_name):
                    errors.append("Last name must be at least 2 characters")
                if not validate_email(email):
                    errors.append("Please enter a valid email address")
                if not validate_phone(phone):
                    errors.append("Please enter a valid phone number")
                if len(password) < 6:
                    errors.append("Password must be at least 6 characters")
                if password != confirm_password:
                    errors.append("Passwords don't match")
                if len(address.strip()) < 10:
                    errors.append("Please enter a complete address")
                if not terms:
                    errors.append("Please accept Terms & Conditions")
                
                if errors:
                    for error in errors:
                        st.error(error)
                else:
                    st.session_state.user_logged_in = True
                    st.session_state.user_info = {
                        "first_name": first_name,
                        "last_name": last_name,
                        "email": email,
                        "phone": phone,
                        "address": address,
                        "age": age,
                        "gender": gender,
                        "newsletter": newsletter,
                        "join_date": datetime.now().strftime("%Y-%m-%d")
                    }
                    st.success("🎉 Account created successfully! Welcome to GenZHub!")
                    st.balloons()
                    st.rerun()

# Admin functions for image upload
def admin_panel():
    if st.sidebar.button("🔧 Admin Mode"):
        st.session_state.admin_mode = not st.session_state.admin_mode
    
    if st.session_state.admin_mode:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 👨‍💼 Admin Panel")
        
        # Image upload section
        st.sidebar.subheader("📸 Upload Product Image")
        uploaded_file = st.sidebar.file_uploader(
            "Choose image file",
            type=['png', 'jpg', 'jpeg', 'webp'],
            help="Upload high-quality product images (recommended: 400x400px or larger)"
        )
        
        if uploaded_file is not None:
            # Display preview
            st.sidebar.image(uploaded_file, caption="Preview", width=200)
            
            # Save options
            save_name = st.sidebar.text_input("Save as:", value=uploaded_file.name)
            
            if st.sidebar.button("💾 Save Image"):
                try:
                    # Create images directory if it doesn't exist
                    os.makedirs("images", exist_ok=True)
                    
                    # Optimize and save image
                    img = Image.open(uploaded_file)
                    img = img.convert("RGB")
                    img.thumbnail((600, 600), Image.Resampling.LANCZOS)
                    
                    save_path = os.path.join("images", save_name)
                    img.save(save_path, "JPEG", quality=90, optimize=True)
                    
                    st.sidebar.success(f"✅ Image saved as: {save_path}")
                    st.sidebar.info(f"💡 Use this path in your product: 'images/{save_name}'")
                except Exception as e:
                    st.sidebar.error(f"Error saving image: {e}")
        
        # Quick add product form
        with st.sidebar.expander("➕ Quick Add Product"):
            with st.form("quick_add_product"):
                prod_name = st.text_input("Product Name")
                prod_category = st.selectbox("Category", ["Boys Jeans", "Boys Tops", "Girls Jeans", "Girls Tops"])
                prod_price = st.number_input("Price", min_value=100, value=2999)
                prod_image_path = st.text_input("Image Path", placeholder="images/product.jpg")
                
                if st.form_submit_button("Add Product"):
                    st.sidebar.success(f"Product '{prod_name}' configuration ready!")

# Main application
if not st.session_state.user_logged_in:
    show_login_signup()
else:
    # Top navigation bar
    col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
    with col1:
        st.markdown(f'<h2 style="color: #667eea; margin: 0;">Welcome, {st.session_state.user_info.get("first_name", "User")}! 👋</h2>', unsafe_allow_html=True)
    with col2:
        search_query = st.text_input("🔍 Search products...", placeholder="Search jeans, tops...", key="search")
    with col3:
        cart_count = get_cart_count()
        if st.button(f"🛒 Cart ({cart_count})", key="cart_nav"):
            st.session_state.current_page = "Cart"
            st.rerun()
    with col4:
        if st.button("🚪 Logout"):
            for key in ['user_logged_in', 'user_info', 'cart', 'current_page']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    
    # Header
    st.markdown('<h1 class="main-header">🛍️ GenZHub Fashion Store</h1>', unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("🎯 Navigation")
    page = st.sidebar.selectbox(
        "Explore Categories",
        ["🏠 Home", "👖 Boys Jeans", "👕 Boys Tops", "👗 Girls Jeans", "👚 Girls Tops", 
         "🛒 Cart", "📦 My Orders", "💝 Wishlist", "👤 Profile"]
    )
    
    # Admin panel (optional)
    admin_panel()
    
    # Filters in sidebar
    if any(word in page for word in ["Jeans", "Tops", "Home"]):
        st.sidebar.markdown("---")
        st.sidebar.subheader("🔍 Filters & Sort")
        
        # Price filter
        price_range = st.sidebar.slider("💰 Price Range (₹)", 500, 5000, (1000, 4000))
        
        # Size filter
        if "Jeans" in page or page == "🏠 Home":
            size_options = ["XS", "S", "M", "L", "XL", "XXL"]
        else:
            size_options = ["XS", "S", "M", "L", "XL"]
        selected_sizes = st.sidebar.multiselect("📏 Size", size_options)
        
        # Color filter
        color_options = ["Blue", "Black", "White", "Grey", "Pink", "Navy", "Olive", "Khaki"]
        selected_colors = st.sidebar.multiselect("🎨 Colors", color_options)
        
        # Sort options
        sort_by = st.sidebar.selectbox("📊 Sort By", 
                                     ["🆕 Newest First", "💰 Price: Low to High", "💸 Price: High to Low", 
                                      "⭐ Highest Rated", "🔥 Most Popular"])
        
        # Rating filter
        min_rating = st.sidebar.slider("⭐ Minimum Rating", 1.0, 5.0, 3.0, 0.5)

# Page routing
def filter_products(products, price_range, selected_sizes, selected_colors, min_rating):
    filtered = []
    for product in products:
        # Price filter
        if product['price'] < price_range[0] or product['price'] > price_range[1]:
            continue
        # Size filter
        if selected_sizes and not any(size in product['sizes'] for size in selected_sizes):
            continue
        # Color filter
        if selected_colors and not any(color in product['colors'] for color in selected_colors):
            continue
        # Rating filter
        if product['rating'] < min_rating:
            continue
        
        filtered.append(product)
    
    return filtered

def sort_products(products, sort_by):
    if sort_by == "💰 Price: Low to High":
        return sorted(products, key=lambda x: x['price'])
    elif sort_by == "💸 Price: High to Low":
        return sorted(products, key=lambda x: x['price'], reverse=True)
    elif sort_by == "⭐ Highest Rated":
        return sorted(products, key=lambda x: x['rating'], reverse=True)
    elif sort_by == "🔥 Most Popular":
        return sorted(products, key=lambda x: x.get('popularity', x['rating']), reverse=True)
    else:  # Newest First
        return sorted(products, key=lambda x: x['id'], reverse=True)

# Page content
if search_query:
    # Search results
    st.markdown(f'<div class="category-header">🔍 Search Results for "{search_query}"</div>', unsafe_allow_html=True)
    search_results = search_products(search_query)
    
    if search_results:
        cols = st.columns(3)
        for idx, product in enumerate(search_results):
            with cols[idx % 3]:
                display_product_card(product, "Search")
    else:
        st.write("No products found. Try different keywords.")

elif page == "🏠 Home":
    # Hero section
    st.markdown("""
    <div style="background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%); 
                padding: 3rem; border-radius: 20px; text-align: center; margin: 2rem 0; color: white;">
        <h2 style="font-size: 2.5rem; margin-bottom: 1rem;">🔥 GenZ Fashion Revolution</h2>
        <p style="font-size: 1.2rem;">Discover the latest trends in jeans and tops designed specifically for Generation Z</p>
        <p style="font-size: 1rem; margin-top: 1rem;">✨ Free shipping on orders above ₹1999 | 🔄 30-day returns | 💯 Authentic products</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Stats section
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="stats-card"><h3>1000+</h3><p>Happy Customers</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="stats-card"><h3>50+</h3><p>Product Varieties</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="stats-card"><h3>4.8⭐</h3><p>Average Rating</p></div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="stats-card"><h3>24/7</h3><p>Customer Support</p></div>', unsafe_allow_html=True)
    
    # Featured products
    st.markdown('<div class="category-header">⭐ Featured Products</div>', unsafe_allow_html=True)
    
    # Get featured products (highest rated from each category)
    featured = []
    for category, subcategories in products_database.items():
        if isinstance(subcategories, dict):
            for subcat, products in subcategories.items():
                if products:
                    featured.append(max(products, key=lambda x: x['rating']))
        else:
            if subcategories:
                featured.append(max(subcategories, key=lambda x: x['rating']))
    
    cols = st.columns(3)
    for idx, product in enumerate(featured[:6]):
        with cols[idx % 3]:
            display_product_card(product, "Featured")
    
    # Categories showcase
    st.markdown('<div class="category-header">🛍️ Shop by Category</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    categories = [
        ("👖 Boys Jeans", "20+ Styles", "#667eea"),
        ("👕 Boys Tops", "15+ Designs", "#4ECDC4"),
        ("👗 Girls Jeans", "18+ Styles", "#FF6B35"),
        ("👚 Girls Tops", "12+ Designs", "#764ba2")
    ]
    
    for idx, (cat_name, cat_desc, color) in enumerate(categories):
        with [col1, col2, col3, col4][idx]:
            st.markdown(f"""
            <div class="product-card" style="text-align: center; min-height: 200px; 
                     background: linear-gradient(135deg, {color} 0%, {color}88 100%); 
                     color: white; cursor: pointer;">
                <h3 style="font-size: 1.5rem; margin-bottom: 1rem;">{cat_name}</h3>
                <p style="font-size: 1.1rem; font-weight: 600;">{cat_desc}</p>
                <p style="margin-top: 1rem; font-size: 0.9rem;">Click to explore →</p>
            </div>
            """, unsafe_allow_html=True)

elif page == "👖 Boys Jeans":
    st.markdown('<div class="category-header">👖 Boys Jeans Collection</div>', unsafe_allow_html=True)
    
    for subcategory, products in products_database["Boys Jeans"].items():
        # Apply filters
        filtered_products = filter_products(products, price_range, selected_sizes, selected_colors, min_rating)
        sorted_products = sort_products(filtered_products, sort_by)
        
        if sorted_products:
            st.markdown(f"### 🔹 {subcategory} Jeans ({len(sorted_products)} items)")
            cols = st.columns(3)
            for idx, product in enumerate(sorted_products):
                with cols[idx % 3]:
                    display_product_card(product, "Boys Jeans", subcategory)

elif page == "👕 Boys Tops":
    st.markdown('<div class="category-header">👕 Boys Tops Collection</div>', unsafe_allow_html=True)
    
    # Apply filters
    filtered_products = filter_products(products_database["Boys Tops"], price_range, selected_sizes, selected_colors, min_rating)
    sorted_products = sort_products(filtered_products, sort_by)
    
    if sorted_products:
        cols = st.columns(3)
        for idx, product in enumerate(sorted_products):
            with cols[idx % 3]:
                display_product_card(product, "Boys Tops")

elif page == "👗 Girls Jeans":
    st.markdown('<div class="category-header">👗 Girls Jeans Collection</div>', unsafe_allow_html=True)
    
    for subcategory, products in products_database["Girls Jeans"].items():
        # Apply filters
        filtered_products = filter_products(products, price_range, selected_sizes, selected_colors, min_rating)
        sorted_products = sort_products(filtered_products, sort_by)
        
        if sorted_products:
            st.markdown(f"### 🔹 {subcategory} Jeans ({len(sorted_products)} items)")
            cols = st.columns(3)
            for idx, product in enumerate(sorted_products):
                with cols[idx % 3]:
                    display_product_card(product, "Girls Jeans", subcategory)

elif page == "👚 Girls Tops":
    st.markdown('<div class="category-header">👚 Girls Tops Collection</div>', unsafe_allow_html=True)
    
    # Apply filters
    filtered_products = filter_products(products_database["Girls Tops"], price_range, selected_sizes, selected_colors, min_rating)
    sorted_products = sort_products(filtered_products, sort_by)
    
    if sorted_products:
        cols = st.columns(3)
        for idx, product in enumerate(sorted_products):
            with cols[idx % 3]:
                display_product_card(product, "Girls Tops")

elif page == "🛒 Cart":
    st.markdown('<div class="category-header">🛒 Your Shopping Cart</div>', unsafe_allow_html=True)
    
    if st.session_state.cart:
        # Cart items
        for idx, item in enumerate(st.session_state.cart):
            image_url = get_image_url(item['image'])
            
            st.markdown(f"""
            <div class="cart-item">
                <div style="display: flex; align-items: center; gap: 1rem;">
                    <img src="{image_url}" style="width: 100px; height: 100px; object-fit: cover; border-radius: 10px;">
                    <div style="flex-grow: 1;">
                        <h4 style="margin: 0; color: #333;">{item['name']}</h4>
                        <p style="margin: 0.5rem 0; color: #666;">Size: {item['size']} | Color: {item['color']}</p>
                        <p style="margin: 0; font-weight: 600; color: #FF6B35; font-size: 1.2rem;">₹{item['price']} × {item['quantity']} = ₹{item['price'] * item['quantity']}</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Quantity controls
            col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 2, 1])
            with col1:
                if st.button("➖", key=f"dec_{idx}"):
                    update_cart_quantity(idx, item['quantity'] - 1)
                    st.rerun()
            with col2:
                st.write(f"**{item['quantity']}**")
            with col3:
                if st.button("➕", key=f"inc_{idx}"):
                    update_cart_quantity(idx, item['quantity'] + 1)
                    st.rerun()
            with col5:
                if st.button("🗑️", key=f"remove_{idx}"):
                    remove_from_cart(idx)
                    st.rerun()
        
        # Cart summary
        st.markdown("---")
        subtotal = calculate_cart_total()
        shipping = 0 if subtotal >= 1999 else 99
        tax = int(subtotal * 0.18)
        total = subtotal + shipping + tax
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("### 💰 Order Summary")
            st.write(f"**Subtotal:** ₹{subtotal}")
            st.write(f"**Shipping:** ₹{shipping} {'🆓 FREE' if shipping == 0 else ''}")
            st.write(f"**Tax (18%):** ₹{tax}")
            st.markdown(f"**🎯 Total: ₹{total}**")
        
        with col2:
            st.markdown("### 🚀 Quick Actions")
            if st.button("🛒 Proceed to Checkout", type="primary"):
                st.session_state.current_page = "Checkout"
                st.rerun()
            if st.button("🧹 Clear Cart", type="secondary"):
                st.session_state.cart = []
                st.rerun()
    else:
        st.markdown("""
        <div style="text-align: center; padding: 3rem; background: #f8f9fa; border-radius: 15px;">
            <h3>🛒 Your cart is empty</h3>
            <p>Discover amazing fashion items and add them to your cart!</p>
        </div>
        """, unsafe_allow_html=True)

elif page == "💝 Wishlist":
    st.markdown('<div class="category-header">💝 Your Wishlist</div>', unsafe_allow_html=True)
    
    if st.session_state.wishlist:
        cols = st.columns(3)
        for idx, product in enumerate(st.session_state.wishlist):
            with cols[idx % 3]:
                display_product_card(product, "Wishlist")
                if st.button("❌ Remove from Wishlist", key=f"remove_wish_{idx}"):
                    st.session_state.wishlist.pop(idx)
                    st.rerun()
    else:
        st.write("Your wishlist is empty. Start adding products you love!")

elif page == "👤 Profile":
    st.markdown('<div class="category-header">👤 My Profile</div>', unsafe_allow_html=True)
    
    # Display current profile
    st.markdown(f"""
    <div class="user-info-card">
        <h3>👋 User Information</h3>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1rem;">
            <div><strong>Name:</strong> {st.session_state.user_info.get('first_name', '')} {st.session_state.user_info.get('last_name', '')}</div>
            <div><strong>Email:</strong> {st.session_state.user_info.get('email', '')}</div>
            <div><strong>Phone:</strong> {st.session_state.user_info.get('phone', '')}</div>
            <div><strong>Age:</strong> {st.session_state.user_info.get('age', 'N/A')}</div>
            <div style="grid-column: 1 / -1;"><strong>Address:</strong> {st.session_state.user_info.get('address', '')}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Update profile section
    with st.expander("✏️ Update Profile Information"):
        with st.form("update_profile"):
            col1, col2 = st.columns(2)
            with col1:
                new_first_name = st.text_input("First Name", value=st.session_state.user_info.get('first_name', ''))
                new_email = st.text_input("Email", value=st.session_state.user_info.get('email', ''))
                new_age = st.number_input("Age", min_value=13, max_value=100, value=st.session_state.user_info.get('age', 20))
            with col2:
                new_last_name = st.text_input("Last Name", value=st.session_state.user_info.get('last_name', ''))
                new_phone = st.text_input("Phone", value=st.session_state.user_info.get('phone', ''))
                new_gender = st.selectbox("Gender", ["Male", "Female", "Other", "Prefer not to say"], 
                                        index=0 if not st.session_state.user_info.get('gender') else 
                                        ["Male", "Female", "Other", "Prefer not to say"].index(st.session_state.user_info.get('gender', 'Male')))
            
            new_address = st.text_area("Address", value=st.session_state.user_info.get('address', ''))
            
            if st.form_submit_button("💾 Update Profile", type="primary"):
                # Validation
                if validate_name(new_first_name) and validate_name(new_last_name) and validate_email(new_email) and validate_phone(new_phone):
                    st.session_state.user_info.update({
                        'first_name': new_first_name,
                        'last_name': new_last_name,
                        'email': new_email,
                        'phone': new_phone,
                        'address': new_address,
                        'age': new_age,
                        'gender': new_gender
                    })
                    st.success("✅ Profile updated successfully!")
                    st.rerun()
                else:
                    st.error("Please check your information and try again")

elif page == "📦 My Orders":
    st.markdown('<div class="category-header">📦 Order History</div>', unsafe_allow_html=True)
    
    if st.session_state.orders:
        for order in reversed(st.session_state.orders):  # Show latest first
            status_color = "#28a745" if "Confirmed" in order['status'] else "#17a2b8"
            
            st.markdown(f"""
            <div class="cart-item">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div>
                        <h4 style="margin: 0; color: #333;">📋 Order #{order['order_id']}</h4>
                        <p style="margin: 0.5rem 0; color: #666;"><strong>Date:</strong> {order['date']}</p>
                        <p style="margin: 0; color: #666;"><strong>Items:</strong> {order['item_count']} items</p>
                        <p style="margin: 0.5rem 0; font-size: 1.2rem; font-weight: 600; color: #FF6B35;">
                            <strong>Total: ₹{order['total']}</strong>
                        </p>
                    </div>
                    <div style="text-align: right;">
                        <span style="background: {status_color}; color: white; padding: 0.5rem 1rem; 
                                   border-radius: 20px; font-weight: 600; font-size: 0.9rem;">
                            {order['status']}
                        </span>
                        <p style="margin-top: 0.5rem; font-size: 0.8rem; color: #666;">
                            Expected delivery: 3-5 days
                        </p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align: center; padding: 3rem; background: #f8f9fa; border-radius: 15px;">
            <h3>📦 No orders yet</h3>
            <p>Your order history will appear here once you make your first purchase!</p>
        </div>
        """, unsafe_allow_html=True)

# Checkout process
if hasattr(st.session_state, 'current_page') and st.session_state.current_page == "Checkout":
    st.markdown('<div class="category-header">💳 Secure Checkout</div>', unsafe_allow_html=True)
    
    if st.session_state.cart:
        col1, col2 = st.columns([3, 2])
        
        with col1:
            # Order summary
            st.subheader("📋 Order Summary")
            total = 0
            for item in st.session_state.cart:
                image_url = get_image_url(item['image'])
                item_total = item['price'] * item['quantity']
                total += item_total
                
                st.markdown(f"""
                <div style="display: flex; align-items: center; gap: 1rem; padding: 1rem; 
                           background: white; border-radius: 10px; margin: 0.5rem 0; 
                           box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    <img src="{image_url}" style="width: 60px; height: 60px; object-fit: cover; border-radius: 8px;">
                    <div style="flex-grow: 1;">
                        <strong>{item['name']}</strong><br>
                        <small>Size: {item['size']} | Color: {item['color']} | Qty: {item['quantity']}</small><br>
                        <span style="color: #FF6B35; font-weight: 600;">₹{item_total}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Pricing breakdown
            shipping = 0 if total >= 1999 else 99
            tax = int(total * 0.18)
            final_total = total + shipping + tax
            
            st.markdown("---")
            st.markdown(
    f"""
    <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 10px;">
        <div style="display: flex; justify-content: space-between; margin: 0.5rem 0;">
            <span>Subtotal:</span><span>₹{total}</span>
        </div>
        <div style="display: flex; justify-content: space-between; margin: 0.5rem 0;">
            <span>Tax:</span><span>₹{total * 0.18:.2f}</span>
        </div>
        <hr>
        <div style="display: flex; justify-content: space-between; margin: 0.5rem 0; font-weight: bold;">
            <span>Total:</span><span>₹{total * 1.18:.2f}</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)