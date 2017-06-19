class ResourceManager {
    constructor(callback, src) {
        const that = this;
        this.textures = {};
        this.icons = {};

        function isReady() {
            for (let idx in that.textures) {
                if (!that.textures[idx] || !that.textures[idx].img || !that.textures[idx].desc) {
                    return false;
                }
            }

            for (let idx in that.icons) {
                if (!that.icons[idx]) {
                    return false;
                }
            }

            return true;
        }

        function checkReady() {
            if (isReady()) {
                callback();
            }
        }

        function loadTexture(name, src, descriptorSrc) {
            that.textures[name] = {img: null, desc: null};

            const img = new Image();
            img.onload = () => {
                that.textures[name].img = img;
                checkReady();
            };
            img.src = src;

            const request = new XMLHttpRequest();
            request.onreadystatechange = () => {
                if (request.readyState === 4 && request.status === 200) {
                    that.textures[name].desc = JSON.parse(request.responseText);
                    checkReady();
                }
            };
            request.open('GET', descriptorSrc, true);
            request.send();
        }

        function loadIcon(name, src) {
            that.icons[name] = null;
            const img = new Image();
            img.onload = () => {
                that.icons[name] = img;
                checkReady();
            };
            img.src = src;
        }

        const request = new XMLHttpRequest();

        request.onreadystatechange = () => {
            if (request.readyState === 4 && request.status === 200) {
                const loadList = JSON.parse(request.responseText);

                for (let idx in loadList.icons) {
                    that.icons[idx] = null;
                }

                for (let idx in loadList.textures) {
                    that.textures[idx] = null;
                }

                for (let idx in loadList.icons) {
                    loadIcon(idx, loadList.icons[idx]);
                }

                for (let idx in loadList.textures) {
                    loadTexture(idx,
                        loadList.textures[idx].src,
                        loadList.textures[idx].desc);
                }
            }
        };

        request.open('GET', src, true);
        request.send();
    }
}
