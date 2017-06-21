/**
 * Пример использования:
 *
 *  // Необходимо подключить Sprite.js
 *  // rm -- объект ResourceManager для взятия описания спрайта
 *
 *  const gm = new GraphicsManager();
 *  const sprite = gm.createSprite(
 *      'static', // Тип спрайта, 'static', 'dynamic' или 'background'
 *      'my-sprite', // Идентификатор спрайта
 *
 *      // Далее 3 аргумента конструктора спрайта
 *      rm.sprites['units:knight'],
 *      {
 *          x: 150,
 *          y: 150
 *      },
 *      {
 *          x: 100,
 *          y: 100
 *      }
 *  );
 *
 *  const sprite2 = gm.getSprite('static', 'my-sprite'); // sprite === sprite2
 *
 *  const sprite3 = gm.registerSprite('dynamic', 'another-sprite', // Другой способ регистрации спрайта
 *      new Sprite( // см. Sprite.js
 *          rm.sprites['units:swordsman'],
 *          {
 *              x: 250,
 *              y: 250
 *          },
 *          {
 *              x: 200,
 *              y: 200
 *          }
 *      )
 *  );
 *
 *  gm.dropSprite('static', 'my-sprite'); // Удаление спрайта по типу и ID
 *  gm.dropSprite('dynamic', 'another-sprite');
 *
 *  // Много кода с добавлением и удалением спрайтов
 *
 *  const spriteList = gm.getSpriteList('dynamic'); // Список спрайтов
 *  const spriteIdList = gm.getIdList('dynamic'); // Список идентификаторов, например, для удаления спрайтов
 *
 * Документация по спрайтам перенесена к соответствующему классу
 */
class GraphicsManager {
    constructor() {
        this.static = {};
        this.dynamic = {};
        this.background = {};
    }

    createSprite(type, id, spriteDescriptor, position, size) {
        return this[type][id] = new Sprite(spriteDescriptor, position, size);
    }

    registerSprite(type, id, sprite) {
        return this[type][id] = sprite;
    }

    dropSprite(type, id) {
        delete this[type][id];
    }

    getSprite(type, id) {
        return this[type][id];
    }

    getIdList(type) {
        const list = [];
        for (const id in this[type]) {
            list.push(id);
        }
        return list;
    }

    getSpriteList(type) {
        const list = [];
        for (const id in this[type]) {
            list.push(this[type][id]);
        }
        return list;
    }
}

