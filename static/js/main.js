document.addEventListener('DOMContentLoaded', () => {
    'use strict';

    // Получаем все элементы языка
    const languageOptions = document.querySelectorAll('.language-option');
    const languageForm = document.getElementById('language-form');
    const languageInput = document.getElementById('language-input');
    const nextInput = document.getElementById('next-input');

    const slugDictElement = document.getElementById('language-slug-dict');

    let languageSlugDict = null;
    if (slugDictElement) {
        // Элемент найден, выполняем действия
        const languageSlugData = slugDictElement.textContent;
        languageSlugDict = JSON.parse(languageSlugData);
    }
    console.log('languageSlugDict - ', languageSlugDict);


    // Для каждого элемента языка добавляем обработчик клика
    languageOptions.forEach(function(option) {
        option.addEventListener('click', function(event) {
            event.preventDefault();
            let langCode = option.getAttribute('data-language');
            languageInput.value = langCode;

            if (languageSlugDict) {
                nextInput.value = '/extensions/' + languageSlugDict[langCode]  + '/';
            }

            languageForm.submit();

        });
    });


    // Получаем все формы с классом needs-validation
    const forms = document.querySelectorAll('.needs-validation');

    // Перебираем формы и блокируем их отправку, если они невалидны
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }

            // Добавляем класс was-validated, чтобы активировать стили ошибок
            form.classList.add('was-validated');

            // Инициализируем тултипы для всех элементов с классом 'invalid-tooltip'
            const tooltips = document.querySelectorAll('.invalid-tooltip');
            tooltips.forEach(tooltip => {
                new bootstrap.Tooltip(tooltip, { placement: 'right' });
            });
        }, false);
    });
});
