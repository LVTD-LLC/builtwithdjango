// Explicit intent/engagement events complement SDK autocapture. Never read inputs.
export function installEngagement(win, doc) {
  if (win.bwdEngagementInstalled) return;
  win.bwdEngagementInstalled = true;
  const started = new WeakSet();
  const invalid = new WeakSet();
  let thresholds = new Set();
  const track = (name, properties) => {
    if (typeof win.bwdTrack === "function") win.bwdTrack(name, properties);
  };
  const formProperties = (form) => ({
    form_id: form.id || "",
    form_method: (form.getAttribute("method") || "get").toUpperCase()
  });
  doc.addEventListener("focusin", (event) => {
    const form = event.target.form;
    if (!form || started.has(form)) return;
    started.add(form);
    track("form started", formProperties(form));
  });
  doc.addEventListener("invalid", (event) => {
    const form = event.target.form;
    if (!form || invalid.has(form)) return;
    invalid.add(form);
    track("form validation blocked", formProperties(form));
  }, true);
  doc.addEventListener("submit", (event) => {
    if (event.target) invalid.delete(event.target);
  }, true);
  let scheduled = false;
  win.addEventListener("scroll", () => {
    if (scheduled) return;
    scheduled = true;
    win.requestAnimationFrame(() => {
      scheduled = false;
      const height = doc.documentElement.scrollHeight - win.innerHeight;
      if (height <= 0) return;
      const depth = Math.min(100, Math.round(win.scrollY / height * 100));
      [25, 50, 75, 100].forEach((threshold) => {
        if (depth >= threshold && !thresholds.has(threshold)) {
          thresholds.add(threshold);
          track("page scroll depth reached", { scroll_depth: threshold });
        }
      });
    });
  }, { passive: true });
  doc.addEventListener("turbo:load", () => { thresholds = new Set(); });
}

if (typeof window !== "undefined") installEngagement(window, document);
