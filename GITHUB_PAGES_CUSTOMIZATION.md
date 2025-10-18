# GitHub Pages Customization Guide

## Dark Theme ✅

Your GitHub Pages site now has a **dark theme** applied! The theme uses GitHub's dark color scheme:
- Dark background (#0d1117)
- Light text (#c9d1d9)
- Blue accents (#58a6ff)
- Dark code blocks (#161b22)

The dark theme is automatically applied through `assets/css/style.scss`.

---

## Adding a Custom Banner

To add a banner image at the top of your pages:

### Step 1: Prepare Your Banner Image
- **Recommended size**: 1200x300 pixels (or similar wide aspect ratio)
- **Format**: PNG, JPG, or SVG
- **Theme**: Consider using SpellForce game artwork, fantasy themes, or modding-related imagery

### Step 2: Add the Image
1. Save your banner image as `banner.png` (or `banner.jpg`) in the `assets/images/` folder
2. You can name it anything, just remember the filename

### Step 3: Enable in Configuration
1. Open `_config.yml` in the root directory
2. Find this line:
   ```yaml
   # banner_image: /assets/images/banner.png
   ```
3. Uncomment it and update the path:
   ```yaml
   banner_image: /assets/images/banner.png
   ```

### Step 4: Commit and Push
```bash
git add assets/images/banner.png _config.yml
git commit -m "Add custom banner image"
git push
```

Wait a few minutes for GitHub Pages to rebuild, then refresh your site!

---

## Adding a Favicon (Browser Tab Icon)

To add a custom icon that appears in browser tabs:

### Option 1: Use Existing SpellForce Icons

You already have SpellForce icons available:
- `OriginalGameFiles/SpellForce_Addon.ico` - Breath of Winter
- `OriginalGameFiles/SpellForce_Addon2.ico` - Shadow of the Phoenix

**Steps**:
1. Copy one of these icons to `assets/images/`:
   ```bash
   copy "OriginalGameFiles\SpellForce_Addon.ico" "assets\images\favicon.ico"
   ```

2. Open `_config.yml` and uncomment:
   ```yaml
   favicon: /assets/images/favicon.ico
   ```

3. Commit and push:
   ```bash
   git add assets/images/favicon.ico _config.yml
   git commit -m "Add favicon"
   git push
   ```

### Option 2: Create a Custom Favicon

1. **Create or find an icon**:
   - Size: 16x16, 32x32, or 64x64 pixels
   - Format: .ico, .png, or .svg
   - Tools: Use Photoshop, GIMP, or online favicon generators

2. **Save as `favicon.ico`** (or `favicon.png`) in `assets/images/`

3. **Enable in `_config.yml`**:
   ```yaml
   favicon: /assets/images/favicon.ico
   ```

4. **Commit and push**

---

## File Structure

```
SpellSmut/
├── _config.yml                    # Site configuration
├── _layouts/
│   └── default.html              # Custom layout with banner/favicon support
├── assets/
│   ├── css/
│   │   └── style.scss            # Dark theme CSS
│   └── images/
│       ├── README.md             # Images folder guide
│       ├── banner.png            # (Add your banner here)
│       └── favicon.ico           # (Add your favicon here)
└── docs/
    └── index.md                  # Documentation homepage
```

---

## Testing Locally (Optional)

To preview your changes before pushing:

1. **Install Jekyll**:
   ```bash
   gem install bundler jekyll
   ```

2. **Create a Gemfile** in the root:
   ```ruby
   source "https://rubygems.org"
   gem "github-pages", group: :jekyll_plugins
   ```

3. **Install dependencies**:
   ```bash
   bundle install
   ```

4. **Run local server**:
   ```bash
   bundle exec jekyll serve
   ```

5. **Visit** `http://localhost:4000` in your browser

---

## Customization Options

### Change Color Scheme

Edit `assets/css/style.scss` to customize colors:

```scss
/* Change primary accent color */
.main-content h1,
.main-content h2,
.main-content a {
  color: #ff6b6b;  /* Change from blue to red */
}

/* Change background */
body {
  background-color: #1a1a1a;  /* Darker background */
}
```

### Change Header Gradient

Edit the `.page-header` section in `style.scss`:

```scss
.page-header {
  background-image: linear-gradient(120deg, #8b0000, #ff4500, #ffa500);
  /* Fire/lava theme colors */
}
```

### Add Custom Fonts

In `_layouts/default.html`, add font imports in the `<head>`:

```html
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&display=swap" rel="stylesheet">
```

Then use in `style.scss`:

```scss
.project-name {
  font-family: 'Cinzel', serif;
}
```

---

## Troubleshooting

### Changes Not Showing Up?
- Wait 2-5 minutes for GitHub Pages to rebuild
- Hard refresh your browser (Ctrl+F5 or Cmd+Shift+R)
- Check GitHub Actions tab for build errors

### Banner Not Displaying?
- Verify image path in `_config.yml` is correct
- Ensure image file exists in `assets/images/`
- Check image isn't too large (keep under 1MB for performance)

### Favicon Not Showing?
- Favicons can be cached aggressively by browsers
- Clear browser cache or try incognito/private mode
- Verify the path in `_config.yml` matches the actual filename

---

## Quick Commands

```bash
# Add existing SpellForce icon as favicon
copy "OriginalGameFiles\SpellForce_Addon.ico" "assets\images\favicon.ico"

# Commit all changes
git add .
git commit -m "Customize site appearance with dark theme, banner, and favicon"
git push

# Check build status
# Visit: https://github.com/YOUR_USERNAME/SpellSmut/actions
```

---

## Resources

- **Jekyll Documentation**: https://jekyllrb.com/docs/
- **GitHub Pages Docs**: https://docs.github.com/en/pages
- **Cayman Theme**: https://github.com/pages-themes/cayman
- **Favicon Generator**: https://favicon.io/
- **Image Optimization**: https://tinypng.com/

---

**Your site is now set up with a dark theme and ready for custom branding!** 🎨
