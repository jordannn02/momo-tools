import { mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const OUT = new URL("./assets/evidence/", import.meta.url);

function esc(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function wrap(text, max = 38) {
  const words = text.split(/\s+/);
  const lines = [];
  let line = "";
  for (const word of words) {
    const next = line ? `${line} ${word}` : word;
    if (next.length > max && line) {
      lines.push(line);
      line = word;
    } else {
      line = next;
    }
  }
  if (line) lines.push(line);
  return lines;
}

function textBlock(lines, x, y, options = {}) {
  const {
    size = 18,
    weight = 600,
    fill = "#14201c",
    lineHeight = Math.round(size * 1.34),
    anchor = "start",
    family = "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
  } = options;
  return `<text x="${x}" y="${y}" font-family="${family}" font-size="${size}" font-weight="${weight}" fill="${fill}" text-anchor="${anchor}">${lines
    .map((line, index) => `<tspan x="${x}" dy="${index ? lineHeight : 0}">${esc(line)}</tspan>`)
    .join("")}</text>`;
}

function card(x, y, w, h, options = {}) {
  const { fill = "#ffffff", stroke = "#d9e1dd", radius = 8, width = 1 } = options;
  return `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${radius}" fill="${fill}" stroke="${stroke}" stroke-width="${width}"/>`;
}

function badge(x, y, label, options = {}) {
  const { fill = "#dff3ef", color = "#075e56", width = Math.max(74, label.length * 8 + 22) } = options;
  return `${card(x, y, width, 28, { fill, stroke: "transparent", radius: 14 })}
  ${textBlock([label], x + width / 2, y + 19, { size: 12, weight: 800, fill: color, anchor: "middle" })}`;
}

function bar(x, y, w, value, color = "#0f766e") {
  return `${card(x, y, w, 14, { fill: "#e8f0ed", stroke: "transparent", radius: 7 })}
  ${card(x, y, Math.round(w * value), 14, { fill: color, stroke: "transparent", radius: 7 })}`;
}

function svg({ title, subtitle, body, width = 1200, height = 760, accent = "#0f766e", dark = false }) {
  const bg = dark ? "#0d1513" : "#f7f8f6";
  const surface = dark ? "#15201d" : "#ffffff";
  const ink = dark ? "#f5faf7" : "#111816";
  const muted = dark ? "#b6c6c0" : "#63706b";
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}">
  <rect width="${width}" height="${height}" fill="${bg}"/>
  <style>
    text { font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
  </style>
  ${card(36, 36, width - 72, height - 72, { fill: surface, stroke: dark ? "#2c3a35" : "#d9e1dd" })}
  ${textBlock(["SYNTHETIC EVIDENCE FIXTURE"], 72, 92, { size: 13, weight: 850, fill: accent })}
  ${textBlock(wrap(title, 26), 72, 158, { size: 48, weight: 850, fill: ink, lineHeight: 56 })}
  ${textBlock(wrap(subtitle, 68), 72, title.length > 28 ? 290 : 230, { size: 19, weight: 500, fill: muted, lineHeight: 30 })}
  ${body({ width, height, accent, surface, ink, muted })}
  </svg>`;
}

function capabilityGate() {
  return svg({
    title: "Review promotion readiness without touching production.",
    subtitle: "Capability gates stay visible while the router selects the smallest useful tool path.",
    height: 820,
    body: ({ accent, ink, muted }) => `
      ${card(72, 380, 260, 118, { fill: "#0d1513", stroke: "#0d1513" })}
      ${textBlock(["Verified"], 96, 420, { size: 17, weight: 800, fill: "#ffffff" })}
      ${textBlock(["18"], 96, 468, { size: 42, weight: 850, fill: "#ffffff" })}
      ${textBlock(["verified-working"], 96, 494, { size: 14, weight: 700, fill: "#c9d4d0" })}
      ${card(356, 380, 260, 118, { fill: "#f7f8f6" })}
      ${textBlock(["Visible"], 380, 420, { size: 17, weight: 800, fill: ink })}
      ${textBlock(["25"], 380, 468, { size: 42, weight: 850, fill: ink })}
      ${textBlock(["needs gated evidence"], 380, 494, { size: 14, weight: 700, fill: muted })}
      ${card(640, 380, 260, 118, { fill: "#fff1c9" })}
      ${textBlock(["Queue"], 664, 420, { size: 17, weight: 800, fill: ink })}
      ${textBlock(["5"], 664, 468, { size: 42, weight: 850, fill: ink })}
      ${textBlock(["write fixture left"], 664, 494, { size: 14, weight: 700, fill: muted })}
      ${card(72, 560, 970, 72, { fill: "#ffffff" })}
      ${textBlock(["frontend-app-builder"], 96, 606, { size: 20, weight: 800, fill: ink })}
      ${textBlock(["write fixture"], 620, 606, { size: 17, weight: 700, fill: muted })}
      ${badge(862, 581, "needs evidence", { fill: "#fff1c9", color: "#7a4b00", width: 128 })}
      ${card(72, 650, 970, 72, { fill: "#ffffff" })}
      ${textBlock(["codex-crew"], 96, 696, { size: 20, weight: 800, fill: ink })}
      ${textBlock(["verified-working"], 620, 696, { size: 17, weight: 700, fill: muted })}
      ${badge(862, 671, "safe to promote", { width: 132 })}
      ${bar(930, 148, 160, 0.72, accent)}
      ${textBlock(["Strict gates"], 930, 184, { size: 16, weight: 800, fill: accent })}
    `,
  });
}

function mobileGate() {
  return svg({
    title: "Gate review on a narrow screen.",
    subtitle: "The same proof model must remain readable in mobile review contexts.",
    width: 420,
    height: 900,
    body: ({ accent, ink, muted }) => `
      ${card(48, 330, 324, 96, { fill: "#0d1513", stroke: "#0d1513" })}
      ${textBlock(["Verified"], 72, 366, { size: 15, weight: 800, fill: "#ffffff" })}
      ${textBlock(["18"], 72, 406, { size: 34, weight: 850, fill: "#ffffff" })}
      ${card(48, 446, 324, 96, { fill: "#ffffff" })}
      ${textBlock(["Visible"], 72, 482, { size: 15, weight: 800, fill: ink })}
      ${textBlock(["25"], 72, 522, { size: 34, weight: 850, fill: ink })}
      ${card(48, 562, 324, 74, { fill: "#ffffff" })}
      ${textBlock(["frontend-app-builder"], 72, 606, { size: 17, weight: 800, fill: ink })}
      ${badge(232, 584, "gated", { fill: "#fff1c9", color: "#7a4b00", width: 82 })}
      ${card(48, 656, 324, 74, { fill: "#ffffff" })}
      ${textBlock(["codex-crew"], 72, 700, { size: 17, weight: 800, fill: ink })}
      ${badge(232, 678, "safe", { width: 82 })}
      ${textBlock(["No hidden promotion."], 48, 792, { size: 20, weight: 850, fill: ink })}
      ${textBlock(wrap("Evidence remains visible before any capability becomes trusted.", 32), 48, 826, { size: 14, weight: 500, fill: muted, lineHeight: 22 })}
    `,
  });
}

function frontendQa() {
  return svg({
    title: "Approve reimbursements without losing the audit trail.",
    subtitle: "Rendered frontend QA verifies layout, interaction proof, and console health.",
    body: ({ accent, ink, muted }) => `
      ${card(72, 350, 270, 96, { fill: "#ffffff" })}
      ${textBlock(["18"], 96, 398, { size: 38, weight: 850, fill: ink })}
      ${textBlock(["items queued"], 96, 424, { size: 16, weight: 600, fill: muted })}
      ${card(370, 350, 270, 96, { fill: "#ffffff" })}
      ${textBlock(["4"], 394, 398, { size: 38, weight: 850, fill: ink })}
      ${textBlock(["need receipts"], 394, 424, { size: 16, weight: 600, fill: muted })}
      ${card(668, 350, 270, 96, { fill: "#ffffff" })}
      ${textBlock(["2"], 692, 398, { size: 38, weight: 850, fill: ink })}
      ${textBlock(["policy flags"], 692, 424, { size: 16, weight: 600, fill: muted })}
      ${card(72, 500, 940, 178, { fill: "#ffffff" })}
      ${textBlock(["Review queue"], 96, 548, { size: 24, weight: 850, fill: ink })}
      ${textBlock(["Owner", "Mae Lin", "Arun Patel"], 100, 594, { size: 16, weight: 750, fill: ink, lineHeight: 36 })}
      ${textBlock(["Vendor", "Northline Studio", "Packet Rail"], 340, 594, { size: 16, weight: 750, fill: ink, lineHeight: 36 })}
      ${textBlock(["Amount", "$482.17", "$118.40"], 650, 594, { size: 16, weight: 750, fill: ink, lineHeight: 36 })}
      ${textBlock(["Status", "Receipt missing", "Ready"], 810, 594, { size: 16, weight: 750, fill: ink, lineHeight: 36 })}
      ${badge(900, 108, "reviewed", { width: 100 })}
      ${bar(900, 148, 160, 0.9, accent)}
    `,
  });
}

function frontendQaMobile() {
  return svg({
    title: "Review queue fits mobile.",
    subtitle: "Responsive QA keeps the action and audit trail visible.",
    width: 420,
    height: 900,
    body: ({ accent, ink, muted }) => `
      ${card(48, 330, 324, 96, { fill: "#ffffff" })}
      ${textBlock(["18"], 72, 378, { size: 34, weight: 850, fill: ink })}
      ${textBlock(["items queued"], 72, 406, { size: 15, weight: 650, fill: muted })}
      ${card(48, 446, 324, 96, { fill: "#ffffff" })}
      ${textBlock(["4"], 72, 494, { size: 34, weight: 850, fill: ink })}
      ${textBlock(["need receipts"], 72, 522, { size: 15, weight: 650, fill: muted })}
      ${card(48, 582, 324, 168, { fill: "#ffffff" })}
      ${textBlock(["Review queue"], 72, 628, { size: 22, weight: 850, fill: ink })}
      ${textBlock(["Mae Lin", "Northline Studio", "$482.17", "Receipt missing"], 72, 672, { size: 16, weight: 700, fill: ink, lineHeight: 26 })}
      ${badge(232, 626, "reviewed", { width: 100 })}
      ${textBlock(["Action proof and console health stay testable on small screens."], 48, 812, { size: 15, weight: 650, fill: muted })}
      ${bar(48, 846, 324, 0.82, accent)}
    `,
  });
}

function imageToCode() {
  return svg({
    title: "Design references become inspectable UI.",
    subtitle: "Image-to-code output is useful only when text, spacing, and hierarchy become native code.",
    body: ({ accent, ink, muted }) => `
      ${card(690, 170, 330, 360, { fill: "#dff3ef", stroke: "#0f766e" })}
      ${card(725, 205, 260, 160, { fill: "#174238", stroke: "transparent" })}
      <circle cx="855" cy="285" r="72" fill="#95d5b2"/>
      <ellipse cx="855" cy="280" rx="94" ry="52" transform="rotate(-24 855 280)" fill="#f5c962"/>
      ${card(725, 390, 120, 96, { fill: "#ffffff" })}
      ${textBlock(["Evidence", "82%"], 752, 430, { size: 17, weight: 800, fill: ink, lineHeight: 36 })}
      ${card(866, 390, 120, 96, { fill: "#0d1513", stroke: "#0d1513" })}
      ${textBlock(["Noise", "-31"], 892, 430, { size: 17, weight: 800, fill: "#ffffff", lineHeight: 36 })}
      ${badge(72, 350, "source image", { width: 126 })}
      ${badge(222, 350, "native code", { fill: "#e4ecfb", color: "#173f82", width: 122 })}
      ${textBlock(["1. Preserve hierarchy", "2. Replace fake text", "3. Validate browser render"], 72, 430, { size: 22, weight: 800, fill: ink, lineHeight: 44 })}
      ${textBlock(["The proof is not the screenshot. The proof is a rendered UI that can be inspected, resized, and tested."], 72, 610, { size: 17, weight: 600, fill: muted })}
    `,
  });
}

function pipeline() {
  return svg({
    title: "Risk stays visible while routing gets smarter.",
    subtitle: "A preview surface for the MoMo pipeline route, rebuilt with native text.",
    height: 980,
    body: ({ accent, ink, muted }) => `
      ${card(72, 330, 220, 120, { fill: "#ffffff" })}
      ${card(318, 330, 220, 120, { fill: "#0d1513", stroke: "#0d1513" })}
      ${card(564, 330, 220, 120, { fill: "#ffffff" })}
      ${card(810, 330, 220, 120, { fill: "#fff1c9" })}
      ${textBlock(["Indexed", "43"], 96, 374, { size: 18, weight: 800, fill: ink, lineHeight: 42 })}
      ${textBlock(["Verified-working", "16"], 342, 374, { size: 18, weight: 800, fill: "#ffffff", lineHeight: 42 })}
      ${textBlock(["Visible", "27"], 588, 374, { size: 18, weight: 800, fill: ink, lineHeight: 42 })}
      ${textBlock(["Regression", "8/8 + 7/7"], 834, 374, { size: 18, weight: 800, fill: ink, lineHeight: 42 })}
      ${card(72, 540, 958, 238, { fill: "#ffffff" })}
      ${textBlock(["Promotion requires evidence, not installed-tool optimism."], 104, 604, { size: 34, weight: 850, fill: ink })}
      ${textBlock(["Configured", "Known path exists."], 104, 682, { size: 18, weight: 800, fill: ink, lineHeight: 30 })}
      ${textBlock(["Visible", "Discoverable index."], 330, 682, { size: 18, weight: 800, fill: ink, lineHeight: 30 })}
      ${textBlock(["Executed", "Bounded output."], 556, 682, { size: 18, weight: 800, fill: ink, lineHeight: 30 })}
      ${textBlock(["Verified", "Repeatable proof."], 782, 682, { size: 18, weight: 800, fill: ink, lineHeight: 30 })}
      ${bar(104, 728, 760, 0.78, accent)}
      ${badge(892, 572, "no overclaiming", { width: 132 })}
    `,
  });
}

function dataViz() {
  return svg({
    title: "Invoices dominate the sample queue.",
    subtitle: "Direct labels and static chart output prove data visualization without production data.",
    body: ({ accent, ink, muted }) => {
      const rows = [
        ["Invoices", 34, 0.96],
        ["Expenses", 18, 0.62],
        ["Vendors", 11, 0.42],
        ["Access", 8, 0.31],
      ];
      return `
        ${rows
          .map(([label, count, value], index) => {
            const y = 360 + index * 70;
            return `${textBlock([label], 72, y + 18, { size: 18, weight: 700, fill: ink })}
            ${bar(240, y, 540, value, accent)}
            ${textBlock([count], 808, y + 18, { size: 18, weight: 850, fill: ink })}`;
          })
          .join("")}
        ${card(850, 330, 250, 250, { fill: "#ffffff" })}
        ${textBlock(["Reading path"], 880, 380, { size: 22, weight: 850, fill: ink })}
        ${textBlock(wrap("Rank queue load, keep source caveats visible, and avoid hover-only meaning.", 26), 880, 430, { size: 16, weight: 600, fill: muted, lineHeight: 24 })}
      `;
    },
  });
}

function browserFixture() {
  return svg({
    title: "Browser control stays bounded.",
    subtitle: "Synthetic browser fixture proves UI control without inspecting unrelated profile state.",
    body: ({ accent, ink, muted }) => `
      ${card(84, 340, 980, 300, { fill: "#ffffff" })}
      ${card(84, 340, 980, 46, { fill: "#e4ecfb" })}
      ${textBlock(["MoMo Browser Fixture"], 112, 370, { size: 18, weight: 850, fill: ink })}
      ${textBlock(["Input"], 120, 450, { size: 17, weight: 800, fill: ink })}
      ${card(220, 424, 360, 48, { fill: "#f7f8f6" })}
      ${textBlock(["synthetic-browser-fixture"], 244, 454, { size: 17, weight: 650, fill: muted })}
      ${card(120, 510, 220, 52, { fill: accent, stroke: "transparent" })}
      ${textBlock(["Apply Action"], 230, 543, { size: 17, weight: 850, fill: "#ffffff", anchor: "middle" })}
      ${textBlock(["Result: synthetic-browser-fixture"], 120, 606, { size: 18, weight: 800, fill: ink })}
      ${textBlock(["No cookies, profile data, or external browser state are represented here."], 650, 454, { size: 17, weight: 600, fill: muted })}
    `,
  });
}

function documentFixture() {
  return svg({
    title: "Document pages become bounded evidence.",
    subtitle: "A document route should preserve source page context before summarizing.",
    height: 860,
    body: ({ accent, ink, muted }) => `
      ${card(92, 330, 760, 420, { fill: "#ffffff" })}
      ${textBlock(["MoMo Tools Document Fixture"], 132, 390, { size: 30, weight: 850, fill: ink })}
      ${textBlock(["Verified Summary"], 132, 462, { size: 20, weight: 850, fill: accent })}
      ${textBlock(wrap("This synthetic page demonstrates document capability output with exact anchors and a visible caveat boundary.", 68), 132, 498, { size: 17, weight: 600, fill: muted, lineHeight: 26 })}
      ${textBlock(["Evidence Matrix"], 132, 590, { size: 20, weight: 850, fill: ink })}
      ${card(132, 622, 620, 56, { fill: "#f0f4f2" })}
      ${textBlock(["Anchor", "Source", "Status"], 160, 656, { size: 16, weight: 850, fill: ink, lineHeight: 0 })}
      ${textBlock(["document-id", "local fixture page", "pass"], 160, 708, { size: 16, weight: 650, fill: ink, lineHeight: 0 })}
      ${badge(890, 360, "local file", { width: 100 })}
    `,
  });
}

function spreadsheetFixture() {
  return svg({
    title: "Spreadsheet previews keep table shape.",
    subtitle: "Small spreadsheet artifacts should remain readable before analysis claims are made.",
    width: 900,
    height: 520,
    body: ({ accent, ink, muted }) => `
      ${card(88, 260, 720, 180, { fill: "#ffffff" })}
      ${card(88, 260, 720, 44, { fill: "#e4ecfb" })}
      ${textBlock(["A", "1", "2", "3"], 130, 292, { size: 18, weight: 850, fill: ink, lineHeight: 42 })}
      ${textBlock(["Metric", "Total Revenue", "Total Cost", "Gross Margin"], 210, 292, { size: 18, weight: 750, fill: ink, lineHeight: 42 })}
      ${textBlock(["Preview only"], 600, 292, { size: 18, weight: 750, fill: muted, lineHeight: 42 })}
      ${badge(88, 204, "bounded table", { width: 126 })}
    `,
  });
}

function presentationFixture() {
  return svg({
    title: "Slide contact sheets show review scope.",
    subtitle: "Presentation routes can expose compact visual evidence before export.",
    width: 1200,
    height: 520,
    body: ({ accent, ink, muted }) => `
      ${[0, 1, 2, 3].map((i) => {
        const x = 86 + i * 262;
        return `${card(x, 260, 220, 138, { fill: "#ffffff" })}
        ${textBlock([`Slide ${i + 1}`], x + 22, 304, { size: 18, weight: 850, fill: ink })}
        ${bar(x + 22, 334, 160, 0.35 + i * 0.12, accent)}
        ${textBlock(["isolated", "repeatable"], x + 22, 374, { size: 14, weight: 650, fill: muted, lineHeight: 22 })}`;
      }).join("")}
      ${badge(86, 210, "contact sheet", { width: 130 })}
    `,
  });
}

function mobileDataViz() {
  return svg({
    title: "Mobile chart keeps labels visible.",
    subtitle: "No hover-only meaning; direct labels stay readable in narrow width.",
    width: 420,
    height: 900,
    body: ({ accent, ink }) => `
      ${[["Invoices", 34, 0.94], ["Expenses", 18, 0.58], ["Vendors", 11, 0.38], ["Access", 8, 0.28]]
        .map(([label, count, value], index) => {
          const y = 360 + index * 86;
          return `${textBlock([label], 48, y, { size: 18, weight: 750, fill: ink })}
          ${bar(48, y + 24, 280, value, accent)}
          ${textBlock([count], 344, y + 38, { size: 18, weight: 850, fill: ink })}`;
        })
        .join("")}
      ${textBlock(["Source: synthetic fixture data."], 48, 760, { size: 15, weight: 650, fill: "#63706b" })}
    `,
  });
}

const assets = {
  "capability-gate-console.svg": capabilityGate(),
  "capability-gate-mobile.svg": mobileGate(),
  "frontend-qa-after.svg": frontendQa(),
  "frontend-qa-mobile.svg": frontendQaMobile(),
  "image-to-code-desktop.svg": imageToCode(),
  "momo-pipeline-preview.svg": pipeline(),
  "web-data-viz-desktop.svg": dataViz(),
  "web-data-viz-mobile.svg": mobileDataViz(),
  "browser-control.svg": browserFixture(),
  "document-fixture.svg": documentFixture(),
  "spreadsheet-preview.svg": spreadsheetFixture(),
  "presentation-contact-sheet.svg": presentationFixture(),
};

mkdirSync(OUT, { recursive: true });
for (const [name, content] of Object.entries(assets)) {
  writeFileSync(join(OUT.pathname, name), `${content}\n`, "utf8");
}
