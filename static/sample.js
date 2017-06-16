const rm = ResourceManager.get(); // Можно каждый раз использовать ResourceManager.get(), rm -- сокращение
rm.onload = () => { // Передача асинхронная, нужен обработчик
    const gm = {}; // Графического менеджера пока в этой ветке нет
    const type = 'static'; // Тип графического объекта. 'static', 'dynamic' или 'background'
    const id = 'id'; // Идентификатор объекта

    const sprite = gm[type][id]; // Спрайт

    const texture = sprite.texture; // Супертекстура, используемая спрайтом
    const descriptor = sprite.descriptor; // Дескриптор, используемый спрайтом

    const img = rm.textures[texture].img; // Само изображение
    const desc = rm.textures[texture].desc[descriptor]; // Дескриптор
    const left   = desc.left;   // Левая граница изображения
    const top    = desc.top;    // Верхняя граница изображения
    const right  = desc.right;  // Правая граница изображения
    const bottom = desc.bottom; // Нижняя граница изображения

    const x = sprite.x; // Координата по оси X
    const y = sprite.y; // Координата по оси Y
    const w = sprite.w; // Размер по оси X
    const h = sprite.h; // Размер по оси Y
};
rm.load('list'); // Ссылка на список с сервера
