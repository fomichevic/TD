// Зависит от:
// https://cdnjs.cloudflare.com/ajax/libs/socket.io/2.0.3/socket.io.js

/**
 * Класс-обертка для SocketIO
 * Пример использования:
 *  const t = new Transmission((o) => { // Обработчик события получения состояния мира
 *      // o -- уже обработанный объект, а не JSON-строка
 *      const players = o.players; // Список игроков
 *      const first = players[0]; // Первый игрок
 *      const second = players[1]; // Второй игрок
 *
 *      // Далее будем работать с первым игроком, то же самое можно сделать и со вторым
 *      const id = first.id; // Идентификатор игрока
 *      const resources = first.resources; // Количество ресурсов игрока
 *
 *      const staticUnits = first.static; // Статические юниты
 *      const dynamicUnits = first.dynamic; // Динамические юниты
 *      // Если сервер не прислал словари статических и динамических юнитов, то вместо них используются пустые объекты
 *
 *      const castle = staticUnits['castle']; // Замок (главное здание)
 *
 *      const unit = dynamicUnits['my-dynamic-unit']; // Произвольный юнит
 *
 *      const position = unit.position; // Положение юнита
 *      const x = position.x; // Координата по оси X
 *      const y = position.y; // Координата по оси Y
 *
 *      const type = unit.type; // Тип юнита, например, 'swordsman'. Точного списка типов пока нет
 *      const hp = unit.hp; // Характеристика прочности/здоровья юнита
 *      const currentHp = hp.current; // Текущая прочность/здоровье
 *      const maxHp = hp.maximal; // Максимальная прочность/здоровье
 *  });
 *
 *  const id = t.id; // Идентификатор сокета
 *
 *  t.send('something'); // Отправка сообщения на сервер, будет использоваться для пользовательского ввода
 */

class Transmission
{
    constructor(stateCallback) {
        this.socket = io.connect(document.domain + ':' + location.port);

        this.socket.on('state-json', (msg) => {
            const got = JSON.parse(msg);
            for (const p of got.players) {
                p.static = p.static || {};
                p.dynamic = p.dynamic || {};
            }
            stateCallback(got);
        });
    }

    send(msg) {
        this.socket.emit('client-input', msg);
    }

    get id() {
        return this.socket.id;
    }
}
