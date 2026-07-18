# Shopify Liquid — Reference Patterns for Figma Implementation

## File Structure

For a new section from a Figma design:
```
sections/
  section-name.liquid     ← main template + schema
assets/
  section-name.css        ← styles
  section-name.js         ← JS if needed (optional)
```

---

## Basic Section Structure

```liquid
{{ 'section-name.css' | asset_url | stylesheet_tag }}

<div class="section-name">
  <!-- content here -->
</div>

{% schema %}
{
  "name": "Section Name",
  "settings": [
    {
      "type": "text",
      "id": "heading",
      "label": "Heading",
      "default": "Default heading"
    }
  ],
  "presets": [
    {
      "name": "Section Name"
    }
  ]
}
{% endschema %}
```

---

## Common Setting Types

```json
{ "type": "text",     "id": "heading",     "label": "Heading" }
{ "type": "textarea", "id": "description", "label": "Description" }
{ "type": "image_picker", "id": "image",   "label": "Image" }
{ "type": "url",      "id": "button_url",  "label": "Button URL" }
{ "type": "color",    "id": "bg_color",    "label": "Background colour", "default": "#ffffff" }
{ "type": "range",    "id": "padding_top", "label": "Padding top", "min": 0, "max": 100, "step": 4, "unit": "px", "default": 40 }
{ "type": "select",   "id": "text_align",  "label": "Text align",
  "options": [
    { "value": "left",   "label": "Left" },
    { "value": "center", "label": "Center" },
    { "value": "right",  "label": "Right" }
  ],
  "default": "left"
}
```

---

## Referencing Settings in Template

```liquid
<div style="background-color: {{ section.settings.bg_color }}; padding-top: {{ section.settings.padding_top }}px;">
  <h2>{{ section.settings.heading }}</h2>
  <p>{{ section.settings.description }}</p>
</div>
```

---

## Images

```liquid
{% if section.settings.image %}
  {{
    section.settings.image
    | image_url: width: 1200
    | image_tag: loading: 'lazy', alt: section.settings.image.alt
  }}
{% endif %}
```

---

## Blocks (Repeatable Items — e.g. Cards, Features)

Schema:
```json
"blocks": [
  {
    "type": "card",
    "name": "Card",
    "settings": [
      { "type": "text",         "id": "title",       "label": "Title" },
      { "type": "textarea",     "id": "description", "label": "Description" },
      { "type": "image_picker", "id": "image",       "label": "Image" }
    ]
  }
],
"max_blocks": 6
```

Template:
```liquid
<div class="cards-grid">
  {% for block in section.blocks %}
    {% case block.type %}
      {% when 'card' %}
        <div class="card" {{ block.shopify_attributes }}>
          {% if block.settings.image %}
            {{ block.settings.image | image_url: width: 600 | image_tag: loading: 'lazy' }}
          {% endif %}
          <h3>{{ block.settings.title }}</h3>
          <p>{{ block.settings.description }}</p>
        </div>
    {% endcase %}
  {% endfor %}
</div>
```

---

## Theme Settings (Global Variables)

Reference global theme settings instead of hardcoding:
```liquid
{{ settings.color_background }}
{{ settings.color_foreground }}
{{ settings.color_accent_1 }}
{{ settings.type_header_font | font_face }}
{{ settings.type_body_font | font_face }}
```

---

## CSS Companion File Patterns

Map Figma design tokens to CSS custom properties:
```css
.section-name {
  --color-bg: {{ section.settings.bg_color }};
  --padding-top: {{ section.settings.padding_top }}px;
  
  background-color: var(--color-bg);
  padding-top: var(--padding-top);
}
```

---

## Responsive Pattern

```css
.section-name__grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
}

@media (min-width: 750px) {
  .section-name__grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 990px) {
  .section-name__grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
```

---

## Common Mistakes to Avoid

- Don't use `px` values from Figma directly as hardcoded CSS — expose them as schema range settings
- Don't use hex colours directly — expose as color settings so merchants can change them
- Always add `{{ block.shopify_attributes }}` to block wrappers for theme editor highlighting
- Always add a `presets` array in schema so the section appears in the theme editor "Add section" list
- Don't use `<script>` inline — put JS in a separate asset file loaded with `{{ 'section-name.js' | asset_url | script_tag }}`
