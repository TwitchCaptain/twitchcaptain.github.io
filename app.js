const listEl = document.getElementById("project-list");

function stripLeadingEmoji(text) {
  return text.replace(/^[\p{Extended_Pictographic}\uFE0F\u200D\s]+/u, "").trim();
}

function formatDate(iso) {
  if (!iso) return null;
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return null;
  return date.toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function projectItem(project, index) {
  const li = document.createElement("li");
  li.className = "project";
  li.style.animationDelay = `${Math.min(index, 8) * 45}ms`;

  const top = document.createElement("div");
  top.className = "project-top";

  const title = document.createElement("h2");
  title.className = "project-name";
  const titleLink = document.createElement("a");
  titleLink.href = project.url;
  titleLink.textContent = project.name;
  title.appendChild(titleLink);

  const meta = document.createElement("div");
  meta.className = "project-meta";
  if (project.language) {
    const lang = document.createElement("span");
    lang.className = "chip";
    lang.textContent = project.language;
    meta.appendChild(lang);
  }
  const updated = formatDate(project.pushed_at);
  if (updated) {
    const when = document.createElement("span");
    when.textContent = `updated ${updated}`;
    meta.appendChild(when);
  }

  top.append(title, meta);

  const desc = document.createElement("p");
  desc.className = "project-desc";
  desc.textContent =
    stripLeadingEmoji(project.description || "") || "No description provided.";

  const actions = document.createElement("div");
  actions.className = "project-actions";

  const repoLink = document.createElement("a");
  repoLink.href = project.url;
  repoLink.textContent = "Repository";
  actions.appendChild(repoLink);

  if (project.pages_url) {
    const pagesLink = document.createElement("a");
    pagesLink.className = "pages-link";
    pagesLink.href = project.pages_url;
    pagesLink.textContent = "Open site";
    actions.appendChild(pagesLink);
  }

  li.append(top, desc, actions);
  return li;
}

async function loadProjects() {
  try {
    const response = await fetch(`projects.json?t=${Date.now()}`, {
      cache: "no-cache",
    });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    const projects = await response.json();
    listEl.replaceChildren();

    if (!Array.isArray(projects) || projects.length === 0) {
      const empty = document.createElement("li");
      empty.className = "project-error";
      empty.textContent = "No public projects found yet.";
      listEl.appendChild(empty);
      return;
    }

    for (const [index, project] of projects.entries()) {
      listEl.appendChild(projectItem(project, index));
    }
  } catch (error) {
    console.error(error);
    listEl.replaceChildren();
    const fail = document.createElement("li");
    fail.className = "project-error";
    fail.textContent = "Could not load the project list.";
    listEl.appendChild(fail);
  }
}

loadProjects();
