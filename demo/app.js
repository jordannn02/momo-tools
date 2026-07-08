const levels = [
  { name: "verified-working", count: 1, caption: "repeatable evidence", value: "100%" },
  { name: "visible", count: 7, caption: "registered only", value: "72%" },
  { name: "executed", count: 0, caption: "awaiting bounded proof", value: "0%" },
];

const gates = [
  { name: "write", description: "Edit, save, send, delete, archive, or persist actions stay gated." },
  { name: "private-data", description: "Account, customer, inbox, or internal content requires bounded scope." },
  { name: "external-network", description: "Current web facts and connector calls remain explicit." },
  { name: "credential", description: "Secrets never belong in the capability index." },
  { name: "local-app", description: "Browser and app state are inspected only inside requested scope." },
  { name: "persist", description: "Memory capture waits until the user-safe delivery boundary." },
];

const evidence = [
  {
    title: "Capability Gate Console",
    category: "frontend",
    status: "fixture",
    image: "assets/evidence/capability-gate-console.png",
    description: "Dashboard concept used to test frontend-app-builder routing and write-gate evidence.",
  },
  {
    title: "Mobile Gate Console",
    category: "mobile",
    status: "responsive",
    image: "assets/evidence/capability-gate-mobile.png",
    description: "Mobile fixture proving the same gate console can collapse into a narrow viewport.",
  },
  {
    title: "Frontend QA After State",
    category: "frontend",
    status: "validated",
    image: "assets/evidence/frontend-qa-after.png",
    description: "Synthetic reimbursement screen after visual debugging and interaction proof.",
  },
  {
    title: "Frontend QA Mobile",
    category: "mobile",
    status: "responsive",
    image: "assets/evidence/frontend-qa-mobile.png",
    description: "Mobile screenshot from the same frontend testing/debugging capability fixture.",
  },
  {
    title: "Image To Code Desktop",
    category: "frontend",
    status: "fixture",
    image: "assets/evidence/image-to-code-desktop.png",
    description: "Image-to-code output used to prove that visual references can become reviewable UI.",
  },
  {
    title: "Momo Pipeline Preview",
    category: "workflow",
    status: "fixture",
    image: "assets/evidence/momo-pipeline-preview.png",
    description: "Preview surface for the slide/deck pipeline route, kept synthetic and local.",
  },
  {
    title: "Web Data Visualization",
    category: "workflow",
    status: "validated",
    image: "assets/evidence/web-data-viz-desktop.png",
    description: "Static chart fixture showing data visualization output without production data.",
  },
  {
    title: "Web Data Visualization Mobile",
    category: "mobile",
    status: "responsive",
    image: "assets/evidence/web-data-viz-mobile.png",
    description: "Mobile chart proof that direct-label visuals remain readable without hover states.",
  },
  {
    title: "Browser Control Screenshot",
    category: "workflow",
    status: "fixture",
    image: "assets/evidence/browser-control.png",
    description: "Local browser-control proof screenshot from a synthetic fixture page.",
  },
  {
    title: "Document Fixture",
    category: "document",
    status: "fixture",
    image: "assets/evidence/document-fixture.png",
    description: "Document reading fixture proving the route can preserve page-level evidence.",
  },
  {
    title: "Spreadsheet Preview",
    category: "document",
    status: "fixture",
    image: "assets/evidence/spreadsheet-preview.png",
    description: "Small spreadsheet preview used as bounded local-file evidence.",
  },
  {
    title: "Presentation Contact Sheet",
    category: "document",
    status: "fixture",
    image: "assets/evidence/presentation-contact-sheet.png",
    description: "Slide contact sheet proving presentation workflows can emit compact visual review artifacts.",
  },
];

const benchmarks = [
  ["pdf_summary_read_only", "document", "document-reader", "local-file, write"],
  ["docx_table_extract", "document", "document-reader", "local-file, write"],
  ["official_latest_release", "current info", "browser-research", "external-network"],
  ["offline_latest_conflict", "conflict", "browser-research", "external-network"],
  ["repo_release_blockers", "code review", "repo-review", "local-file"],
  ["security_audit", "code review", "repo-review", "local-file"],
  ["email_draft_guarded", "private comms", "email-triage", "private-data, external-network, write"],
  ["remember_allowed", "memory capture", "memory-capture", "write, private-data"],
  ["remember_blocked_by_no_save", "conflict", "document-reader", "local-file, write"],
  ["frontend_visual_qa", "frontend", "frontend-qa", "local-app, write"],
  ["csv_dashboard", "data", "data-analysis", "local-file, write"],
  ["capability_dashboard", "router", "momo-tools", "none"],
];

const levelList = document.querySelector("#levelList");
const gateMatrix = document.querySelector("#gateMatrix");
const galleryGrid = document.querySelector("#galleryGrid");
const benchmarkRows = document.querySelector("#benchmarkRows");
const filters = document.querySelectorAll("[data-filter]");
const previewDialog = document.querySelector("#previewDialog");
const previewImage = document.querySelector("#previewImage");
const previewTitle = document.querySelector("#previewTitle");
const previewDescription = document.querySelector("#previewDescription");

function renderLevels() {
  levelList.innerHTML = levels
    .map(
      (level) => `
        <div class="level-row">
          <div class="level-label">
            <strong>${level.name}</strong>
            <span>${level.caption}</span>
          </div>
          <div class="level-track" aria-hidden="true">
            <span class="level-fill" style="--value:${level.value}"></span>
          </div>
          <span class="level-count">${level.count}</span>
        </div>
      `,
    )
    .join("");
}

function renderGates() {
  gateMatrix.innerHTML = gates
    .map(
      (gate) => `
        <div class="gate-card">
          <strong>${gate.name}</strong>
          <span>${gate.description}</span>
        </div>
      `,
    )
    .join("");
}

function evidenceCard(item) {
  const mobile = item.category === "mobile" ? " is-mobile" : "";
  return `
    <article class="evidence-card${mobile}" data-category="${item.category}">
      <img class="evidence-media" src="${item.image}" alt="${item.title}" data-preview="${item.title}">
      <div class="evidence-body">
        <div class="meta-row">
          <span class="tag">${item.category}</span>
          <span class="tag warn">${item.status}</span>
        </div>
        <h3>${item.title}</h3>
        <p>${item.description}</p>
      </div>
    </article>
  `;
}

function renderGallery(filter = "all") {
  const items = filter === "all" ? evidence : evidence.filter((item) => item.category === filter);
  galleryGrid.innerHTML = items.map(evidenceCard).join("");
}

function renderBenchmarks() {
  benchmarkRows.innerHTML = benchmarks
    .map(
      ([id, promptClass, route, gate]) => `
        <tr>
          <td><strong>${id}</strong></td>
          <td>${promptClass}</td>
          <td>${route}</td>
          <td>${gate}</td>
          <td><span class="status-pass">passed</span></td>
        </tr>
      `,
    )
    .join("");
}

function openPreview(item) {
  previewImage.src = item.image;
  previewImage.alt = item.title;
  previewTitle.textContent = item.title;
  previewDescription.textContent = item.description;
  previewDialog.showModal();
}

filters.forEach((button) => {
  button.addEventListener("click", () => {
    filters.forEach((filter) => filter.classList.remove("is-active"));
    button.classList.add("is-active");
    renderGallery(button.dataset.filter);
  });
});

galleryGrid.addEventListener("click", (event) => {
  const image = event.target.closest("[data-preview]");
  if (!image) return;
  const item = evidence.find((entry) => entry.title === image.dataset.preview);
  if (item) openPreview(item);
});

document.querySelector("[data-close-preview]").addEventListener("click", () => {
  previewDialog.close();
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && previewDialog.open) {
    previewDialog.close();
  }
});

renderLevels();
renderGates();
renderGallery();
renderBenchmarks();
