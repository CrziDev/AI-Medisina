
document.addEventListener('DOMContentLoaded', function () {
    setTimeout(function () {
        document.body.classList.add('show');
    }, 200);
    if (window.innerWidth >= 867 || window.innerWidth >= 1090) {

        if (localStorage.getItem('isClosed') === 'true') {
            closeNav();
        } else {
            openNav();
        }
    } else {
        closeNav();
    }


});
function getUrlParameter(name) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(name);
}


const currentPage = getUrlParameter('page');

const sidebarItems = document.querySelectorAll('.sidebar-item');

sidebarItems.forEach(item => {
    const itemPage = item.getAttribute('href').split('page=')[1];
    if (itemPage === currentPage) {
        item.classList.add('selected');
    }
});

function handleScroll() {
    var navbar = document.getElementById("nav");
    var sidebar = document.getElementById("mySidebar");

    if (window.scrollY > 0) {
        navbar.classList.add("border-bottom");

    } else {

        navbar.classList.remove("border-bottom");
    }
}


window.addEventListener("scroll", handleScroll);



function openNav() {
    localStorage.setItem('isClosed', false);
    var opnbtn = document.getElementById("opnbtn");

    var sidebar = document.getElementById("mySidebar");
    var main = document.getElementById("main");
    var sidebarlogo = document.getElementById("sidebarlogo");



    if (window.innerWidth >= 1090) {
        opnbtn.style.display = "none"
        sidebar.style.width = "300px";
        sidebar.style.marginLeft = "0px";
        main.style.marginLeft = "300px";
    




        sidebar.style.zIndex = "1";
    } else if (window.innerWidth >= 867) {
        sidebar.style.width = "250px";
        sidebar.style.marginLeft = "0px";
        opnbtn.style.display = "none"
        main.style.marginLeft = "250px";
    





        sidebar.style.zIndex = "1";
    } else {
        sidebar.style.marginLeft = "0px";
        sidebar.style.width = "300px";
        opnbtn.style.display = "block"

        sidebar.style.marginTop = "0px";
        main.style.marginLeft = "0";
        

        sidebar.style.zIndex = "4000";
    }

}
largeScreen = false;

function closeNav() {
    localStorage.setItem('isClosed', true);
    var opnbtn = document.getElementById("opnbtn");
    var sidebar = document.getElementById("mySidebar");
    var main = document.getElementById("main");


    sidebar.style.marginLeft = "-300px";
    main.style.marginLeft = "0";

    opnbtn.style.display = "block"

}

function toggleNav() {

    var sidebar = document.getElementById("mySidebar");
    if (window.innerWidth >= 867) {


        if (sidebar.style.marginLeft === "-300px") {
            if (window.innerWidth >= 867) {
                largeScreen = false;
            }
            openNav();

        } else {

            closeNav();
            if (window.innerWidth >= 867) {
                largeScreen = true;
            }
        }
    } else {
        if (sidebar.style.marginLeft === "0px") {
            closeNav();
            if (window.innerWidth >= 867) {
                largeScreen = true;
            }
        } else {

            if (window.innerWidth >= 867) {
                largeScreen = false;
            }
            openNav();

        }
    }
}








// Automatically open the sidebar on larger devices (width >= 768px)

window.addEventListener('resize', function () {
    if (window.innerWidth >= 867) {
        if (!largeScreen) {
            openNav();
        }


    } else if (window.innerWidth >= 1090) {
        if (!largeScreen) {
            openNav();
        }


    } else {

        closeNav();


    }
});
