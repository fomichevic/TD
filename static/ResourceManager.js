class ResourceManager {
    constructor(callback, src) {
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
                        checkReady();
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
