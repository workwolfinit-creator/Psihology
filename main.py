import flet as ft
import asyncio
import random


async def main(page: ft.Page):
    # --- НАСТРОЙКИ ---
    page.title = "Neon Checkers | Hunter Mode"
    page.bgcolor = "#050505"
    page.padding = 0
    page.theme_mode = "dark"
    page.scroll = None

    GAME_WIDTH = 350
    GAME_HEIGHT = 650

    # 5 КОЛОНОК
    COLS = [35, 105, 175, 245, 315]
    CELL_H = 70

    PLAYER_SIZE = 50
    ENEMY_SIZE = 50

    state = {
        "running": False,
        "score": 0,
        "speed": 3,
        "p_col": 2,
        "p_row": 0,
        "enemies": [],
        "is_moving": False,
    }

    # --- ВИЗУАЛ ---
    combo_text = ft.Text("", size=40, weight="bold", color="#FFFF00", opacity=0, animate_opacity=200)
    score_text = ft.Text("0", size=100, weight="bold", color="#FFFFFF1A", text_align="center")

    def create_checker(color, glow_color):
        return ft.Container(
            width=PLAYER_SIZE,
            height=PLAYER_SIZE,
            bgcolor=color,
            border_radius=ft.BorderRadius.all(50),
            shadow=ft.BoxShadow(spread_radius=2, blur_radius=15, color=glow_color),
            alignment=ft.alignment.Alignment(0, 0),
            content=ft.Container(
                width=PLAYER_SIZE * 0.6,
                height=PLAYER_SIZE * 0.6,
                border=ft.Border.all(3, "#80000000"),
                border_radius=ft.BorderRadius.all(50)
            )
        )

    player_content = create_checker("#00FF00", "#00FF00")

    def get_pos(col, row):
        x = COLS[col] - (PLAYER_SIZE / 2)
        y = (row * CELL_H) + 20
        return x, y

    start_x, start_y = get_pos(2, 0)

    player = ft.Container(
        content=player_content,
        left=start_x,
        bottom=start_y,
        animate_position=100
    )

    game_area = ft.Stack(
        controls=[score_text, combo_text, player],
        width=GAME_WIDTH,
        height=GAME_HEIGHT,
    )

    # --- ЛОГИКА ---
    def game_over():
        state["running"] = False
        game_over_screen.content.controls[2].value = str(state["score"])
        game_over_screen.visible = True
        page.update()

    def restart_game(e=None):
        state["running"] = True
        state["score"] = 0
        state["speed"] = 3
        state["p_col"] = 2
        state["p_row"] = 0
        state["enemies"] = []
        state["is_moving"] = False

        game_area.controls = [score_text, combo_text, player]

        score_text.value = "0"
        px, py = get_pos(2, 0)
        player.left = px
        player.bottom = py

        player.content.bgcolor = "#00FF00"
        player.content.shadow.color = "#00FF00"

        game_over_screen.visible = False
        page.update()
        asyncio.create_task(game_loop())

    game_over_screen = ft.Container(
        visible=False,
        bgcolor="#E6000000",
        alignment=ft.alignment.Alignment(0, 0),
        content=ft.Column([
            ft.Text("GAME OVER", size=26, color="#FF0000", weight="bold"),
            ft.Text("Счет:", size=20, color="white"),
            ft.Text("0", size=50, weight="bold", color="#00FF00"),
            ft.FilledButton("ЗАНОВО", style=ft.ButtonStyle(bgcolor="#00FF00", color="black"), width=200,
                            on_click=restart_game)
        ], horizontal_alignment="center", alignment=ft.MainAxisAlignment.CENTER),
        width=GAME_WIDTH, height=GAME_HEIGHT
    )

    # --- ПОИСК ВРАГОВ ---
    def get_enemy_at_grid(target_col, target_row):
        target_bottom = (target_row * CELL_H) + 20
        target_top_y = GAME_HEIGHT - target_bottom - PLAYER_SIZE

        for enemy in state["enemies"]:
            enemy_cx = enemy.left + (PLAYER_SIZE / 2)
            grid_cx = COLS[target_col]

            if abs(enemy_cx - grid_cx) < 20:
                if abs(enemy.top - target_top_y) < 50:
                    return enemy
        return None

    # --- ДВИЖЕНИЕ ИГРОКА ---
    def move_player(dir_x, dir_y):
        if not state["running"] or state["is_moving"]: return

        cur_c, cur_r = state["p_col"], state["p_row"]
        tar_c, tar_r = cur_c + dir_x, cur_r + dir_y

        if tar_c < 0 or tar_c > 4: return
        if tar_r < 0 or tar_r > 7: return

        enemy = get_enemy_at_grid(tar_c, tar_r)

        if enemy:
            # АТАКА (Прыжок)
            jmp_c, jmp_r = cur_c + (dir_x * 2), cur_r + (dir_y * 2)

            # ВАЖНО: Если прыгать некуда (стена или верх) - ничего не делаем.
            # Это и есть "классика": нельзя бить у борта.
            if 0 <= jmp_c <= 4 and 0 <= jmp_r <= 7:
                asyncio.create_task(perform_jump_kill(jmp_c, jmp_r, enemy))
        else:
            # ОБЫЧНЫЙ ШАГ
            asyncio.create_task(perform_step(tar_c, tar_r))

    async def perform_step(c, r):
        state["is_moving"] = True
        state["p_col"], state["p_row"] = c, r
        nx, ny = get_pos(c, r)
        player.left, player.bottom = nx, ny
        page.update()
        await asyncio.sleep(0.1)
        state["is_moving"] = False

    async def perform_jump_kill(c, r, enemy):
        state["is_moving"] = True

        player.content.bgcolor = "#FFFFFF"
        player.content.shadow.color = "#FFFFFF"
        player.content.shadow.blur_radius = 40

        state["p_col"], state["p_row"] = c, r
        nx, ny = get_pos(c, r)
        player.left, player.bottom = nx, ny

        if enemy in state["enemies"]:
            state["enemies"].remove(enemy)
            if enemy in game_area.controls: game_area.controls.remove(enemy)
            state["score"] += 10
            score_text.value = str(state["score"])
            asyncio.create_task(show_combo(enemy.left, enemy.top, "KILL!"))

        page.update()
        await asyncio.sleep(0.15)

        player.content.bgcolor = "#00FF00"
        player.content.shadow.color = "#00FF00"
        player.content.shadow.blur_radius = 15
        state["is_moving"] = False
        page.update()

    async def show_combo(x, y, text):
        combo_text.value = text
        combo_text.left = x
        combo_text.top = y
        combo_text.opacity = 1
        page.update()
        await asyncio.sleep(0.3)
        combo_text.opacity = 0
        page.update()

    # --- ЛОГИКА ОХОТНИКОВ (ORANGE HUNTERS) ---
    async def hunter_attack(enemy):
        # Охотник прыгает на игрока
        enemy.content.bgcolor = "#FFFFFF"
        enemy.update()

        # Прыжок в позицию игрока
        enemy.top = GAME_HEIGHT - player.bottom - PLAYER_SIZE
        enemy.left = player.left
        page.update()

        await asyncio.sleep(0.1)
        game_over()

    def spawn_enemy():
        is_hunter = random.random() < 0.35  # 35% шанс Оранжевого

        if is_hunter:
            # Оранжевый Охотник
            col = random.randint(0, 4)
            color = "#FF8800"
            tag = "hunter"
        else:
            # Красная пешка
            col = random.randint(0, 4)
            color = "#FF0044"
            tag = "normal"

        enemy = ft.Container(
            content=create_checker(color, color),
            left=COLS[col] - (PLAYER_SIZE / 2),
            top=-60,
            data={"col": col, "tag": tag}
        )

        game_area.controls.insert(1, enemy)
        state["enemies"].append(enemy)

    async def game_loop():
        spawn_timer = 0
        while state["running"]:
            threshold = 60 if state["score"] < 50 else 35
            spawn_timer += 1
            if spawn_timer > threshold:
                spawn_enemy()
                spawn_timer = 0

            for enemy in state["enemies"][:]:
                # Падение вниз
                enemy.top += state["speed"]

                # --- ЛОГИКА ОХОТНИКА ---
                if enemy.data["tag"] == "hunter" and not state["is_moving"]:
                    # Если игрок рядом по диагонали (снизу)
                    p_top_y = GAME_HEIGHT - player.bottom - PLAYER_SIZE
                    p_col = state["p_col"]
                    e_col = enemy.data["col"]

                    dist_y = p_top_y - enemy.top

                    # Охотник атакует, если игрок чуть ниже (дистанция удара)
                    if 50 < dist_y < 120:
                        # И если игрок в соседней колонке
                        if abs(p_col - e_col) == 1:
                            await hunter_attack(enemy)
                            return

                # --- ОБЫЧНОЕ СТОЛКНОВЕНИЕ ---
                if not state["is_moving"]:
                    ptop = GAME_HEIGHT - player.bottom - PLAYER_SIZE
                    if abs(enemy.top - ptop) < 40:
                        if abs(enemy.left - player.left) < 20:
                            game_over()
                            return

                # Удаление
                if enemy.top > GAME_HEIGHT:
                    if enemy in state["enemies"]: state["enemies"].remove(enemy)
                    if enemy in game_area.controls: game_area.controls.remove(enemy)
                    state["score"] += 1
                    score_text.value = str(state["score"])
                    if state["score"] % 20 == 0: state["speed"] += 0.5

            page.update()
            await asyncio.sleep(0.02)

    # --- УПРАВЛЕНИЕ (КНОПКИ) ---
    def btn(icon, cb):
        return ft.Container(
            content=ft.Icon(icon, size=24, color="#FFFFFF88"),
            width=55, height=55,
            bgcolor="#11111188",
            border=ft.Border.all(1, "#FFFFFF22"),
            border_radius=ft.BorderRadius.all(10),
            alignment=ft.alignment.Alignment(0, 0),
            on_click=cb,
        )

    controls_layer = ft.Stack([
        # СЛЕВА
        ft.Container(
            left=15, bottom=15,
            content=ft.Column([
                btn("north_west", lambda e: move_player(-1, 1)),
                ft.Container(height=5),
                btn("south_west", lambda e: move_player(-1, -1)),
            ])
        ),
        # СПРАВА
        ft.Container(
            right=15, bottom=15,
            content=ft.Column([
                btn("north_east", lambda e: move_player(1, 1)),
                ft.Container(height=5),
                btn("south_east", lambda e: move_player(1, -1)),
            ])
        )
    ], width=GAME_WIDTH, height=GAME_HEIGHT)

    layout = ft.Container(
        content=ft.Stack([game_area, controls_layer, game_over_screen]),
        alignment=ft.alignment.Alignment(0, 0),
        bgcolor="#050505",
        width=GAME_WIDTH, height=GAME_HEIGHT,
        border=ft.Border.all(2, "#333333"),
        border_radius=ft.BorderRadius.all(15),
        clip_behavior=ft.ClipBehavior.HARD_EDGE
    )

    page.add(ft.Container(content=layout, alignment=ft.alignment.Alignment(0, 0), expand=True))
    restart_game()


if __name__ == "__main__":
    ft.run(main)
