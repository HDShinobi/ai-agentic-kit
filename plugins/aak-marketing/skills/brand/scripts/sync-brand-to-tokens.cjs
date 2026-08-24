#!/usr/bin/env node
/**
 * sync-brand-to-tokens.cjs
 *
 * Syncs brand-guidelines.md colors → design-tokens.json → design-tokens.css
 *
 * Usage:
 *   node sync-brand-to-tokens.cjs
 *   node sync-brand-to-tokens.cjs --dry-run
 */

const fs = require('fs');
const path = require('path');

// Paths
const BRAND_GUIDELINES = 'docs/brand-guidelines.md';
const DESIGN_TOKENS_JSON = 'assets/design-tokens.json';
const DESIGN_TOKENS_CSS = 'assets/design-tokens.css';

/**
 * Extract color info from brand guidelines markdown
 */
function extractColorsFromMarkdown(content) {
  const colors = {
    primary: { name: 'primary', shades: {} },
    secondary: { name: 'secondary', shades: {} },
    accent: { name: 'accent', shades: {} }
  };

  // Extract color name and hex from Quick Reference table.
  // The "(Name)" suffix is OPTIONAL — the shipped starter template writes "| Primary Color | #hex |"
  // with no name, so fall back to the role name and never leave `base` undefined.
  const quickRefMatch = content.match(/Primary Color\s*\|\s*#([A-Fa-f0-9]{6})(?:\s*\(([^)]+)\))?/);
  if (quickRefMatch) {
    colors.primary.name = (quickRefMatch[2] || 'primary').toLowerCase().replace(/\s+/g, '-');
    colors.primary.base = `#${quickRefMatch[1]}`;
  }

  const secondaryMatch = content.match(/Secondary Color\s*\|\s*#([A-Fa-f0-9]{6})(?:\s*\(([^)]+)\))?/);
  if (secondaryMatch) {
    colors.secondary.name = (secondaryMatch[2] || 'secondary').toLowerCase().replace(/\s+/g, '-');
    colors.secondary.base = `#${secondaryMatch[1]}`;
  }

  const accentMatch = content.match(/Accent Color\s*\|\s*#([A-Fa-f0-9]{6})(?:\s*\(([^)]+)\))?/);
  if (accentMatch) {
    colors.accent.name = (accentMatch[2] || 'accent').toLowerCase().replace(/\s+/g, '-');
    colors.accent.base = `#${accentMatch[1]}`;
  }

  // Extract all shades from Primary Colors table
  const primarySection = content.match(/### Primary Colors[\s\S]*?\|[\s\S]*?(?=###|$)/i);
  if (primarySection) {
    const hexMatches = primarySection[0].matchAll(/\*\*([^*]+)\*\*\s*\|\s*#([A-Fa-f0-9]{6})/g);
    for (const match of hexMatches) {
      const name = match[1].trim().toLowerCase();
      const hex = `#${match[2]}`;
      if (name.includes('dark')) colors.primary.dark = hex;
      else if (name.includes('light')) colors.primary.light = hex;
      else colors.primary.base = hex;
    }
  }

  // Extract secondary shades
  const secondarySection = content.match(/### Secondary Colors[\s\S]*?\|[\s\S]*?(?=###|$)/i);
  if (secondarySection) {
    const hexMatches = secondarySection[0].matchAll(/\*\*([^*]+)\*\*\s*\|\s*#([A-Fa-f0-9]{6})/g);
    for (const match of hexMatches) {
      const name = match[1].trim().toLowerCase();
      const hex = `#${match[2]}`;
      if (name.includes('dark')) colors.secondary.dark = hex;
      else if (name.includes('light')) colors.secondary.light = hex;
      else colors.secondary.base = hex;
    }
  }

  // Extract accent shades
  const accentSection = content.match(/### Accent Colors[\s\S]*?\|[\s\S]*?(?=###|$)/i);
  if (accentSection) {
    const hexMatches = accentSection[0].matchAll(/\*\*([^*]+)\*\*\s*\|\s*#([A-Fa-f0-9]{6})/g);
    for (const match of hexMatches) {
      const name = match[1].trim().toLowerCase();
      const hex = `#${match[2]}`;
      if (name.includes('dark')) colors.accent.dark = hex;
      else if (name.includes('light')) colors.accent.light = hex;
      else colors.accent.base = hex;
    }
  }

  return colors;
}

/**
 * Generate color scale from base color (simple approach)
 */
function generateColorScale(baseHex, darkHex, lightHex) {
  // Use provided shades or generate approximations
  return {
    "50": { "$value": lightHex || adjustBrightness(baseHex, 0.9), "$type": "color" },
    "100": { "$value": lightHex || adjustBrightness(baseHex, 0.8), "$type": "color" },
    "200": { "$value": adjustBrightness(baseHex, 0.6), "$type": "color" },
    "300": { "$value": adjustBrightness(baseHex, 0.4), "$type": "color" },
    "400": { "$value": adjustBrightness(baseHex, 0.2), "$type": "color" },
    "500": { "$value": baseHex, "$type": "color" },
    "600": { "$value": darkHex || adjustBrightness(baseHex, -0.15), "$type": "color" },
    "700": { "$value": adjustBrightness(baseHex, -0.3), "$type": "color" },
    "800": { "$value": adjustBrightness(baseHex, -0.45), "$type": "color" },
    "900": { "$value": adjustBrightness(baseHex, -0.6), "$type": "color" }
  };
}

/**
 * Adjust hex color brightness
 */
function adjustBrightness(hex, percent) {
  const num = parseInt(hex.replace('#', ''), 16);
  const r = Math.min(255, Math.max(0, (num >> 16) + Math.round(255 * percent)));
  const g = Math.min(255, Math.max(0, ((num >> 8) & 0x00FF) + Math.round(255 * percent)));
  const b = Math.min(255, Math.max(0, (num & 0x0000FF) + Math.round(255 * percent)));
  return `#${((r << 16) | (g << 8) | b).toString(16).padStart(6, '0').toUpperCase()}`;
}

/**
 * Update design tokens JSON
 */
function updateDesignTokens(tokens, colors) {
  // Update brand name
  const brandName = `ClaudeKit Marketing - ${colors.primary.name.split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}`;
  tokens.brand = brandName;

  // Update primitive colors with new names (initialize the tree when starting from no tokens file)
  tokens.primitive = tokens.primitive || {};
  const primitiveColors = tokens.primitive.color || {};

  // Remove old color keys, add new ones
  delete primitiveColors.coral;
  delete primitiveColors.purple;
  delete primitiveColors.mint;

  // Add new named colors
  // Only generate scales for roles that were actually found (accent is optional in the
  // starter template). Skipping a role with no base keeps the script from crashing.
  for (const role of ['primary', 'secondary', 'accent']) {
    const c = colors[role];
    if (c && c.base) primitiveColors[c.name] = generateColorScale(c.base, c.dark, c.light);
  }

  tokens.primitive.color = primitiveColors;

  // Update ALL semantic color references
  if (tokens.semantic?.color) {
    const sem = tokens.semantic.color;
    const p = colors.primary.name;
    const s = colors.secondary.name;
    const a = colors.accent.name;

    // Primary variants
    sem.primary = { "$value": `{primitive.color.${p}.500}`, "$type": "color" };
    sem['primary-hover'] = { "$value": `{primitive.color.${p}.600}`, "$type": "color" };
    sem['primary-active'] = { "$value": `{primitive.color.${p}.700}`, "$type": "color" };
    sem['primary-light'] = { "$value": `{primitive.color.${p}.400}`, "$type": "color" };
    sem['primary-lighter'] = { "$value": `{primitive.color.${p}.100}`, "$type": "color" };
    sem['primary-dark'] = { "$value": `{primitive.color.${p}.600}`, "$type": "color" };

    // Secondary variants
    sem.secondary = { "$value": `{primitive.color.${s}.500}`, "$type": "color" };
    sem['secondary-hover'] = { "$value": `{primitive.color.${s}.600}`, "$type": "color" };
    sem['secondary-light'] = { "$value": `{primitive.color.${s}.300}`, "$type": "color" };
    sem['secondary-dark'] = { "$value": `{primitive.color.${s}.600}`, "$type": "color" };

    // Accent variants
    sem.accent = { "$value": `{primitive.color.${a}.500}`, "$type": "color" };
    sem['accent-hover'] = { "$value": `{primitive.color.${a}.600}`, "$type": "color" };
    sem['accent-light'] = { "$value": `{primitive.color.${a}.300}`, "$type": "color" };

    // Status colors (use accent for success, primary for error/info)
    sem.success = { "$value": `{primitive.color.${a}.500}`, "$type": "color" };
    sem['success-light'] = { "$value": `{primitive.color.${a}.300}`, "$type": "color" };
    sem.error = { "$value": `{primitive.color.${p}.500}`, "$type": "color" };
    sem['error-light'] = { "$value": `{primitive.color.${p}.300}`, "$type": "color" };
    sem.info = { "$value": `{primitive.color.${s}.500}`, "$type": "color" };
    sem['info-light'] = { "$value": `{primitive.color.${s}.300}`, "$type": "color" };
  }

  // Update component references (button uses primary color with opacity)
  if (tokens.component?.button?.secondary) {
    const primaryBase = colors.primary.base;
    tokens.component.button.secondary['bg-hover'] = {
      "$value": `${primaryBase}1A`,
      "$type": "color"
    };
  }

  return tokens;
}

/**
 * Main
 */
function main() {
  const dryRun = process.argv.includes('--dry-run');

  console.log('🔄 Syncing brand guidelines → design tokens\n');

  // Read brand guidelines
  const guidelinesPath = path.resolve(process.cwd(), BRAND_GUIDELINES);
  if (!fs.existsSync(guidelinesPath)) {
    console.error(`❌ Brand guidelines not found: ${guidelinesPath}`);
    process.exit(1);
  }
  const guidelinesContent = fs.readFileSync(guidelinesPath, 'utf-8');

  // Extract colors
  const colors = extractColorsFromMarkdown(guidelinesContent);
  console.log('📊 Extracted colors:');
  console.log(`   Primary: ${colors.primary.name} (${colors.primary.base})`);
  console.log(`   Secondary: ${colors.secondary.name} (${colors.secondary.base})`);
  console.log(`   Accent: ${colors.accent.name} (${colors.accent.base})\n`);

  // Read existing tokens
  const tokensPath = path.resolve(process.cwd(), DESIGN_TOKENS_JSON);
  let tokens = {};
  if (fs.existsSync(tokensPath)) {
    tokens = JSON.parse(fs.readFileSync(tokensPath, 'utf-8'));
  }

  // Update tokens
  tokens = updateDesignTokens(tokens, colors);

  if (dryRun) {
    console.log('📋 Would update design-tokens.json:');
    console.log(JSON.stringify(tokens.primitive.color, null, 2).slice(0, 500) + '...');
    console.log('\n⏭️  Dry run - no files changed');
    return;
  }

  // Write updated tokens (create the assets/ dir when it doesn't exist yet)
  fs.mkdirSync(path.dirname(tokensPath), { recursive: true });
  fs.writeFileSync(tokensPath, JSON.stringify(tokens, null, 2));
  console.log(`✅ Updated: ${DESIGN_TOKENS_JSON}`);

  // Regenerate CSS custom properties from the token tree (self-contained — no external
  // design-system skill required). Flattens every leaf value under design-tokens.json into
  // `--dot.path` CSS variables on :root.
  try {
    const cssPath = path.resolve(process.cwd(), DESIGN_TOKENS_CSS);
    fs.mkdirSync(path.dirname(cssPath), { recursive: true });
    fs.writeFileSync(cssPath, tokensToCss(tokens));
    console.log(`✅ Regenerated: ${DESIGN_TOKENS_CSS}`);
  } catch (e) {
    console.error('⚠️  Failed to regenerate CSS:', e.message);
  }

  console.log('\n✨ Brand sync complete!');
}

// Flatten a nested token object into CSS custom properties.
// { primitive: { color: { primary: { base: "#123" } } } } -> "--primitive-color-primary-base: #123;"
function tokensToCss(tokens) {
  const lines = [];
  const walk = (obj, prefix) => {
    for (const [k, v] of Object.entries(obj || {})) {
      const name = prefix ? `${prefix}-${k}` : k;
      if (v && typeof v === 'object') walk(v, name);
      else if (v !== undefined && v !== null) lines.push(`  --${name}: ${v};`);
    }
  };
  walk(tokens, '');
  return `/* Generated from ${DESIGN_TOKENS_JSON} by sync-brand-to-tokens.cjs. Do not edit by hand. */\n:root {\n${lines.join('\n')}\n}\n`;
}

main();
