const btn = document.getElementById("theme-toggle");
const themeIcon = document.getElementById("theme-icon");
const currentTheme = localStorage.getItem("theme");

// Verifica se o usuário já tinha uma preferência salva
if (currentTheme === "dark") {
    document.body.classList.add("dark-theme");
    themeIcon.innerText = "☀️";
}

btn.onclick = () => {
    document.body.classList.toggle("dark-theme");
    
    let theme = "light";
    if (document.body.classList.contains("dark-theme")) {
        theme = "dark";
        themeIcon.innerText = "☀️";
    } else {
        themeIcon.innerText = "🌙";
    }
    
    // Salva a escolha para a próxima página
    localStorage.setItem("theme", theme);
};
