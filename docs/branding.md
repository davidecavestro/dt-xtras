# DT Taxonomy Branding

## 🎯 Logo Design Concept

The DT Taxonomy logo is inspired by the original DependencyTrack logo but reimagined to represent the interconnected nature of taxonomy relationships.

### Design Philosophy

- **3 Main Squares**: Represent the three primary aspects of taxonomy (categories, relations, and projections)
- **Central Connector**: Fills the gap between squares, symbolizing the connections and relationships that bind taxonomies together
- **Green Color Scheme**: Complementary to DependencyTrack's typical color palette, representing growth and organization
- **Rounded Corners**: Modern, approachable design that's less technical than the original DT logo

## 🎨 Logo Components

### Main Structure
- **Top-left square**: Primary taxonomy category
- **Top-right square**: Secondary taxonomy category  
- **Bottom square**: Taxonomy projection/result
- **Central square**: Relationship connections
- **Accent squares**: Subtle details representing individual tags

### Color Variants

#### Default (Green)
- **Primary**: `#10B981` (Green-500)
- **Secondary**: `#34D399` (Green-400)
- **Accent**: `#6EE7B7` (Green-300)

#### Light Variant
- **Primary**: `#10B981` (Green-500)
- **Secondary**: `#34D399` (Green-400)
- **Accent**: `#6EE7B7` (Green-300)
- **Background**: `#F0FDF4` (Green-50)

#### Dark Variant
- **Primary**: `#059669` (Green-600)
- **Secondary**: `#10B981` (Green-500)
- **Accent**: `#34D399` (Green-400)
- **Background**: `#064E3B` (Green-900)

#### Monochrome Variant
- **Primary**: `#6B7280` (Gray-500)
- **Secondary**: `#9CA3AF` (Gray-400)
- **Accent**: `#D1D5DB` (Gray-300)

## 📦 Logo Components

### DTLogo.vue
Full-size logo (100x100 viewBox) suitable for:
- Landing pages
- About sections
- Marketing materials

**Usage:**
```vue
<DTLogo size="60" variant="default" />
<DTLogo size="80" variant="light" className="custom-class" />
```

### DTLogoCompact.vue
Compact logo (48x48 viewBox) suitable for:
- Navigation headers
- Button icons
- Small UI elements

**Usage:**
```vue
<DTLogoCompact size="24" variant="dark" />
<DTLogoCompact size="32" variant="monochrome" />
```

### DTLogoWithText.vue
Logo with text combination suitable for:
- Application headers
- Brand headers
- Navigation branding

**Usage:**
```vue
<DTLogoWithText size="medium" variant="default" />
<DTLogoWithText size="large" variant="light" showText />
```

## 🎯 Design Inspiration

The logo design draws inspiration from:

1. **DependencyTrack Original**: The 3-square layout and geometric precision
2. **Video Game UI**: Rounded, connected elements that feel interactive
3. **Network Graphs**: The interconnected nature of taxonomy relationships
4. **Modern SaaS**: Clean, approachable design with personality

## 🔄 Animation & Interaction

All logo components include subtle hover and active states:
- **Hover**: Scale up slightly (1.05-1.1x depending on component)
- **Active**: Scale down slightly (0.95x) for tactile feedback
- **Transitions**: Smooth 0.2s ease-in-out animations

## 📐 Technical Specifications

### SVG Structure
- **ViewBox**: 100x100 (full), 48x48 (compact)
- **Coordinate System**: Centered at 50,50
- **Border Radius**: 6px (large), 3px (compact)
- **Stroke**: None (filled shapes only)

### Responsive Scaling
- Components scale proportionally while maintaining aspect ratio
- Border radius scales with size
- Text spacing adjusts based on logo size

## 🎨 Usage Guidelines

### Do's
- ✅ Use on light and dark backgrounds
- ✅ Scale proportionally
- ✅ Maintain adequate whitespace
- ✅ Use appropriate variant for context

### Don'ts
- ❌ Stretch or distort aspect ratio
- ❌ Modify colors (use variants instead)
- ❌ Add drop shadows or effects
- ❌ Place on busy backgrounds without contrast

## 🔧 Implementation Notes

The logo components are built with Vue 3 Composition API and include:
- **Type-safe props** with validation
- **Computed properties** for dynamic styling
- **CSS transitions** for smooth interactions
- **Responsive design** principles

Components are self-contained and can be used throughout the application without additional dependencies.
