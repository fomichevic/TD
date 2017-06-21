/**
 * Пример использования:
 *
 *  // rm -- объект ResourceManager для взятия описяния спрайта
 *
 *  const sprite = new Sprite(
 *      rm.sprites['units:knight'], // То, что вы хотите хранить как поле descriptor. В данном случае -- описание спрайта
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
 *  const descriptor = sprite.descriptor; // То, что передано первым аргументом
 *  const position = sprite.position; // Положение центра спрайта
 *  const cx = position.x; // Координата по оси X
 *  const cy = position.y; // Координата по оси Y
 *  const size = sprite.size; // Размер спрайта
 *  const szx = size.x; // Размер по оси X
 *  const szy = size.y; // Размер по оси Y
 *
 *  const vertexCoords = sprite.vertexCoords; // Координаты вершин прямоугольника. Объект Float32Array
 *  const textureCoords = sprite.textureCoords; // Текстурные координаты. Объект Float32Array
 */
class Sprite {
    constructor(descriptor, position = {x: 0, y: 0}, size = {x: 0, y: 0}) {
        this.descriptor = descriptor;
        this.position = position;
        this.size = size;
    }

    get vertexCoords() {
        return new Float32Array([
            this.position.x - this.size.x / 2.0, this.position.y - this.size.y / 2.0,
            this.position.x - this.size.x / 2.0, this.position.y + this.size.y / 2.0,
            this.position.x + this.size.x / 2.0, this.position.y + this.size.y / 2.0,

            this.position.x - this.size.x / 2.0, this.position.y - this.size.y / 2.0,
            this.position.x + this.size.x / 2.0, this.position.y - this.size.y / 2.0,
            this.position.x + this.size.x / 2.0, this.position.y + this.size.y / 2.0,
        ]);
    }

    get textureCoords() {
        return new Float32Array([
            this.descriptor.left, this.descriptor.bottom,
            this.descriptor.left, this.descriptor.top,
            this.descriptor.right, this.descriptor.top,

            this.descriptor.left, this.descriptor.bottom,
            this.descriptor.right, this.descriptor.bottom,
            this.descriptor.right, this.descriptor.top,
        ]);
    }
}
