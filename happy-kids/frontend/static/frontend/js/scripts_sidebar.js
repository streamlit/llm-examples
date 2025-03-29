function toggleMenu() {
    const sidebar = document.querySelector('.sidebar');
    sidebar.classList.toggle('expanded');

    const menuLinks = document.querySelectorAll('.sidebar ul li a');

    if (sidebar.classList.contains('expanded')) {
        menuLinks.forEach(link => {
            link.classList.remove('collapsed');
        });
    } else {
        menuLinks.forEach(link => {
            link.classList.add('collapsed');
        });
    }
}
