import os
import random
import sys
import tkinter as tk

from glob import glob
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

from PIL import Image, ImageDraw, ImageFont, ImageTk

import camelup.camelup as camelup
import camelup.config as config
import camelup.treesearch as treesearch


CURR_DIR = os.path.dirname(os.path.abspath(__file__))

font = ImageFont.truetype(os.path.join(CURR_DIR, "fonts/arial.ttf"), 9)


def create_board(img, game):
    """Create the board from the base image

    Parameters
    ----------
    img : PIL object
        Base board to put the board onto
    game : camelup game
        Camel up game to visualize

    Returns
    -------
    dict
        Info for where the tiles were placed on the image

    """
    board_info = dict()
    draw = ImageDraw.Draw(img)
    border = 5
    width = (img.size[0] - border * 2) / 5
    height = (img.size[1] - border * 2) / 5
    space = 1
    top_left_corner = (border, border)
    bottom_right_corner = (top_left_corner[0] + width, top_left_corner[1] + height)
    draw.rectangle(
        [top_left_corner, bottom_right_corner],
        fill=(251, 207, 41),
        outline=(29, 29, 29),
    )
    draw.text(
        (top_left_corner[0] + 2, top_left_corner[1] + 2),
        str(space),
        font=font,
        fill=(0, 0, 0),
    )
    board_info[space] = (top_left_corner, bottom_right_corner)
    space += 1
    for i in range(4):
        top_left_corner = (top_left_corner[0] + width, top_left_corner[1])
        bottom_right_corner = (top_left_corner[0] + width, top_left_corner[1] + height)
        draw.rectangle(
            [top_left_corner, bottom_right_corner],
            fill=(251, 207, 41),
            outline=(29, 29, 29),
        )
        draw.text(
            (top_left_corner[0] + 2, top_left_corner[1] + 2),
            str(space),
            font=font,
            fill=(0, 0, 0),
        )
        board_info[space] = (top_left_corner, bottom_right_corner)
        space += 1
    for i in range(4):
        top_left_corner = (top_left_corner[0], top_left_corner[1] + height)
        bottom_right_corner = (top_left_corner[0] + width, top_left_corner[1] + height)
        draw.rectangle(
            [top_left_corner, bottom_right_corner],
            fill=(251, 207, 41),
            outline=(29, 29, 29),
        )
        draw.text(
            (top_left_corner[0] + 2, top_left_corner[1] + 2),
            str(space),
            font=font,
            fill=(0, 0, 0),
        )
        board_info[space] = (top_left_corner, bottom_right_corner)
        space += 1
    for i in range(4):
        top_left_corner = (top_left_corner[0] - width, top_left_corner[1])
        bottom_right_corner = (top_left_corner[0] + width, top_left_corner[1] + height)
        draw.rectangle(
            [top_left_corner, bottom_right_corner],
            fill=(251, 207, 41),
            outline=(29, 29, 29),
        )
        draw.text(
            (top_left_corner[0] + 2, top_left_corner[1] + 2),
            str(space),
            font=font,
            fill=(0, 0, 0),
        )
        board_info[space] = (top_left_corner, bottom_right_corner)
        space += 1
    for i in range(3):
        top_left_corner = (top_left_corner[0], top_left_corner[1] - height)
        bottom_right_corner = (top_left_corner[0] + width, top_left_corner[1] + height)
        draw.rectangle(
            [top_left_corner, bottom_right_corner],
            fill=(251, 207, 41),
            outline=(29, 29, 29),
        )
        draw.text(
            (top_left_corner[0] + 2, top_left_corner[1] + 2),
            str(space),
            font=font,
            fill=(0, 0, 0),
        )
        board_info[space] = (top_left_corner, bottom_right_corner)
        space += 1
    draw.text((120, 340), "To Be Rolled", font=font, fill=(0, 0, 0))

    bet_str = "Bet Tiles (Colour - Value)"
    for key, val in game.bet_tiles.items():
        bet_str += f"\n{key} - {val[0]}"
    draw.text((120, 120), bet_str, font=font, fill=(0, 0, 0))

    player_str = "Player Items"
    for key, val in game.player_dict.items():
        player_str += f'\n{val["name"]} Coins: {val["coins"]} Bet Tiles: '
        for tile, bets in game.player_dict[key]["bet_tiles"].items():
            player_str += f"{tile[0]}("
            player_str += ", ".join(str(x) for x in bets)
            player_str += ") "
    draw.text((120, 220), player_str, font=font, fill=(0, 0, 0))

    game_str = (
        f"Winner Bets: {len(game.winner_bets)}\nLoser Bets: {len(game.loser_bets)}"
    )
    draw.text((300, 120), game_str, font=font, fill=(0, 0, 0))
    return board_info


def modulo_space(space):
    """Translate spaces greater than 16 to a space on the board

    Parameters
    ----------
    space : int
        Space the camel was on

    Returns
    -------
    int
        Space the camel will be displayed on

    """
    if space % 16 == 0:
        return 16
    else:
        return space % 16


def open_camel(file):
    """Open the camel files and put the transparceny filter on them

    Parameters
    ----------
    file : str
        File location

    Returns
    -------
    object
        PIL image object

    """
    camel = Image.open(file)
    transparency = Image.new("RGBA", camel.size, (0, 0, 0, 0))
    transparency.paste(camel, (0, 0))
    per = 0.1
    wsize = int(transparency.size[0] * per)
    hsize = int(transparency.size[1] * per)
    return transparency.resize((wsize, hsize), Image.ANTIALIAS)


picture_dict = dict()
for camel in config.CAMELS:
    file = glob(os.path.join(CURR_DIR, f"img/*{camel}*"))[0]
    picture_dict[camel] = open_camel(file)


def place_camel_dict(img, game, board_info):
    """Placing the camels on the board

    Parameters
    ----------
    img : object
        PIL image to put the camels on
    game : class
        Camelup game to visualize
    board_info : dict
        Dict with info about where to place tiles
    """
    counter = 0
    border = 5
    width = (img.size[0] - border * 2) / 5
    for camel, values in game.camel_dict.items():
        pic = picture_dict[camel]
        square = board_info[modulo_space(values["space"])]
        x = int(square[0][0] + width / 2 - (pic.size[0] / 2))
        y = int(square[1][1] - pic.size[0] - ((values["height"] - 1) * 14))
        img.paste(pic, (x, y), mask=pic)
        if values["need_roll"]:
            x = 120 + counter * 35
            y = 350
            img.paste(pic, (x, y), mask=pic)
            counter += 1


def place_tiles(img, game, board_info):
    """Place tiles on board

    Parameters
    ----------
    img : object
        PIL image to put the camels on
    game : class
        Camelup game to place
    board_info : dict
        Dict with info about where to place tiles
    """
    draw = ImageDraw.Draw(img)
    for space, val in game.tiles_dict.items():
        tile = board_info[space]
        top_left_corner = (tile[0][0] + 10, tile[0][1] + 10)
        bottom_right_corner = (tile[1][0] - 10, tile[1][1] - 10)
        draw.rectangle(
            [top_left_corner, bottom_right_corner],
            fill=(255, 225, 255),
            outline=(29, 29, 29),
        )
        draw.text(
            (tile[0][0] + 25, tile[0][1] + 35),
            val["tile_type"],
            font=font,
            fill=(0, 0, 0),
        )


class CamelApp(tk.Tk):
    """Top level tk app

    Attributes
    ----------
    title : str
        Title of app
    game : class
        Camelup class to visualize
    _frame : frame
        Current frame to show within the app

    """

    def __init__(self):
        tk.Tk.__init__(self)
        self.title("Camel Up")
        self.game = camelup.Game(2)
        self._frame = StartPage(self, self.game)
        self._frame.pack()

    def switch_to_start(self):
        """Switch to start frame, reset the game
        """
        self._frame.destroy()
        self.game = camelup.Game(2)
        self._frame = StartPage(self, self.game)
        self._frame.pack()

    def switch_to_game(self):
        """Switch to game frame
        """
        self.game = self._frame.game
        self._frame.destroy()
        self._frame = GamePage(self, self.game)
        self._frame.update()
        self._frame.pack()


class StartPage(tk.Frame):
    """Frame for the starting page of the app
    Attributes
    ----------
    names : list
        Names of players
    player_labels : list
        Player labels
    num_players : object
        Combobox object to select players
    game_enter : object
        Button object to enter game
    """

    def __init__(self, master, game):
        tk.Frame.__init__(self, master)
        self.master = master
        self.game = game
        self.names = list()
        self.player_labels = list()
        self.num_players = ttk.Combobox(self, values=["2", "3", "4", "5", "6"])
        self.num_players.grid(column=1, row=0)
        tk.Label(self, text=f"Number of Players").grid(column=0, row=0)
        self.game_enter = ttk.Button(
            self, text="Start Game", command=self.destroy_start
        )
        self.num_players.bind("<<ComboboxSelected>>", self.name_text_boxes)

    def destroy_start(self):
        """Destroy the start frame
        """
        for counter, name in enumerate(self.names):
            self.game.player_dict[counter + 1]["name"] = name.get()
        self.master.switch_to_game()

    def name_text_boxes(self, event):
        """Genreate the text boxes to input names based of number of players selected
        """
        for name in self.names:
            name.destroy()
        for label in self.player_labels:
            label.destroy()
        self.game_enter.pack_forget()
        self.game = camelup.Game(int(self.num_players.get()))
        del self.names[:]
        del self.player_labels[:]
        for num in range(int(self.num_players.get())):
            self.player_labels.append(tk.Label(self, text=f"Player: {num+1}"))
            self.player_labels[-1].grid(row=num + 1, column=0)
            self.names.append(tk.Entry(self))
            self.names[-1].grid(row=num + 1, column=1)
        self.game_enter.grid(row=num + 2, column=0, columnspan=1)


class GamePage(tk.Frame):
    """Game frame

    Attributes
    ----------
    img : object
        Image of camelup game
    board : object
        Label that contains `img`
    player_turn_text : object
        Text with which player's turn it is
    player_turn : object
        Label that contains `player_turn_text`
    combo : object
        Combobox with all the potential moves
    turn_enter : object
        Button to enter the play
    turn_info : object
        Info with what happened within the turn
    turn_info_label : type
        Lable for `turn_info`
    """

    def __init__(self, master, game):
        tk.Frame.__init__(self, master)
        self.master = master
        self.game = game
        self.img = Image.new("RGB", (500, 500), color=(236, 192, 81))
        self.board = tk.Label(self)
        self.board.img = ImageTk.PhotoImage(self.img)
        self.board.config(image=self.board.img)
        self.board.grid(column=0, row=0, rowspan=4)

        self.player_turn_text = tk.StringVar()
        self.player_turn_text.set(
            f"Turn: Player {self.game.player_dict[self.game.state]['name']}"
        )
        self.player_turn = tk.Label(self, textvariable=self.player_turn_text)
        self.player_turn.grid(column=1, row=0)

        self.combo = ttk.Combobox(self, values=list(self.game.available_moves().keys()))
        self.combo.grid(column=1, row=1)
        self.combo.current(0)

        self.turn_enter = ttk.Button(self, text="Play", command=self.play)
        self.turn_enter.grid(column=1, row=2)

        self.turn_info = tk.StringVar()
        self.turn_info_label = ScrolledText(self)
        self.turn_info_label.replace("1.0", tk.END, self.turn_info.get())
        self.turn_info_label.grid(column=1, row=3)

    def update(self):
        """Updates the image of the board
        """
        self.img = Image.new("RGB", (500, 500), color=(236, 192, 81))
        self.board_info = create_board(self.img, self.game)
        place_camel_dict(self.img, self.game, self.board_info)
        place_tiles(self.img, self.game, self.board_info)
        self.board.img = ImageTk.PhotoImage(self.img)
        self.board.config(image=self.board.img)
        self.combo.config(values=list(self.game.available_moves().keys()))
        self.player_turn_text.set(
            f"Turn: Player {self.game.player_dict[self.game.state]['name']}"
        )

    def play(self):
        """Executes a play
        """
        print(self.combo.get())
        if self.combo.get() == "Roll":
            need_roll = [
                key
                for key in self.game.camel_dict.keys()
                if self.game.camel_dict[key]["need_roll"]
            ]
            camel = random.choice(need_roll)
            roll = random.randint(1, 3)
            output = self.game.play(
                self.game.available_moves()[self.combo.get()]
                .replace("camel", f"'{camel}'")
                .replace(", roll", f", {roll}")
            )
            self.turn_info.set(
                f"Camel: {camel} Rolled: {str(roll)}\n{self.turn_info.get()}"
            )
            self.turn_info_label.replace("1.0", tk.END, self.turn_info.get())
            if output == "Done":
                self.player_turn.grid_forget()
                self.combo.grid_forget()
                self.turn_enter.grid_forget()
                self.img = Image.new("RGB", (500, 500), color=(236, 192, 81))
                self.board_info = create_board(self.img, self.game)
                place_camel_dict(self.img, self.game, self.board_info)
                place_tiles(self.img, self.game, self.board_info)
                self.board.img = ImageTk.PhotoImage(self.img)
                self.board.config(image=self.board.img)
                self.end = tk.Label(self, text="Game Done")
                self.end.grid(column=1, row=0, rowspan=2)
                self.restart = tk.Button(
                    self,
                    text="Play Again",
                    command=lambda: self.master.switch_to_start(),
                )
                self.restart.grid(column=1, row=2)
                return
        else:
            self.game.play(self.game.available_moves()[self.combo.get()])
        if self.game.player_dict[self.game.state]["name"] == "Robot":
            moves = treesearch.get_move(self.game)
            best_move = max(moves, key=moves.get)
            self.turn_info.set(
                f"Robot Move: {best_move} Utility: {moves[best_move]}\n{self.turn_info.get()}"
            )
            self.turn_info_label.replace("1.0", tk.END, self.turn_info.get())
            if "roll" in best_move:
                need_roll = [
                    key
                    for key in self.game.camel_dict.keys()
                    if self.game.camel_dict[key]["need_roll"]
                ]
                camel = random.choice(need_roll)
                roll = random.randint(1, 3)
                output = self.game.play(
                    best_move.replace("camel", f"'{camel}'").replace(
                        ", roll", f", {roll}"
                    )
                )
                self.turn_info.set(
                    f"Camel: {camel} Rolled: {str(roll)}\n{self.turn_info.get()}"
                )
                self.turn_info_label.replace("1.0", tk.END, self.turn_info.get())
                if output == "Done":
                    self.player_turn.grid_forget()
                    self.combo.grid_forget()
                    self.turn_enter.grid_forget()
                    self.img = Image.new("RGB", (500, 500), color=(236, 192, 81))
                    self.board_info = create_board(self.img, self.game)
                    place_camel_dict(self.img, self.game, self.board_info)
                    place_tiles(self.img, self.game, self.board_info)
                    self.board.img = ImageTk.PhotoImage(self.img)
                    self.board.config(image=self.board.img)
                    self.end = tk.Label(self, text="Game Done")
                    self.end.grid(column=1, row=0, rowspan=2)
                    self.restart = tk.Button(
                        self,
                        text="Play Again",
                        command=lambda: self.master.switch_to_start(),
                    )
                    self.restart.grid(column=1, row=2)
                    return
            else:
                self.game.play(best_move)
        self.update()


if __name__ == "__main__":
    app = CamelApp()
    app.mainloop()
