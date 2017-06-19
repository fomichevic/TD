(function () { // Для того, чтобы код не был вызван
    const rm = new ResourceManager('load-list.json', // Путь до списка закачки
        () => { // callback, который будет вызван, когда все скачается
            const gm = GraphicsManager.get(); // GraphicsManager -- синглтон

            const sprite = gm.createSprite( // Создаем спрайт
                'static', // Тип спрайта. 'static', 'dynamic' или 'background'
                'units', // Идентификатор текстуры, например
                'knight' // Идентификатор дескриптора, например
            );

            // Задаем размер спрайта
            sprite.size.x = 100;
            sprite.size.y = 100;

            // Задаем положение спрайта
            sprite.position.x = 150;
            sprite.position.y = 150;

            // Список спрайтов
            const spriteList = gm.getSpriteList(
                'dynamic', // Тип спрайтов, опять же, 'static', 'dynamic' или 'background'
                true // Оптимизировать ли список по очередности текстур. По умолчанию false. Можно не указывать
            );

            for (let s of spriteList) { // Пройдем по спрайтам из списка
                const texture = rm.textures[s.texture]; // Полная текстура, к которой принадлежит спрайт, вместе с дескрипторами
                const image = texture.img; // Картинка текстуры, объект Image
                const descriptor = texture.desc[s.descriptor]; // Дескриптор текстуры
                const {left, top, right, bottom} = descriptor; // Текстурные координаты прямоугольника
            }

        });
});