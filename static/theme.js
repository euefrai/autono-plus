document.addEventListener('DOMContentLoaded', () => {
    const btn = document.getElementById("theme-toggle");
    const themeIcon = document.getElementById("theme-icon");
    
    // 1. Ao carregar, verifica o que está salvo no navegador
    const currentTheme = localStorage.getItem("theme");

    if (currentTheme === "dark") {
        document.body.classList.add("dark-theme");
        if (themeIcon) themeIcon.innerText = "☀️";
    }

    // 2. Lógica do Clique
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
            
            // 3. Salva a escolha para não perder ao mudar de página
            localStorage.setItem("theme", theme);
        };
    }
});
