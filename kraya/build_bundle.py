import os
import re

def build_bundle():
    print("Starting Kraya compilation & bundling...")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 1. Read CSS
    css_path = os.path.join(base_dir, 'styles.css')
    with open(css_path, 'r', encoding='utf-8') as f:
        css_content = f.read()
        
    # 2. Read DB
    db_path = os.path.join(base_dir, 'js', 'db.js')
    with open(db_path, 'r', encoding='utf-8') as f:
        db_content = f.read()
    
    # Clean export statement from db.js
    db_content = re.sub(r'export const db =', 'const db =', db_content)
    
    # Rewrite product image paths to point to absolute GitHub Pages URLs
    # so they render perfectly inside any sandboxed iframe
    github_assets_url = "https://pramodakumarpradhan.github.io/PySphereArcade/kraya/assets/product_images/"
    db_content = db_content.replace("assets/product_images/", github_assets_url)
    
    # 3. Read Components
    components = ['reseller', 'catalog', 'detail', 'cart', 'profile', 'seller']
    components_js = ""
    
    for comp in components:
        comp_path = os.path.join(base_dir, 'js', 'components', f'{comp}.js')
        with open(comp_path, 'r', encoding='utf-8') as f:
            comp_content = f.read()
            
        # Clean import and export statements
        comp_content = re.sub(r'import\s+[\s\S]*?from\s+[\'"].*?[\'"];?', '', comp_content)
        comp_content = re.sub(r'export function render\(', f'function render_{comp}(', comp_content)
        comp_content = re.sub(r'export function triggerResellerModal\(', 'function triggerResellerModal(', comp_content)
        
        components_js += f"\n// --- COMPONENT: {comp} ---\n" + comp_content + "\n"
        
    # 4. Read App.js
    app_path = os.path.join(base_dir, 'js', 'app.js')
    with open(app_path, 'r', encoding='utf-8') as f:
        app_content = f.read()
        
    # Clean import and export statements from app.js
    app_content = re.sub(r'import\s+[\s\S]*?from\s+[\'"].*?[\'"];?', '', app_content)
    app_content = re.sub(r'export const CATEGORY_MAP =', 'const CATEGORY_MAP =', app_content)
    app_content = re.sub(r'export const state =', 'const state =', app_content)
    app_content = re.sub(r'export function updateBadges\(', 'function updateBadges(', app_content)
    app_content = re.sub(r'export function renderCartDrawerList\(', 'function renderCartDrawerList(', app_content)
    app_content = re.sub(r'export function openModal\(', 'function openModal(', app_content)
    app_content = re.sub(r'export function closeModal\(', 'function closeModal(', app_content)
    app_content = re.sub(r'export function navigateToRoute\(', 'function navigateToRoute(', app_content)
    
    # Replace dynamic component loader in app.js with local direct mapping calls
    old_loader = """async function loadComponent(componentName, params) {
  // Show spinner while loading
  viewport.innerHTML = `
    <div class="container d-flex align-center justify-center" style="padding: 100px 0; justify-content: center;">
      <div class="spinner"></div>
    </div>`;
    
  try {
    // Import module dynamically
    const module = await import(`./components/${componentName}.js`);
    
    // Call the rendering method inside the component module
    if (module.render) {
      module.render(viewport, params);
      window.scrollTo(0, 0);
      lucide.createIcons();
    } else {
      viewport.innerHTML = `<div class="container" style="padding: 40px 0; text-align:center; color: var(--error);">Error: render function not found in ${componentName} module.</div>`;
    }
  } catch (error) {
    console.error("Component load failed:", error);
    viewport.innerHTML = `<div class="container" style="padding: 40px 0; text-align:center; color: var(--error);">
      <h3>Could not load page</h3>
      <p style="margin-top: 10px; color: var(--text-muted);">${error.message}</p>
      <button class="supplier-btn" style="margin-top: 20px;" onclick="window.location.reload()">Reload Application</button>
    </div>`;
  }
}"""

    new_loader = """async function loadComponent(componentName, params) {
  viewport.innerHTML = `
    <div class="container d-flex align-center justify-center" style="padding: 100px 0; justify-content: center;">
      <div class="spinner"></div>
    </div>`;
    
  try {
    // Direct call mapping instead of dynamic import
    if (componentName === 'catalog') {
      render_catalog(viewport, params);
    } else if (componentName === 'detail') {
      render_detail(viewport, params);
    } else if (componentName === 'cart') {
      render_cart(viewport, params);
    } else if (componentName === 'profile') {
      render_profile(viewport, params);
    } else if (componentName === 'seller') {
      render_seller(viewport, params);
    } else {
      throw new Error("Component " + componentName + " not found.");
    }
    window.scrollTo(0, 0);
    lucide.createIcons();
  } catch (error) {
    console.error("Component load failed:", error);
    viewport.innerHTML = `<div class="container" style="padding: 40px 0; text-align:center; color: var(--error);">
      <h3>Could not load page</h3>
      <p style="margin-top: 10px; color: var(--text-muted);">${error.message}</p>
      <button class="supplier-btn" style="margin-top: 20px;" onclick="window.location.reload()">Reload Application</button>
    </div>`;
  }
}"""

    app_content = app_content.replace(old_loader, new_loader)
    
    # 5. Compile JS tag
    compiled_js = f"""
// --- DATABASE ---
{db_content}

// --- COMPONENTS ---
{components_js}

// --- CORE APP CONTROLLER ---
{app_content}
"""

    # 6. Read index.html shell
    index_path = os.path.join(base_dir, 'index.html')
    with open(index_path, 'r', encoding='utf-8') as f:
        html_shell = f.read()
        
    # Inject CSS
    css_replacement = f"<style>\n{css_content}\n</style>"
    html_shell = re.sub(r'<link rel="stylesheet" href="styles.css">', css_replacement, html_shell)
    
    # Inject JS
    js_replacement = f"<script>\n{compiled_js}\n</script>"
    html_shell = re.sub(r'<script type="module" src="js/app.js"></script>', js_replacement, html_shell)
    
    # Write to target Streamlit bundle HTML
    output_path = os.path.join(base_dir, 'index_streamlit.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_shell)
        
    print(f"Bundling complete! Created self-contained file: {output_path}")

if __name__ == '__main__':
    build_bundle()
