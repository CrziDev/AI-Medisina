
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-bs-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-bs-theme', newTheme);

    localStorage.setItem('theme', newTheme);
}

function handleSwitchStateChange() {
    const switchState = this.checked;
    localStorage.setItem('switchState', switchState);
}

document.getElementById('btnSwitch').addEventListener('click', toggleTheme);

document.getElementById('btnSwitch').addEventListener('change', handleSwitchStateChange);

const savedTheme = localStorage.getItem('theme');
if (savedTheme) {
    document.documentElement.setAttribute('data-bs-theme', savedTheme);
} else {
    document.documentElement.setAttribute('data-bs-theme', 'light'); // Set 'light' as default
    localStorage.setItem('theme', 'light'); // Store default theme in localStorage
}

const savedSwitchState = localStorage.getItem('switchState');
if (savedSwitchState) {
    document.getElementById('btnSwitch').checked = savedSwitchState === 'true'; // Convert the string to a boolean
}
