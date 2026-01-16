const toggle = document.getElementById("theme-toggle");

if (localStorage.getItem("theme") === "dark") {
    document.body.classList.add("dark");
    toggle.innerText = "☀️ Modo claro";
}

toggle.addEventListener("click", () => {
    document.body.classList.toggle("dark");

    const isDark = document.body.classList.contains("dark");
    toggle.innerText = isDark ? "☀️ Modo claro" : "🌙 Modo escuro";

    localStorage.setItem("theme", isDark ? "dark" : "light");
});
