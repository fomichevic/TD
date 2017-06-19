/**
 * Пример использования:
 *  const rm = new ResourceManager('list.json', () => {
 *      const someIcon = rm.icons['icon-id']; // Объект Image
 *
 *      const textureObject = rm.textures['texture-id']; // Текстура с дескрипторами
 *
 *      const image = textureObject.img; // Объект Image
 *
 *      const descriptor = textureObject.desc['descriptor-id']; // Дескриптор спрайта
 *      const {left, top, right, bottom} = descriptor; // Текстурные координаты
 *  });
 *
 *  Пример файла list.json:
 *  {
 *    "icons": {
 *      "icon-id": "icon-src.png",
 *      "another-icon-id": "another-icon-src.png"
 *    },
 *
 *    "textures": {
 *      "texture-id": {
 *        "src": "image-src.png",
 *        "desc": "descriptors-src.json"
 *      },
 *
 *      "another-texture-id": {
 *        "src": "another-image-src.png",
 *        "desc": "another-descriptors-src.json"
 *      }
 *    }
 *  }
 *
 *  Пример файла descriptors-src.json:
 *  {
 *    "descriptor-id": {
 *      "left": 0,
 *      "top": 0,
 *      "right": 0.5,
 *      "bottom": 0.5
 *    },
 *
 *    "another-descriptor-id": {
 *      "left": 0.5,
 *      "top": 0.5,
 *      "right": 1,
 *      "bottom": 1
 *    }
 *  }
 */
class ResourceManager {
    constructor(src, callback) {
        const that = this;
        this.textures = {};
        this.icons = {};

        this.onload = null;

        function loadTexture(name, src, descriptorSrc) {
            that.textures[name] = {img: null, desc: null};

            const imgPromise = new Promise((resolve, reject) => {
                const img = new Image();
                img.onload = () => {
                    that.textures[name].img = img;
                    resolve();
                };
                img.src = src;
            });

            const descPromise = new Promise((resolve, reject) => {
                const request = new XMLHttpRequest();
                request.onreadystatechange = () => {
                    if (request.readyState === 4 && request.status === 200) {
                        that.textures[name].desc = JSON.parse(request.responseText);
                        resolve();
                    }
                };
                request.open('GET', descriptorSrc, true);
                request.send();
            });

            return Promise.all([imgPromise, descPromise]);
        }

        function loadIcon(name, src) {
            return new Promise((resolve, reject) => {
                that.icons[name] = null;
                const img = new Image();
                img.onload = () => {
                    that.icons[name] = img;
                    resolve();
                };
                img.src = src;
            });
        }

        const request = new XMLHttpRequest();

        request.onreadystatechange = () => {
            if (request.readyState === 4 && request.status === 200) {
                const loadList = JSON.parse(request.responseText);

                const promiseList = [];

                for (let idx in loadList.icons) {
                    promiseList.push(loadIcon(idx, loadList.icons[idx]));
                }

                for (let idx in loadList.textures) {
                    promiseList.push(loadTexture(idx,
                        loadList.textures[idx].src,
                        loadList.textures[idx].desc));
                }

                Promise.all(promiseList).then(callback);
            }
        };

        request.open('GET', src, true);
        request.send();
    }
}
