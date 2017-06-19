class ResourceManager
{
    static get() {
        if (!this.instance) {
            this.instance = new this();
        }
        return this.instance;
    }

    constructor() {
        this.textures = {};
        this.icons = {};

        this.onload = null;
    }

    get ready() {
        for (let idx in this.textures) {
            if (!this.textures[idx] || !this.textures[idx].img || !this.textures[idx].desc) {
                return false;
            }
        }

        for (let idx in this.icons) {
            if (!this.icons[idx]) {
                return false;
            }
        }

        return true;
    }

    checkReady() {
        if (this.onload && this.ready) {
            this.onload();
        }
    }

    load(src) {
        const request = new XMLHttpRequest();

        request.onreadystatechange = () => {
            if (request.readyState === 4 && request.status === 200) {
                const loadList = JSON.parse(request.responseText);

                for (let idx in loadList.icons) {
                    this.icons[idx] = null;
                }

                for (let idx in loadList.textures) {
                    this.textures[idx] = { img: null, desc: null };
                }

                for (let idx in loadList.icons) {
                    this.loadIcon(idx, loadList.icons[idx]);
                }

                for (let idx in loadList.textures) {
                    this.loadTexture(idx,
                        loadList.textures[idx].src,
                        loadList.textures[idx].desc);
                }
            }
        };

        request.open('GET', src, true);
        request.send();
    }

    loadTexture(name, src, descriptorsSrc) {
        this.textures[name] = { img: null, desc: null };

        const img = new Image();
        img.onload = () => {
            this.textures[name].img = img;
            this.checkReady();
        };
        img.src = src;

        const request = new XMLHttpRequest();
        request.onreadystatechange = () => {
            if (request.readyState === 4 && request.status === 200) {
                this.textures[name].desc = JSON.parse(request.responseText);
                this.checkReady();
            }
        };
        request.open('GET', descriptorsSrc, true);
        request.send();
    }

    loadIcon(name, src) {
        this.icons[name] = null;
        const img = new Image();
        img.onload = () => {
            this.icons[name] = img;
            this.checkReady();
        };
        img.src = src;
    }
}