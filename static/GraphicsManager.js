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
    constructor(gl) {
        this.gl = gl;
        this.static = {};
        this.dynamic = {};
        this.background = {};
    }

    createSprite(type, id, spriteDescriptor, position, size) {
        const gm = this;

        class Sprite {
            constructor(descriptor, x = 0, y = 0, w = 0, h = 0) {
                this.descriptor = descriptor;

                class Vector {
                    constructor(x, y) {
                        this._x = x;
                        this._y = y;
                    }

                    get x() {
                        return this._x;
                    }

                    get y() {
                        return this._y;
                    }

                    set x(val) {
                        this._x = val;
                        sprite.updatePointVerticeBuffer();
                    }

                    set y(val) {
                        this._y = val;
                        sprite.updatePointVerticeBuffer();
                    }
                }

                this._position = new Vector(x, y);
                this._size = new Vector(w, h);

                const sprite = this;
                this.pointBuffer = gm.gl.createBuffer();
                this.updatePointVerticeBuffer();

                this.textureBuffer = gm.gl.createBuffer();
                gm.gl.bindBuffer(gl.ARRAY_BUFFER, this.textureBuffer);
                gm.gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([
                    this.descriptor.desc.left,  this.descriptor.desc.bottom,
                    this.descriptor.desc.left,  this.descriptor.desc.top,
                    this.descriptor.desc.right, this.descriptor.desc.top,

                    this.descriptor.desc.left,  this.descriptor.desc.bottom,
                    this.descriptor.desc.right, this.descriptor.desc.bottom,
                    this.descriptor.desc.right, this.descriptor.desc.top,
                ]), gm.gl.STATIC_DRAW);
            }

            get position() {
                return this._position;
            }

            get size() {
                return this._size;
            }

            updatePointVerticeBuffer() {
                gm.gl.bindBuffer(gl.ARRAY_BUFFER, this.pointBuffer);
                gm.gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([
                    this.position.x,               this.position.y + this.size.y,
                    this.position.x,               this.position.y,
                    this.position.x + this.size.x, this.position.y,

                    this.position.x,               this.position.y + this.size.y,
                    this.position.x + this.size.x, this.position.y + this.size.y,
                    this.position.x + this.size.x, this.position.y,
                ]), gm.gl.STATIC_DRAW);
            }
        }

        return this[type][id] = new Sprite(spriteDescriptor, position, size);
    }

    dropSprite(type, id) {
        const sprite = this[type][id];
        this.gl.deleteBuffer(sprite.pointBuffer);
        this.gl.deleteBuffer(sprite.textureBuffer);
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

