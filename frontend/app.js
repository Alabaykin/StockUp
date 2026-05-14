document.addEventListener("DOMContentLoaded", () => {
    // Инициализация Telegram Web App
    const tg = window.Telegram.WebApp;
    
    // Сообщаем телеграму, что приложение готово
    tg.ready();
    tg.expand(); // Открываем на весь экран

    const greeting = document.getElementById("greeting");
    
    if (tg.initDataUnsafe && tg.initDataUnsafe.user) {
        greeting.textContent = `Привет, ${tg.initDataUnsafe.user.first_name}!`;
    }

    const addBtn = document.getElementById("addBtn");
    addBtn.addEventListener("click", () => {
        // Заглушка: в будущем здесь будет открытие формы добавления продукта
        tg.showAlert("Здесь будет форма добавления продукта!");
    });
});
