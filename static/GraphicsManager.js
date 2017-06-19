class GraphicsManager {
    static get() {
        if (!this.instance) {
            this.instance = new this();
        }
        return this.instance;
    }

    constructor() {
        this.static = [];
        this.dynamic = [];
        this.background = [];
    }

    createSprite(type, texture, descriptor) {
        const sprite = {
            texture: texture,
            descriptor: descriptor,
            position: {
                x: 0,
                y: 0
            },
            size: {
                x: 0,
                y: 0
            }
        };

        this[type].push(sprite);
        return sprite;
    }

    getSpriteList(type, optimize = false) {
        if (optimize) {
            this.optimizeSpriteList(type);
        }

        return this[type];
    }

    optimizeSpriteList(type) {
        this[type].sort((a, b) => {
            if (a.texture < b.texture) {
                return -1;
            }

            if (a.texture > b.texture) {
                return 1;
            }

            if (a.descriptor < b.descriptor) {
                return -1;
            }

            if (a.descriptor > b.descriptor) {
                return 1;
            }

            return 0;
        });
    }
}
