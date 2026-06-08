// Kraya Mock Database & LocalStorage Manager

const INITIAL_PRODUCTS = [
  {
    id: 1,
    name: "Premium Embroidered Pink Georgette Saree",
    description: "Indulge in classic elegance with this premium pink georgette saree, featuring gorgeous gold floral embroidery along the border. Highly popular for weddings, festive occasions, and evening wear. Comes with a matching unstitched blouse piece.",
    price: 1299,
    originalPrice: 2599,
    discount: 50,
    rating: 4.3,
    reviewsCount: 320,
    image: "assets/product_images/designer_pink_saree.png",
    images: [
      "assets/product_images/designer_pink_saree.png",
      "assets/product_images/designer_pink_saree.png"
    ],
    category: "Women Ethnic",
    subcategory: "Sarees",
    sizes: ["Free Size"],
    freeDelivery: true,
    codAvailable: true,
    seller: {
      name: "Radhe Gobind Creation",
      rating: 4.2,
      followers: 8400,
      productCount: 142
    },
    details: {
      "Fabric": "Georgette",
      "Pattern": "Embroidered",
      "Color": "Pink & Gold",
      "Saree Length": "5.5 meters",
      "Blouse Piece": "0.8 meters (Unstitched)",
      "Occasion": "Festive / Wedding"
    },
    reviews: [
      { name: "Ananya S.", rating: 5, comment: "Beautiful saree! The embroidery is very neat and looks premium. Exactly like meesho photos.", date: "2026-05-20" },
      { name: "Priya M.", rating: 4, comment: "Saree is very soft and light. Good value for money.", date: "2026-05-18" },
      { name: "Ritu K.", rating: 4, comment: "Color is exactly as shown. Perfect for family events.", date: "2026-05-10" }
    ]
  },
  {
    id: 2,
    name: "Men's Sky Blue Casual Cotton Shirt",
    description: "Elevate your daily style with this lightweight sky blue cotton shirt. Designed with a structured slim fit, full sleeves, and a classic collar, it transitions effortlessly from office meetings to weekend social outings.",
    price: 499,
    originalPrice: 999,
    discount: 50,
    rating: 4.1,
    reviewsCount: 185,
    image: "assets/product_images/mens_slimfit_shirt.png",
    images: [
      "assets/product_images/mens_slimfit_shirt.png"
    ],
    category: "Men",
    subcategory: "Shirts",
    sizes: ["S", "M", "L", "XL"],
    freeDelivery: true,
    codAvailable: true,
    seller: {
      name: "Vogue Fabrications",
      rating: 3.9,
      followers: 1200,
      productCount: 45
    },
    details: {
      "Fabric": "100% Breathable Cotton",
      "Fit": "Slim Fit",
      "Color": "Sky Blue",
      "Sleeve": "Full Sleeves",
      "Neck": "Collar Neck",
      "Care": "Machine wash cold"
    },
    reviews: [
      { name: "Rohan D.", rating: 4, comment: "Fitting is perfect. The fabric feels soft and breathable.", date: "2026-05-25" },
      { name: "Suresh P.", rating: 5, comment: "Amazing shirt at just 499! Best purchase in a while.", date: "2026-05-21" }
    ]
  },
  {
    id: 3,
    name: "Sleek Black AMOLED Smart Watch",
    description: "Track your fitness, notifications, and vital stats with this premium black smart sports watch. Featuring a vibrant 1.43\" AMOLED display, IP68 waterproofing, 7-day battery life, and 100+ active sports modes.",
    price: 1999,
    originalPrice: 4999,
    discount: 60,
    rating: 4.5,
    reviewsCount: 540,
    image: "assets/product_images/smart_sports_watch.png",
    images: [
      "assets/product_images/smart_sports_watch.png"
    ],
    category: "Electronics",
    subcategory: "Smartwatches",
    sizes: ["Free Size"],
    freeDelivery: true,
    codAvailable: true,
    seller: {
      name: "PulseTech Electronics",
      rating: 4.4,
      followers: 12500,
      productCount: 88
    },
    details: {
      "Display": "1.43 inch AMOLED Touch",
      "Battery Life": "Up to 7-10 Days",
      "Water Resistance": "IP68 dust & water proof",
      "Sensors": "Heart Rate, SpO2, Sleep Tracker",
      "Bluetooth Calling": "Yes, enabled"
    },
    reviews: [
      { name: "Amit G.", rating: 5, comment: "The AMOLED screen is beautiful! Very bright under sunlight. Calling works clear.", date: "2026-05-30" },
      { name: "Kunal S.", rating: 4, comment: "Good health tracking. UI is very smooth. Recommended.", date: "2026-05-28" }
    ]
  },
  {
    id: 4,
    name: "Traditional Gold-Plated Bridal Necklace Set",
    description: "Adorn yourself with royal grandeur. This traditional set includes a choker-style gold-plated necklace with intricate kundan and pearl droplets, paired with matching heavy jhumka earrings. Perfect for bridal and ceremonial wear.",
    price: 899,
    originalPrice: 2999,
    discount: 70,
    rating: 4.2,
    reviewsCount: 98,
    image: "assets/product_images/gold_plated_necklace.png",
    images: [
      "assets/product_images/gold_plated_necklace.png"
    ],
    category: "Jewellery & Accessories",
    subcategory: "Jewellery Sets",
    sizes: ["Free Size"],
    freeDelivery: true,
    codAvailable: true,
    seller: {
      name: "Sagarika Jewellers",
      rating: 4.1,
      followers: 3400,
      productCount: 210
    },
    details: {
      "Material": "Brass alloy, Gold plated",
      "Stone Type": "Kundan & Pearls",
      "Set Contents": "1 Necklace, 2 Earrings",
      "Closure": "Adjustable Thread / Drawstring",
      "Weight": "115 grams"
    },
    reviews: [
      { name: "Meena B.", rating: 5, comment: "It looks so heavy and royal! Everyone asked me where I bought it from.", date: "2026-05-22" },
      { name: "Seema R.", rating: 4, comment: "Nice quality. Shine is good, didn't blacken after first use.", date: "2026-05-15" }
    ]
  },
  {
    id: 5,
    name: "Sleek White Wireless ANC Earbuds",
    description: "Immerse yourself in premium audio. These white wireless earbuds feature Hybrid Active Noise Cancellation, high-fidelity dynamic drivers, ultra-low latency gaming mode, and a total playtime of up to 30 hours with the case.",
    price: 1499,
    originalPrice: 3999,
    discount: 62,
    rating: 4.4,
    reviewsCount: 215,
    image: "assets/product_images/wireless_earbuds.png",
    images: [
      "assets/product_images/wireless_earbuds.png"
    ],
    category: "Electronics",
    subcategory: "Earbuds",
    sizes: ["Free Size"],
    freeDelivery: true,
    codAvailable: true,
    seller: {
      name: "PulseTech Electronics",
      rating: 4.4,
      followers: 12500,
      productCount: 88
    },
    details: {
      "Bluetooth Version": "v5.3",
      "Noise Cancellation": "Active Noise Cancellation (ANC)",
      "Playtime": "Up to 30 Hours (with Case)",
      "Driver Size": "10mm dynamic driver",
      "Charging Port": "Type-C Fast charging"
    },
    reviews: [
      { name: "Vikram N.", rating: 5, comment: "Sound quality is superb, bass is deep. Noise cancellation works very well in office.", date: "2026-06-01" },
      { name: "Anjali T.", rating: 4, comment: "Very comfortable fit. Case looks premium and stylish.", date: "2026-05-29" }
    ]
  },
  {
    id: 6,
    name: "Floral Print A-Line Kurti & Palazzo Set",
    description: "Casual elegance redefined. A matching floral printed cotton A-line kurti with flared palazzo pants. Very soft and lightweight fabric, suitable for office or daily wear.",
    price: 599,
    originalPrice: 1499,
    discount: 60,
    rating: 4.0,
    reviewsCount: 230,
    image: "custom:gradient_kurti",
    images: [],
    category: "Women Ethnic",
    subcategory: "Kurtis",
    sizes: ["M", "L", "XL", "XXL"],
    freeDelivery: true,
    codAvailable: true,
    seller: {
      name: "Radhe Gobind Creation",
      rating: 4.2,
      followers: 8400,
      productCount: 142
    },
    details: {
      "Fabric": "Crepe Cotton Blend",
      "Pattern": "Floral Printed",
      "Sleeve": "3/4 Sleeves",
      "Set Contents": "1 Kurti, 1 Palazzo",
      "Length": "Calf Length"
    },
    reviews: [
      { name: "Kirti P.", rating: 4, comment: "Very comfortable. Fabric is light and breathable. Ideal for summer.", date: "2026-05-15" }
    ]
  },
  {
    id: 7,
    name: "Women's High-Rise Slim Fit Stretch Jeans",
    description: "Classic high-waisted stretch denim jeans featuring a five-pocket layout, zip fly, and button closure. Engineered with stretch fabric to offer comfort and body-hugging aesthetics.",
    price: 699,
    originalPrice: 1799,
    discount: 61,
    rating: 4.2,
    reviewsCount: 120,
    image: "custom:gradient_jeans",
    images: [],
    category: "Women Western",
    subcategory: "Jeans",
    sizes: ["28", "30", "32", "34"],
    freeDelivery: true,
    codAvailable: true,
    seller: {
      name: "Vogue Fabrications",
      rating: 3.9,
      followers: 1200,
      productCount: 45
    },
    details: {
      "Fabric": "Cotton Stretchable Denim",
      "Fit": "Slim Fit",
      "Rise": "High Rise",
      "Length": "Ankle Length",
      "Wash Care": "Do not bleach, wash inside out"
    },
    reviews: [
      { name: "Pooja V.", rating: 5, comment: "Perfect stretch! Very comfortable around the waist. True to size.", date: "2026-05-19" }
    ]
  },
  {
    id: 8,
    name: "Classic Regular Fit Men's Polo T-Shirt",
    description: "Add a touch of sophistication to your casual wear with this solid cotton-pique polo t-shirt. Features a rib-knit collar, two-button placket, and short sleeves with ribbed cuffs.",
    price: 349,
    originalPrice: 799,
    discount: 56,
    rating: 4.1,
    reviewsCount: 390,
    image: "custom:gradient_polo",
    images: [],
    category: "Men",
    subcategory: "T-Shirts",
    sizes: ["M", "L", "XL"],
    freeDelivery: true,
    codAvailable: true,
    seller: {
      name: "Tees & Hoods Store",
      rating: 4.0,
      followers: 4300,
      productCount: 156
    },
    details: {
      "Fabric": "Pique Cotton",
      "Pattern": "Solid",
      "Sleeve Length": "Short Sleeves",
      "Neck": "Polo Collar"
    },
    reviews: [
      { name: "Rishabh S.", rating: 4, comment: "Good quality polo for 350. Color didn't bleed after wash.", date: "2026-05-12" }
    ]
  },
  {
    id: 9,
    name: "Kids Cotton Unsex Graphic Print Set",
    description: "Cute, soft cotton t-shirt and shorts set designed for toddlers. Featuring quirky cartoon prints, elasticated waistbands, and tagless neckline to prevent itching.",
    price: 299,
    originalPrice: 599,
    discount: 50,
    rating: 4.3,
    reviewsCount: 78,
    image: "custom:gradient_kids_set",
    images: [],
    category: "Kids",
    subcategory: "Sets & Suits",
    sizes: ["2-3 Y", "3-4 Y", "4-5 Y"],
    freeDelivery: true,
    codAvailable: true,
    seller: {
      name: "TinyTots Clothing",
      rating: 4.3,
      followers: 2100,
      productCount: 60
    },
    details: {
      "Fabric": "100% Organic Cotton",
      "Set Contents": "1 Printed Tee, 1 Matching Shorts",
      "Gender": "Unisex",
      "Fit": "Regular Comfort Fit"
    },
    reviews: [
      { name: "Neha D.", rating: 5, comment: "Extremely soft cotton. My kid loves the cartoon prints. Will buy more.", date: "2026-05-24" }
    ]
  },
  {
    id: 10,
    name: "Premium Double Bedsheet with Pillow Covers",
    description: "Dress your master bedroom with this luxurious double bedsheet. Woven with 250 Thread Count microfiber cotton for an ultra-soft feel. Includes two matching pillow covers.",
    price: 499,
    originalPrice: 1299,
    discount: 61,
    rating: 4.2,
    reviewsCount: 412,
    image: "custom:gradient_bedsheet",
    images: [],
    category: "Home & Kitchen",
    subcategory: "Bedsheets",
    sizes: ["Double King"],
    freeDelivery: true,
    codAvailable: true,
    seller: {
      name: "Comfort Nest Decor",
      rating: 4.1,
      followers: 5100,
      productCount: 112
    },
    details: {
      "Fabric": "Microfiber Cotton Blend",
      "Thread Count": "250 TC",
      "Size": "228 cm x 274 cm (90x108 inch)",
      "Pillow Cover Size": "46 cm x 69 cm (18x27 inch)",
      "Print": "Floral/Abstract"
    },
    reviews: [
      { name: "Vandana P.", rating: 4, comment: "Very large bedsheet, fits perfectly on my king-size bed. Colors are fast.", date: "2026-05-22" }
    ]
  },
  {
    id: 11,
    name: "Waterproof Matte Long-Lasting Lipstick",
    description: "Stays stunning all day. A highly pigmented liquid matte lipstick that provides a weightless, non-drying finish. Transfer-proof, waterproof, and enriched with Vitamin E.",
    price: 189,
    originalPrice: 399,
    discount: 52,
    rating: 4.0,
    reviewsCount: 650,
    image: "custom:gradient_lipstick",
    images: [],
    category: "Beauty & Health",
    subcategory: "Makeup",
    sizes: ["Free Size"],
    freeDelivery: true,
    codAvailable: true,
    seller: {
      name: "Glamour Secrets",
      rating: 4.2,
      followers: 18000,
      productCount: 220
    },
    details: {
      "Finish": "Liquid Matte Finish",
      "Duration": "Up to 16 Hours stay",
      "Weight": "5ml",
      "Key Ingredients": "Vitamin E, Jojoba Oil",
      "Cruelty-Free": "Yes, verified"
    },
    reviews: [
      { name: "Riya S.", rating: 5, comment: "It does not smudge at all! Beautiful red shade. Love it.", date: "2026-05-27" }
    ]
  },
  {
    id: 12,
    name: "Unisex Retro Aviator Sunglasses",
    description: "Protect your eyes with style. Classic retro metal aviator sunglasses with polarized UV400 lenses. Durable lightweight frame with comfortable silicone nose pads.",
    price: 249,
    originalPrice: 999,
    discount: 75,
    rating: 4.1,
    reviewsCount: 154,
    image: "custom:gradient_sunglasses",
    images: [],
    category: "Jewellery & Accessories",
    subcategory: "Sunglasses",
    sizes: ["Free Size"],
    freeDelivery: true,
    codAvailable: true,
    seller: {
      name: "Style & Shade Corp",
      rating: 4.0,
      followers: 3800,
      productCount: 95
    },
    details: {
      "Frame Material": "Stainless Steel",
      "Lens Material": "Polarized Polycarbonate",
      "UV Protection": "100% UV400 Protection",
      "Frame Size": "Medium fit"
    },
    reviews: [
      { name: "Abhishek K.", rating: 4, comment: "Classy glasses, very sturdy frame. Polarized lenses are great while driving.", date: "2026-05-18" }
    ]
  },
  {
    id: 13,
    name: "Classic Women's Handbag with Sling Strap",
    description: "Carry your essentials elegantly. Crafted from durable textured faux leather, this structured handbag features twin handle loops, zippered compartments, and an adjustable, detachable shoulder sling strap.",
    price: 450,
    originalPrice: 1299,
    discount: 65,
    rating: 4.2,
    reviewsCount: 304,
    image: "custom:gradient_bag",
    images: [],
    category: "Bags & Footwear",
    subcategory: "Bags",
    sizes: ["Free Size"],
    freeDelivery: true,
    codAvailable: true,
    seller: {
      name: "LeatherCraft Accessories",
      rating: 4.1,
      followers: 7200,
      productCount: 124
    },
    details: {
      "Material": "Textured PU Leather",
      "Dimensions": "30cm x 12cm x 22cm",
      "Compartments": "2 main, 3 inner pockets",
      "Closure Type": "Zippered"
    },
    reviews: [
      { name: "Deepa N.", rating: 5, comment: "Outstanding handbag. Stitching is clean and the color is gorgeous.", date: "2026-05-23" }
    ]
  },
  {
    id: 14,
    name: "Men's Light Responsive Cushion Running Shoes",
    description: "Go the extra mile with supreme comfort. These running shoes feature a breathable fly-knit upper mesh, highly elastic responsive cushioning sole, and anti-skid rubber bottom traction.",
    price: 649,
    originalPrice: 1999,
    discount: 67,
    rating: 4.3,
    reviewsCount: 480,
    image: "custom:gradient_shoes",
    images: [],
    category: "Bags & Footwear",
    subcategory: "Footwear",
    sizes: ["6", "7", "8", "9", "10"],
    freeDelivery: true,
    codAvailable: true,
    seller: {
      name: "PulseTech Electronics", // Reuse supplier for mock convenience
      rating: 4.4,
      followers: 12500,
      productCount: 88
    },
    details: {
      "Material": "Flyknit mesh upper",
      "Sole Material": "EVA Responsive cushioning",
      "Closure": "Lace-Up",
      "Activity": "Running / Gym / Walking"
    },
    reviews: [
      { name: "Siddharth J.", rating: 4, comment: "Very lightweight shoes. Perfect fit, good cushioning for morning runs.", date: "2026-05-26" }
    ]
  },
  {
    id: 15,
    name: "Automatic Electric Hand Blender & Frother",
    description: "Whip up rich milk froths, coffee, or dressings in seconds. Powerful high-speed motor, stainless steel double spring whisk, operates on standard AA batteries.",
    price: 199,
    originalPrice: 499,
    discount: 60,
    rating: 3.9,
    reviewsCount: 820,
    image: "custom:gradient_frother",
    images: [],
    category: "Home & Kitchen",
    subcategory: "Kitchen Appliances",
    sizes: ["Free Size"],
    freeDelivery: true,
    codAvailable: true,
    seller: {
      name: "Comfort Nest Decor",
      rating: 4.1,
      followers: 5100,
      productCount: 112
    },
    details: {
      "Material": "ABS Plastic + Stainless Steel",
      "Power Source": "2 x AA Batteries (Not Included)",
      "Speed": "Single Speed high RPM",
      "Cleaning": "Wash whisk tip in warm soapy water"
    },
    reviews: [
      { name: "Mamta S.", rating: 4, comment: "Perfect for making cold coffee foam. Simple and works fast.", date: "2026-05-14" }
    ]
  }
];

const INITIAL_ADDRESSES = [
  {
    name: "Pramoda Kumar Pradhan",
    phone: "9876543210",
    houseNo: "Plot No. 124, 2nd Floor",
    roadName: "Sanjay Nagar Lane 3",
    pincode: "751001",
    city: "Bhubaneswar",
    state: "Odisha",
    isDefault: true
  }
];

// Helper to write to LocalStorage
function write(key, data) {
  localStorage.setItem(`kraya_${key}`, JSON.stringify(data));
}

// Helper to read from LocalStorage
function read(key, defaultData) {
  const value = localStorage.getItem(`kraya_${key}`);
  if (value === null) {
    write(key, defaultData);
    return defaultData;
  }
  try {
    return JSON.parse(value);
  } catch (e) {
    write(key, defaultData);
    return defaultData;
  }
}

// Database Operations
export const db = {
  // Initialize Database
  init() {
    read("products", INITIAL_PRODUCTS);
    read("cart", []);
    read("wishlist", []);
    read("orders", []);
    read("addresses", INITIAL_ADDRESSES);
    read("user", {
      name: "Pramoda Kumar Pradhan",
      email: "pramoda@kraya.com",
      phone: "9876543210",
      resellerBalance: 1250, // Reseller total earnings
      sharedProductsCount: 12
    });
  },

  // Products
  getProducts() {
    return read("products", INITIAL_PRODUCTS);
  },

  getProductById(id) {
    const products = this.getProducts();
    return products.find(p => p.id === Number(id));
  },

  addProduct(product) {
    const products = this.getProducts();
    // Auto increment ID
    const nextId = products.reduce((max, p) => p.id > max ? p.id : max, 0) + 1;
    product.id = nextId;
    product.rating = 5.0; // Brand new products default 5 stars
    product.reviewsCount = 0;
    product.reviews = [];
    
    // Add default values for visual comfort if not present
    if (!product.image) {
      product.image = "custom:gradient_added";
    }
    if (!product.images || product.images.length === 0) {
      product.images = [product.image];
    }
    
    products.unshift(product); // Add new items at the beginning
    write("products", products);
    return product;
  },

  updateProduct(updatedProduct) {
    const products = this.getProducts();
    const index = products.findIndex(p => p.id === updatedProduct.id);
    if (index !== -1) {
      products[index] = { ...products[index], ...updatedProduct };
      write("products", products);
      return true;
    }
    return false;
  },

  deleteProduct(id) {
    const products = this.getProducts();
    const filtered = products.filter(p => p.id !== Number(id));
    write("products", filtered);
    return true;
  },

  // Cart
  getCart() {
    return read("cart", []);
  },

  addToCart(productId, size, quantity = 1) {
    const cart = this.getCart();
    const product = this.getProductById(productId);
    if (!product) return false;

    const existingIndex = cart.findIndex(item => item.productId === Number(productId) && item.size === size);
    if (existingIndex !== -1) {
      cart[existingIndex].quantity += Number(quantity);
    } else {
      cart.push({
        productId: Number(productId),
        name: product.name,
        image: product.image,
        price: product.price,
        originalPrice: product.originalPrice,
        size: size,
        quantity: Number(quantity),
        sellerName: product.seller.name
      });
    }
    write("cart", cart);
    
    // Trigger local event to update headers
    window.dispatchEvent(new Event("kraya_cart_updated"));
    return true;
  },

  updateCartQuantity(productId, size, quantity) {
    const cart = this.getCart();
    const index = cart.findIndex(item => item.productId === Number(productId) && item.size === size);
    if (index !== -1) {
      if (Number(quantity) <= 0) {
        cart.splice(index, 1);
      } else {
        cart[index].quantity = Number(quantity);
      }
      write("cart", cart);
      window.dispatchEvent(new Event("kraya_cart_updated"));
      return true;
    }
    return false;
  },

  removeFromCart(productId, size) {
    const cart = this.getCart();
    const index = cart.findIndex(item => item.productId === Number(productId) && item.size === size);
    if (index !== -1) {
      cart.splice(index, 1);
      write("cart", cart);
      window.dispatchEvent(new Event("kraya_cart_updated"));
      return true;
    }
    return false;
  },

  clearCart() {
    write("cart", []);
    window.dispatchEvent(new Event("kraya_cart_updated"));
  },

  // Wishlist
  getWishlist() {
    return read("wishlist", []);
  },

  toggleWishlist(productId) {
    const wishlist = this.getWishlist();
    const id = Number(productId);
    const index = wishlist.indexOf(id);
    let added = false;
    
    if (index !== -1) {
      wishlist.splice(index, 1);
    } else {
      wishlist.push(id);
      added = true;
    }
    write("wishlist", wishlist);
    window.dispatchEvent(new Event("kraya_wishlist_updated"));
    return added;
  },

  isInWishlist(productId) {
    const wishlist = this.getWishlist();
    return wishlist.includes(Number(productId));
  },

  // Orders
  getOrders() {
    return read("orders", []);
  },

  createOrder(orderData) {
    const orders = this.getOrders();
    const nextId = "KR" + Math.floor(100000 + Math.random() * 900000);
    const date = new Date().toISOString().split("T")[0];
    
    const newOrder = {
      orderId: nextId,
      date: date,
      status: "Ordered", // Ordered -> Shipped -> Out for Delivery -> Delivered
      items: orderData.items,
      paymentMethod: orderData.paymentMethod,
      address: orderData.address,
      totals: orderData.totals,
      resellerMargin: orderData.resellerMargin || 0
    };

    orders.unshift(newOrder); // Newest order first
    write("orders", orders);

    // Update user balance if there was a reseller margin
    if (orderData.resellerMargin > 0) {
      const user = this.getCurrentUser();
      user.resellerBalance += Number(orderData.resellerMargin);
      this.updateCurrentUser(user);
    }

    return newOrder;
  },

  // Addresses
  getAddresses() {
    return read("addresses", INITIAL_ADDRESSES);
  },

  addAddress(address) {
    const addresses = this.getAddresses();
    if (address.isDefault) {
      addresses.forEach(a => a.isDefault = false);
    }
    addresses.push(address);
    write("addresses", addresses);
    return addresses;
  },

  deleteAddress(index) {
    const addresses = this.getAddresses();
    addresses.splice(index, 1);
    // If we deleted the default, set first one as default
    if (addresses.length > 0 && !addresses.some(a => a.isDefault)) {
      addresses[0].isDefault = true;
    }
    write("addresses", addresses);
    return addresses;
  },

  // User details
  getCurrentUser() {
    return read("user", {
      name: "Pramoda Kumar Pradhan",
      email: "pramoda@kraya.com",
      phone: "9876543210",
      resellerBalance: 1250,
      sharedProductsCount: 12
    });
  },

  updateCurrentUser(user) {
    write("user", user);
    window.dispatchEvent(new Event("kraya_user_updated"));
  }
};
