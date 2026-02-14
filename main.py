import flet as ft
import asyncio
import random


async def main(page: ft.Page):
    # --- НАСТРОЙКИ ---
    page.title = "Neon Checkers | Fixed Button"
    page.bgcolor = "#101010"
    page.padding = 0
    page.theme_mode = "dark"
    page.scroll = None

    GAME_WIDTH = 350
    GAME_HEIGHT = 650
    CELL_SIZE = 70
    PLAYER_SIZE = 50
    ENEMY_SIZE = 50

    # Координаты 5 полос (Центры)
    LANES = [10, 80, 150, 220, 290]

    # Состояние
    state = {
        "running": False,
        "score": 0,
        "speed": 4,
        "lane_idx": 2,  # Игрок начинает в центре
        "p_y": 50,
        "enemies": [],
        "is_moving": False,
    }

    # --- ВИЗУАЛ ---
    combo_text = ft.Text("", size=40, weight="bold", color="#FFFF00", opacity=0, animate_opacity=200)
    score_text = ft.Text("0", size=100, weight="bold", color="#FFFFFF1A", text_align="center")

    def create_checker_shape(color, glow_color):
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

    player_content = create_checker_shape("#FFFFFF", "#FFFFFF")

    player = ft.Container(
        content=player_content,
        left=LANES[state["lane_idx"]],
        bottom=state["p_y"],
        animate_position=150
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
        state["speed"] = 4
        state["lane_idx"] = 2
        state["p_y"] = 50
        state["enemies"] = []
        state["is_moving"] = False

        # Сброс врагов и игрока
        game_area.controls = [score_text, combo_text, player]
        score_text.value = "0"
        player.left = LANES[2]
        player.bottom = 50
        player.content.bgcolor = "#FFFFFF"
        player.content.shadow.color = "#FFFFFF"

        game_over_screen.visible = False
        page.update()
        asyncio.create_task(game_loop())

    game_over_screen = ft.Container(
        visible=False,
        bgcolor="#E6000000",
        alignment=ft.alignment.Alignment(0, 0),
        content=ft.Column([
            ft.Text("ПАРТИЯ ОКОНЧЕНА", size=26, color="#FF0000", weight="bold"),
            ft.Text("Счет:", size=20, color="white"),
            ft.Text("0", size=50, weight="bold", color="#00FF00"),
            ft.FilledButton("НОВАЯ ИГРА", style=ft.ButtonStyle(bgcolor="#FFFFFF", color="black"), width=200,
                            on_click=restart_game)
        ], horizontal_alignment="center", alignment=ft.MainAxisAlignment.CENTER),
        width=GAME_WIDTH, height=GAME_HEIGHT
    )

    # --- ОБРАБОТКА ВХОДА (МАТРИЦА) ---
    def handle_matrix_click(e, target_lane_idx, is_top_row):
        if not state["running"] or state["is_moving"]: return

        current_lane = state["lane_idx"]

        dir_x = 0
        if target_lane_idx > current_lane:
            dir_x = 1  # Вправо
        elif target_lane_idx < current_lane:
            dir_x = -1  # Влево

        dir_y = -1  # По умолчанию вниз/обычный шаг
        if is_top_row: dir_y = 1  # Атака вверх

        if dir_x == 0: return  # Нажатие в ту же колонку

        handle_move_logic(dir_x, dir_y)

    def handle_move_logic(direction_x, direction_y):
        current_x = LANES[state["lane_idx"]]
        current_y = state["p_y"]

        step_x = direction_x * CELL_SIZE
        step_y = direction_y * CELL_SIZE

        target_1_x = current_x + step_x
        target_1_y = current_y + step_y

        enemy_in_path = check_collision_at(target_1_x, target_1_y)

        if enemy_in_path:
            # АТАКА (x2)
            target_2_x = current_x + (step_x * 2)
            target_2_y = current_y + (step_y * 2)

            new_lane_idx = state["lane_idx"] + (direction_x * 2)

            if 0 <= new_lane_idx <= 4 and 0 <= target_2_y < GAME_HEIGHT:
                asyncio.create_task(perform_attack_jump(new_lane_idx, target_2_y, enemy_in_path))
        else:
            # ОБЫЧНЫЙ ХОД
            new_lane_idx = state["lane_idx"] + direction_x
            if 0 <= new_lane_idx <= 4 and 0 <= target_1_y < GAME_HEIGHT - PLAYER_SIZE:
                asyncio.create_task(perform_move(new_lane_idx, target_1_y))

    def check_collision_at(x, bottom_y):
        target_top = GAME_HEIGHT - bottom_y - PLAYER_SIZE
        for enemy in state["enemies"]:
            if abs(enemy.top - target_top) < CELL_SIZE * 0.8:
                if abs(enemy.left - x) < CELL_SIZE * 0.8:
                    return enemy
        return None

    async def perform_move(new_lane_idx, y):
        state["is_moving"] = True
        state["lane_idx"] = new_lane_idx
        state["p_y"] = y
        player.left = LANES[new_lane_idx]
        player.bottom = y
        page.update()
        await asyncio.sleep(0.15)
        state["is_moving"] = False

    async def perform_attack_jump(new_lane_idx, y, enemy_to_kill):
        state["is_moving"] = True
        player.content.bgcolor = "#FFD700"
        player.content.shadow.color = "#FFD700"
        player.content.shadow.blur_radius = 40

        state["lane_idx"] = new_lane_idx
        state["p_y"] = y
        player.left = LANES[new_lane_idx]
        player.bottom = y
        page.update()

        if enemy_to_kill in state["enemies"]:
            state["enemies"].remove(enemy_to_kill)
            if enemy_to_kill in game_area.controls:
                game_area.controls.remove(enemy_to_kill)
            state["score"] += 10
            score_text.value = str(state["score"])
            asyncio.create_task(show_combo(enemy_to_kill.left, enemy_to_kill.top))

        await asyncio.sleep(0.2)
        player.content.bgcolor = "#FFFFFF"
        player.content.shadow.color = "#FFFFFF"
        player.content.shadow.blur_radius = 15
        state["is_moving"] = False
        page.update()

    async def show_combo(x, y):
        combo_text.value = "+10"
        combo_text.left = x
        combo_text.top = y
        combo_text.opacity = 1
        page.update()
        await asyncio.sleep(0.3)
        combo_text.opacity = 0
        page.update()

    def spawn_enemy():
        lane_idx = random.randint(0, 4)
        lane_x = LANES[lane_idx]
        enemy_content = create_checker_shape("#FF0044", "#FF0044")
        enemy = ft.Container(
            content=enemy_content,
            left=lane_x,
            top=-60,
        )
        game_area.controls.insert(1, enemy)
        state["enemies"].append(enemy)

    async def game_loop():
        spawn_timer = 0
        while state["running"]:
            spawn_threshold = 50 if state["score"] < 50 else 30
            spawn_timer += 1
            if spawn_timer > spawn_threshold:
                spawn_enemy()
                spawn_timer = 0

            for enemy in state["enemies"][:]:
                enemy.top += state["speed"]
                if not state["is_moving"]:
                    player_top = GAME_HEIGHT - state["p_y"] - PLAYER_SIZE
                    current_player_x = LANES[state["lane_idx"]]

                    if abs(enemy.top - player_top) < PLAYER_SIZE * 0.8:
                        if abs(enemy.left - current_player_x) < PLAYER_SIZE * 0.8:
                            game_over()
                            return
                if enemy.top > GAME_HEIGHT:
                    if enemy in state["enemies"]: state["enemies"].remove(enemy)
                    if enemy in game_area.controls: game_area.controls.remove(enemy)
                    state["score"] += 1
                    score_text.value = str(state["score"])
                    if state["score"] % 20 == 0: state["speed"] += 0.5

            page.update()
            await asyncio.sleep(0.02)

    # --- СЕТКА УПРАВЛЕНИЯ ---

    grid_controls = ft.Column(spacing=0, width=GAME_WIDTH, height=GAME_HEIGHT)

    # Генерация сетки кнопок
    # Важно: используем lambda e, idx=i: ... чтобы захватить значение переменной

    # 1. Верхний ряд
    row_top = ft.Row(spacing=0, expand=1)
    for i in range(5):
        btn = ft.Container(expand=1, bgcolor="#00000000", on_click=lambda e, idx=i: handle_matrix_click(e, idx, True))
        row_top.controls.append(btn)

    # 2. Средний ряд
    row_mid = ft.Row(spacing=0, expand=1)
    for i in range(5):
        btn = ft.Container(expand=1, bgcolor="#00000000", on_click=lambda e, idx=i: handle_matrix_click(e, idx, False))
        row_mid.controls.append(btn)

    # 3. Нижний ряд
    row_bot = ft.Row(spacing=0, expand=1)
    for i in range(5):
        btn = ft.Container(expand=1, bgcolor="#00000000", on_click=lambda e, idx=i: handle_matrix_click(e, idx, False))
        row_bot.controls.append(btn)

    grid_controls.controls.extend([row_top, row_mid, row_bot])

    # --- СБОРКА СЦЕНЫ (ИСПРАВЛЕН ПОРЯДОК СЛОЕВ) ---

    # БЫЛО: [game_area, game_over_screen, grid_controls] -> Кнопка не нажималась
    # СТАЛО: [game_area, grid_controls, game_over_screen] -> Экран смерти ПОВЕРХ всего

    layout = ft.Container(
        content=ft.Stack([game_area, grid_controls, game_over_screen]),
        alignment=ft.alignment.Alignment(0, 0),
        bgcolor="#151515",
        width=GAME_WIDTH, height=GAME_HEIGHT,
        border=ft.Border.all(4, "#333333"),
        border_radius=ft.BorderRadius.all(15),
        clip_behavior=ft.ClipBehavior.HARD_EDGE
    )

    page.add(ft.Container(content=layout, alignment=ft.alignment.Alignment(0, 0), expand=True))
    restart_game()


if __name__ == "__main__":
    ft.run(main)
