// 1. EXECUÇÃO IMEDIATA (Evita o "piscar" branco)
const currentTheme = localStorage.getItem("theme");
if (currentTheme === "dark") {
    document.body.classList.add("dark-theme");
}

// 2. CONFIGURAÇÃO DO BOTÃO (Após o carregamento da página)
document.addEventListener('DOMContentLoaded', () => {
    const btn = document.getElementById("theme-toggle");
    const themeIcon = document.getElementById("theme-icon");

    // Ajusta o ícone inicial com base no tema carregado
    if (document.body.classList.contains("dark-theme")) {
        if (themeIcon) themeIcon.innerText = "☀️";
    }

    if (btn) {
        btn.onclick = () => {
            document.body.classList.toggle("dark-theme");
            
            let theme = "light";
            if (document.body.classList.contains("dark-theme")) {
                theme = "dark";
                if (themeIcon) themeIcon.innerText = "☀️";
            } else {
                if (themeIcon) themeIcon.innerText = "🌙";
            }
            
            localStorage.setItem("theme", theme);
        };
    }
});
