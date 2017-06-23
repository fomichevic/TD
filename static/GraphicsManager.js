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
 *  const pos = sprite.position; // Положение спрайта
 *  const x = pos.x; // Координата по оси X
 *  const y = pos.y; // Координата по оси Y
 *  const size = sprite.size; // Размер спрайта
 *  const szx = size.x; // Размер по оси X
 *  const szy = size.y; // Размер по оси Y
 *
 *  const pointBuffer = sprite.pointBuffer; // Буфер вершин. Пересчитывается при получении
 *  const textureBuffer = sprite.textureBuffer; // Буфер текстурных вершин. Считается при создании спрайта

 *  gm.dropSprite('static', 'my-sprite'); // Удаление спрайта по типу и ID
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
            constructor(type, descriptor, position = {x: 0, y: 0}, size = {x: 0, y: 0}) {
                this.type = type;
                this.descriptor = descriptor;

                this._position = position;
                this._size = size;

                this._pointBuffer = gm.gl.createBuffer();
                this._updatePointBuffer();

                this._textureBuffer = gm.gl.createBuffer();

                gm.gl.bindBuffer(gm.gl.ARRAY_BUFFER, this._textureBuffer);
                gm.gl.bufferData(gm.gl.ARRAY_BUFFER, new Float32Array([
                    this.descriptor.desc.left,  this.descriptor.desc.bottom,
                    this.descriptor.desc.left,  this.descriptor.desc.top,
                    this.descriptor.desc.right, this.descriptor.desc.top,

                    this.descriptor.desc.left,  this.descriptor.desc.bottom,
                    this.descriptor.desc.right, this.descriptor.desc.bottom,
                    this.descriptor.desc.right, this.descriptor.desc.top,
                ]), gm.gl.STATIC_DRAW);
            }

            get position() {
                return {
                    x: this._position.x,
                    y: this._position.y
                };
            }

            get size() {
                return {
                    x: this._size.x,
                    y: this._size.y
                }
            }

            _updatePointBuffer() {
                gm.gl.bindBuffer(gm.gl.ARRAY_BUFFER, this._pointBuffer);
                gm.gl.bufferData(gm.gl.ARRAY_BUFFER, new Float32Array([
                    this.position.x,               this.position.y + this.size.y,
                    this.position.x,               this.position.y,
                    this.position.x + this.size.x, this.position.y,

                    this.position.x,               this.position.y + this.size.y,
                    this.position.x + this.size.x, this.position.y + this.size.y,
                    this.position.x + this.size.x, this.position.y,
                ]), this.type);
            }

            set position(val) {
                this.position.x = val.x;
                this.position.y = val.y;
                this._updatePointBuffer();
            }

            set size(val) {
                this.size.x = val.x;
                this.size.y = val.y;
                this._updatePointBuffer();
            }

            get pointBuffer() {
                return this._pointBuffer;
            }

            get textureBuffer() {
                return this._textureBuffer;
            }
        }

        return this[type][id] = new Sprite(
            type !== 'dynamic' ? this.gl.STATIC_DRAW : this.gl.DYNAMIC_DRAW,
            spriteDescriptor, position, size);
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

