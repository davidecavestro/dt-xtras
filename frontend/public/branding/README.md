# DT Taxonomy Branding Assets

This directory contains all branding assets for the DT Taxonomy application.

## 📁 Files Overview

### Logo Files
- **`dt-xtras-logo.svg`** - Full-size logo (100x100) with light background
- **`dt-xtras-logo-compact.svg`** - Compact logo (48x48) for UI elements
- **`dt-xtras-logo-dark.svg`** - Dark theme variant (100x100)
- **`favicon.svg`** - Browser favicon (32x32)

### Design Specifications

#### Color Palette
- **Primary Green**: `#10B981` (Green-500)
- **Secondary Green**: `#34D399` (Green-400)
- **Accent Green**: `#6EE7B7` (Green-300)
- **Dark Background**: `#064E3B` (Green-900)
- **Light Background**: `#F0FDF4` (Green-50)

#### Design Concept
The logo is inspired by the DependencyTrack logo but reimagined for taxonomy:
- **3 Main Squares**: Represent taxonomy categories, relations, and projections
- **Central Connector**: Symbolizes relationships that bind taxonomies together
- **Green Color Scheme**: Complementary to DT, representing growth and organization
- **Rounded Corners**: Modern, approachable design

## 🎯 Usage Guidelines

### Web Applications
```html
<!-- Full logo -->
<img src="/branding/dt-xtras-logo.svg" alt="DT Taxonomy" width="100" height="100">

<!-- Compact logo -->
<img src="/branding/dt-xtras-logo-compact.svg" alt="DT Taxonomy" width="48" height="48">

<!-- Dark theme -->
<img src="/branding/dt-xtras-logo-dark.svg" alt="DT Taxonomy" width="100" height="100">
```

### Vue Components
```vue
<!-- Using the built-in components -->
<DTLogo size="60" variant="default" />
<DTLogoCompact size="24" variant="dark" />
<DTLogoWithText size="medium" variant="light" />
```

### Documents and Presentations
- Use **dt-xtras-logo.svg** for headers and covers
- Use **dt-xtras-logo-compact.svg** for inline elements
- Use **dt-xtras-logo-dark.svg** for dark backgrounds

## 📐 Technical Details

### SVG Structure
- **ViewBox**: 100x100 (full), 48x48 (compact)
- **Coordinate System**: Centered design
- **Border Radius**: 6px (large), 3px (compact)
- **Format**: Optimized SVG with minimal paths

### File Sizes
- **Full Logo**: ~2KB
- **Compact Logo**: ~1.5KB
- **Dark Variant**: ~2KB
- **Favicon**: ~1KB

### Browser Support
- ✅ Chrome 4+
- ✅ Firefox 3.0+
- ✅ Safari 3.1+
- ✅ Edge 12+
- ✅ IE 9+

## 🎨 Variants

### Light Theme (Default)
- Background: Light green (`#F0FDF4`)
- Primary: Medium green (`#10B981`)
- Secondary: Light green (`#34D399`)

### Dark Theme
- Background: Dark green (`#064E3B`)
- Primary: Dark green (`#059669`)
- Secondary: Medium green (`#10B981`)

### Monochrome
- Gray scale variants for minimal designs
- Suitable for print and single-color applications

## 🔧 Implementation Notes

### Vue Components
The branding includes three Vue components:
1. **DTLogo.vue** - Full-size logo with variants
2. **DTLogoCompact.vue** - Compact logo for UI elements
3. **DTLogoWithText.vue** - Logo with "DT Taxonomy" text

All components support:
- Size customization
- Color variants (default, light, dark, monochrome)
- Hover animations
- Responsive scaling

### CSS Integration
```css
/* Custom CSS usage */
.logo {
  background-image: url('/branding/dt-xtras-logo-compact.svg');
  background-size: contain;
  background-repeat: no-repeat;
  width: 48px;
  height: 48px;
}
```

## 📝 License

These branding assets extend the DependencyTrack branding and follow the same licensing terms as the main project.

## 🚀 Future Enhancements

Planned branding improvements:
- [ ] Animated logo variants
- [ ] PNG fallbacks for older browsers
- [ ] Vector icon font integration
- [ ] Brand guidelines document
- [ ] Marketing materials templates
