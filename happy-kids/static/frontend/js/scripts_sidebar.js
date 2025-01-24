function toggleMenu() {
    const sidebar = document.querySelector('.sidebar');
    const menu = document.getElementById('menu');
    
    sidebar.classList.toggle('expanded');

    if (menu.style.display === "none" || menu.style.display === "") {
        menu.style.display = "block";
    } else {
        menu.style.display = "none";
    }
}