(function() { // Обернем все в анонимную функцию, чтобы этот код не был выполнен, а был только примером

    const rm = ResourceManager.get(); // Можно каждый раз использовать ResourceManager.get(), rm -- сокращение
    rm.onload = () => { // Передача асинхронная, нужен обработчик события
        const gm = GraphicsManager.get(); // Графического менеджера пока в этой ветке нет, но обращение к нему будет таким
        const type = 'static'; // Тип графического объекта. 'static', 'dynamic' или 'background'
        const id = 'id'; // Идентификатор объекта

        const sprite = gm[type][id]; // Спрайт

        const texture = sprite.texture; // Супертекстура, используемая спрайтом
        const descriptor = sprite.descriptor; // Дескриптор, используемый спрайтом

        const img = rm.textures[texture].img; // Само изображение
        const desc = rm.textures[texture].desc[descriptor]; // Дескриптор
        const left = desc.left;   // Левая граница изображения
        const top = desc.top;    // Верхняя граница изображения
        const right = desc.right;  // Правая граница изображения
        const bottom = desc.bottom; // Нижняя граница изображения

        const pos = sprite.position; // Положение
        const size = sprite.size; // Размер

        const x = pos.x; // Координата по оси X
        const y = pos.y; // Координата по оси Y
        const w = size.x; // Размер по оси X
        const h = size.y; // Размер по оси Y
    };
    rm.load('list'); // Начинаем скачивание. На месте 'list' -- путь до списка на сервере

});
