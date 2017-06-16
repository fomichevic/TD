class GraphicsManager
{
    static get() {
        if (!this.instance) {
            this.instance = new this();
        }
        return this.instance;
    }

    constructor() {
        // {
        // textureName: string,
        // textureBox: { left: number, top: number, right: number, bottom: number }
        // }
        this.static = [];
        this.dynamic = [];
        this.background = [];
    }

    sortList(listName) {
        const list = this[listName];
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
    }

    drawString() {
        return JSON.stringify({
            static: this.static,
            dynamic: this.dynamic,
            background: this.background
        });
    }
}
