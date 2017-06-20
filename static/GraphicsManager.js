/**
 * Пример использования:
 *
 *  // rm -- объект ResourceManager. Нужен для взятия описания спрайта
 *
 *  const gm = new GraphicsManager();
 *  const sprite = gm.createSprite(
 *      'static', // Тип спрайта, 'static', 'dynamic' или 'background'
 *      'my-sprite', // Идентификатор спрайта
 *      rm.sprites['units:knight'], // Любой аргумент, который вы хотите хранить под именем spriteDescriptor. В данном случае -- описание спрайта
 *      { // Положение спрайта. По умолчанию -- ( 0 ; 0 )
 *          x: 150,
 *          y: 150
 *      },
 *      { // Размер спрайта. По умолчанию -- ( 0 ; 0 )
 *          x: 100,
 *          y: 100
 *      }
 *  );
 *
 *  const sprite2 = gm.getSprite('static', 'my-sprite'); // sprite === sprite2
 *
 *  gm.dropSprite('static', 'my-sprite'); // Удаление спрайта по типу и ID
 *
 *  // Много кода с добавлением и удалением спрайтов
 *
 *  for (const s of gm.getSpriteList('dynamic')) { // Если нужны только сами спрайты
 *      const spriteDescriptor = s.spriteDescriptor; // Аргумент, который был передан 3-м параметром
 *
 *      const position = s.position; // Положение
 *      const x = position.x; // Координата по оси X
 *      const y = position.y; // Координата по оси Y
 *      const size = s.size; // Размер
 *      const szx = size.x; // Размер по оси X
 *      const szy = size.y; // Размер по оси Y
 *
 *      // Любые поля спрайта можно менять:
 *      s.position.x = 0; // Положение по оси X
 *      s.position.y = 0; // Положение по оси Y
 *      s.position = {x: 0, y: 0}; // Положение как вектор
 *
 *      s.size.x = 100; // Размер по оси X
 *      s.size.y = 100; // Размер по оси Y
 *      s.size = {x: 100, y: 100}; // Размер как вектор
 *  }
 *
 *  for (const id of gm.getIdList('dynamic')) { // Если нужны идентификаторы спрайтов
 *      gm.dropSprite('dynamic', id); // Например, при их удалении
 *  }
 */
class GraphicsManager {
    constructor() {
        this.static = {};
        this.dynamic = {};
        this.background = {};
    }

    createSprite(type, id, spriteDescriptor, position = {x: 0, y: 0}, size = {x: 0, y: 0}) {
        return this[type][id] = {
            spriteDescriptor: spriteDescriptor,
            position: {
                x: position.x,
                y: position.y
            },
            size: {
                x: size.x,
                y: size.y
            }
        };
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

