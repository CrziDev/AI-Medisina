function handleScroll() {
    var navbar = document.getElementById("nav");

    if (window.scrollY > 0) {
        navbar.classList.add("border-bottom");
        navbar.classList.add("bg-white")

    } else {
        navbar.classList.remove("bg-white")

        navbar.classList.remove("border-bottom");
    }
}


window.addEventListener("scroll", handleScroll);