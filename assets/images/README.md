# Images Folder

This folder contains custom images for the GitHub Pages site.

## Banner Image

To add a custom banner that appears at the top of every page:

1. **Create or find a banner image** (recommended size: 1200x300 pixels)
2. **Save it as `banner.png`** (or `banner.jpg`) in this folder
3. **Edit `_config.yml`** in the root directory and uncomment:
   ```yaml
   banner_image: /assets/images/banner.png
   ```

## Favicon

To add a custom icon that appears in browser tabs:

1. **Create or convert an icon file** 
   - Can be `.ico`, `.png`, or `.svg`
   - Recommended sizes: 16x16, 32x32, or 64x64 pixels
   - You can use one of the SpellForce .ico files from `OriginalGameFiles/`
   
2. **Save it as `favicon.ico`** (or `favicon.png`) in this folder

3. **Edit `_config.yml`** in the root directory and uncomment:
   ```yaml
   favicon: /assets/images/favicon.ico
   ```

## Using Existing SpellForce Icons

You have SpellForce icons available in `OriginalGameFiles/`:
- `SpellForce_Addon.ico` - Breath of Winter expansion icon
- `SpellForce_Addon2.ico` - Shadow of the Phoenix expansion icon

To use one as your favicon:
1. Copy the desired `.ico` file to this folder
2. Rename it to `favicon.ico` (or keep the original name)
3. Update `_config.yml` with the correct filename

## Example

```yaml
# In _config.yml
banner_image: /assets/images/banner.png
favicon: /assets/images/favicon.ico
```
