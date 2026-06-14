const toggle = document.getElementById('theme-toggle');
toggle.addEventListener('click', () => {
    // toggle the 'dark' class on document.documentElement
    document.documentElement.classList.toggle('dark');
    // then save 'dark' or 'light' to localStorage.theme based on whether the class is now present
    localStorage.theme = document.documentElement.classList.contains('dark') ? 'dark' : 'light';
    }
);