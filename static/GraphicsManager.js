class GraphicsManager
{
    static get() {
        if (!this.instance) {
            this.instance = new this();
        }
        return this.instance;
    }

    constructor() {
        this.static = {};
        this.dynamic = {};
        this.background = {};
    }

    optimalIdList(type) {
        const list = [];
        for (let id in this[type]) {
            list.push(id);
        }

        list.sort((a, b) => {
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

        return list;
    }
}
