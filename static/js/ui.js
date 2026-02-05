// =========================================
// UI.JS – MICROINTERAÇÕES AUTONO+
// =========================================

document.addEventListener("DOMContentLoaded", () => {

  // -------------------------------
  // 1. Ativar animações ao carregar
  // -------------------------------
  document.querySelectorAll(".animate-fade, .animate-slide, .animate-page")
    .forEach(el => {
      el.style.opacity = "1";
    });

  // -------------------------------
  // 2. Shake em ações bloqueadas (Free)
  // -------------------------------
  document.querySelectorAll(".locked-box, .disabled").forEach(el => {
    el.addEventListener("click", () => {
      el.classList.add("shake");
      setTimeout(() => el.classList.remove("shake"), 400);
    });
  });

  // -------------------------------
  // 3. Feedback ao clicar em botões
  // -------------------------------
  document.querySelectorAll("button, .btn, .btn-nav, .btn-sm").forEach(btn => {
    btn.addEventListener("click", () => {
      btn.classList.add("clicked");
      setTimeout(() => btn.classList.remove("clicked"), 150);
    });
  });

  // -------------------------------
  // 4. Scroll reveal simples
  // -------------------------------
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = "1";
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll(".animate-fade, .animate-slide")
    .forEach(el => observer.observe(el));

});
