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

    sortList(listName) {
        this[listName].sort((a, b) => {
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
