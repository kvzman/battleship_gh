from random import randint


class BoardException(Exception):
    pass


class OutBoardException(BoardException):
    def __str__(self):
        return "Выстрел мимо доски!"


class UsedBoardException(BoardException):
    def __str__(self):
        return "В эту клетку уже стреляли!"


class WrongShipBoardException(BoardException):
    pass


class Pos:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Pos({self.x}, {self.y})"


class Ship:
    def __init__(self, length, bow, vector):
        self.length = length
        self.bow = bow
        self.lives = length
        self.vector = vector

    @property
    def position(self):
        ship_pos = []
        for i in range(self.length):
            cur_x = self.bow.x
            cur_y = self.bow.y
            if self.vector == 0:
                cur_x += i
            if self.vector == 1:
                cur_y += i
            ship_pos.append(Pos(cur_x, cur_y))
        return ship_pos

    # метод не используется
    # def killed(self, shot):
    #     return shot in self.position


class Board:
    def __init__(self, hid=False, size=6):
        self.hid = hid
        self.size = size
        self.count_killed = 0
        self.cells = [["0"] * size for _ in range(size)]
        self.navy = []
        self.busy = []

    def __str__(self):
        show_board = "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.cells):
            show_board += f"\n{i+1} | " + " | ".join(row) + " | "

        if self.hid:
            show_board = show_board.replace("#", "0")

        return show_board

    def out(self, cell):
        return not ((0 <= cell.x < self.size) and (0 <= cell.y < self.size))

    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]

        for cell in ship.position:
            for x, y in near:
                cur = Pos(cell.x + x, cell.y + y)
                if not(self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.cells[cur.x][cur.y] = "."
                self.busy.append(cur)

    def add_ship(self, ship):
        for cell in ship.position:
            if self.out(cell) or cell in self.busy:
                raise WrongShipBoardException()

        for cell in ship.position:
            self.cells[cell.x][cell.y] = "#"
            self.busy.append(cell)

        self.navy.append(ship)
        self.contour(ship)

    def shot(self, hit):
        if self.out(hit):
            raise OutBoardException
        if hit in self.busy:
            raise UsedBoardException

        self.busy.append(hit)

        for ship in self.navy:
            if hit in ship.position:
                ship.lives -= 1
                self.cells[hit.x][hit.y] = "X"
                if ship.lives == 0:
                    self.count_killed += 1
                    self.contour(ship, verb=True)
                    print("Корабль уничножен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True

        self.cells[hit.x][hit.y] = "."
        print("Мимо!")
        return False

    def begin(self):
        self.busy = []

    def defeat(self):
        return self.count_killed == len(self.navy)


class Player:
    def __init__(self, player_board, enemy_board):
        self.player_board = player_board
        self.enemy_board = enemy_board

    def ask(self):
        raise NotImplementedError

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy_board.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class Com(Player):
    def ask(self):
        while True:
            hit = Pos(randint(0, 5), randint(0, 5))
            for ship in self.enemy_board.navy:
                if hit in ship.position and hit not in self.enemy_board.busy:
                    print(f"Ход компьютера: {hit.x + 1} {hit.y + 1}")
                    return hit


class User(Player):
    def ask(self):
        while True:
            hit = input("Ваш ход:  ").split()
            if len(hit) != 2:
                print("Введите две координаты через пробел!")
                continue
            x, y = hit
            if not(x.isdigit()) or not(y.isdigit()):
                print("Введите целые числа в качестве координат!")
            x, y = int(x), int(y)
            return Pos(x-1, y-1)


class Game:
    def __init__(self, size=6):
        self.size = size
        self.harbor = [3, 2, 2, 1, 1, 1, 1]
        pl = self.random_board()
        co = self.random_board()
        co.hid = True                          # скрывает корабли компьютера в консоли
        self.user = User(pl, co)
        self.com = Com(co, pl)

    def try_board(self):
        board = Board(size=self.size)
        attempts = 0
        for length in self.harbor:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(length, Pos(randint(0, self.size), randint(0, self.size)), randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except WrongShipBoardException:
                    pass
        board.begin()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    @staticmethod
    def greet():
        print("-----------------------------")
        print("           Привет!           ")
        print("   Это игра - морской бой!   ")
        print("-----------------------------")
        print(" формат ввода координат: x y ")
        print(" x - номер строки            ")
        print(" y - номер столбца           ")

    def print_boards(self):
        print("-" * 20)
        print("Доска пользователя:")
        print(self.user.player_board)
        print("-" * 20)
        print("Доска компьютера:")
        print(self.com.player_board)
        print("-" * 20)

    def loop(self):
        move_number = 0
        while True:
            self.print_boards()
            if move_number % 2 == 0:
                print("Ходит пользователь!")
                repeat = self.user.move()
            else:
                print("Ходит компьютер!")
                repeat = self.com.move()

            if repeat:
                move_number -= 1

            if self.com.player_board.defeat():
                self.print_boards()
                print("-" * 20)
                print("Пользователь выиграл!")
                break

            if self.user.player_board.defeat():
                self.print_boards()
                print("-" * 20)
                print("Компьютер выиграл!")
                break
            move_number += 1

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()
