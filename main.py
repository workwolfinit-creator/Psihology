import flet as ft
import asyncio
import random


async def main(page: ft.Page):
    # --- НАСТРОЙКИ ---
    page.title = "Neon Checkers | Clean Mode"
    page.bgcolor = "#050505"
    page.padding = 0
    page.theme_mode = "dark"
    # Отключаем скролл, чтобы экран не дергался при игре
    page.scroll = None

    GAME_WIDTH = 350
    GAME_HEIGHT = 650
    CELL_SIZE = 70
    PLAYER_SIZE = 40
    ENEMY_SIZE = 40

    state = {
        "running": False,
        "score": 0,
        "speed": 5,
        "p_x": 155,
        "p_y": 50,
        "enemies": [],
        "is_moving": False,
    }

    # --- ИНТЕРФЕЙС ---

    combo_text = ft.Text("", size=40, weight="bold", color="#FFFF00", opacity=0, animate_opacity=200)
    score_text = ft.Text("0", size=100, weight="bold", color="#FFFFFF1A", text_align="center")

    # Игрок (Яркий зеленый неон)
    player = ft.Container(
        width=PLAYER_SIZE,
        height=PLAYER_SIZE,
        bgcolor="#00FF00",
        border_radius=8,
        shadow=ft.BoxShadow(spread_radius=2, blur_radius=20, color="#00FF00"),
        left=state["p_x"],
        bottom=state["p_y"],
        animate_position=100  # Быстрая реакция
    )

    # Игровая зона
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
        state["speed"] = 5
        state["p_x"] = 155
        state["p_y"] = 50
        state["enemies"] = []
        state["is_moving"] = False

        # Сброс поля (удаляем всех старых врагов)
        game_area.controls = [score_text, combo_text, player]

        score_text.value = "0"
        player.left = 155
        player.bottom = 50
        player.bgcolor = "#00FF00"

        game_over_screen.visible = False
        page.update()
        asyncio.create_task(game_loop())

    # Экран смерти
    game_over_screen = ft.Container(
        visible=False,
        bgcolor="#E6000000",  # Темный полупрозрачный фон
        alignment=ft.alignment.Alignment(0, 0),
        content=ft.Column([
            ft.Text("GAME OVER", size=30, color="#FF0000", weight="bold"),
            ft.Text("Счет:", size=20, color="white"),
            ft.Text("0", size=50, weight="bold", color="#00FF00"),
            ft.FilledButton("ЗАНОВО", style=ft.ButtonStyle(bgcolor="#00FF00", color="black"), width=200,
                            on_click=restart_game)
        ], horizontal_alignment="center", alignment="center"),
        width=GAME_WIDTH, height=GAME_HEIGHT
    )

    # --- УМНОЕ ДВИЖЕНИЕ ---

    def handle_input(direction_x, direction_y):
        if not state["running"] or state["is_moving"]: return

        step_x = direction_x * CELL_SIZE
        step_y = direction_y * CELL_SIZE

        target_1_x = state["p_x"] + step_x
        target_1_y = state["p_y"] + step_y

        # Проверка: Враг в соседней клетке?
        enemy_in_path = check_collision_at(target_1_x, target_1_y)

        if enemy_in_path:
            # Прыжок через врага (АТАКА)
            target_2_x = state["p_x"] + (step_x * 2)
            target_2_y = state["p_y"] + (step_y * 2)

            if 0 <= target_2_x < GAME_WIDTH and 0 <= target_2_y < GAME_HEIGHT:
                asyncio.create_task(perform_attack_jump(target_2_x, target_2_y, enemy_in_path))
        else:
            # Обычный шаг
            if 0 <= target_1_x < GAME_WIDTH - PLAYER_SIZE and 0 <= target_1_y < GAME_HEIGHT - PLAYER_SIZE:
                asyncio.create_task(perform_move(target_1_x, target_1_y))

    def check_collision_at(x, bottom_y):
        target_top = GAME_HEIGHT - bottom_y - PLAYER_SIZE
        for enemy in state["enemies"]:
            if abs(enemy.top - target_top) < CELL_SIZE:
                if abs(enemy.left - x) < CELL_SIZE:
                    return enemy
        return None

    async def perform_move(x, y):
        state["is_moving"] = True
        state["p_x"] = x
        state["p_y"] = y
        player.left = x
        player.bottom = y
        page.update()
        await asyncio.sleep(0.15)
        state["is_moving"] = False

    async def perform_attack_jump(x, y, enemy_to_kill):
        state["is_moving"] = True

        # Эффект удара (Белая вспышка)
        player.bgcolor = "#FFFFFF"
        player.shadow.color = "#FFFFFF"
        player.shadow.blur_radius = 40

        state["p_x"] = x
        state["p_y"] = y
        player.left = x
        player.bottom = y
        page.update()

        # Убийство
        if enemy_to_kill in state["enemies"]:
            state["enemies"].remove(enemy_to_kill)
            if enemy_to_kill in game_area.controls:
                game_area.controls.remove(enemy_to_kill)

            state["score"] += 10
            score_text.value = str(state["score"])
            asyncio.create_task(show_combo(enemy_to_kill.left, enemy_to_kill.top))

        await asyncio.sleep(0.2)

        # Возврат цвета
        player.bgcolor = "#00FF00"
        player.shadow.color = "#00FF00"
        player.shadow.blur_radius = 20
        state["is_moving"] = False
        page.update()

    async def show_combo(x, y):
        combo_text.value = "SLASH!"
        combo_text.left = x
        combo_text.top = y
        combo_text.opacity = 1
        page.update()
        await asyncio.sleep(0.3)
        combo_text.opacity = 0
        page.update()

    def spawn_enemy():
        lanes = [15, 85, 155, 225, 295]
        lane_x = random.choice(lanes)

        enemy = ft.Container(
            width=ENEMY_SIZE,
            height=ENEMY_SIZE,
            bgcolor="#FF0044",
            border_radius=5,
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=15, color="#FF0044"),
            left=lane_x,
            top=-50,
        )
        game_area.controls.insert(1, enemy)
        state["enemies"].append(enemy)

    async def game_loop():
        spawn_timer = 0
        while state["running"]:
            # Спавн врагов
            spawn_threshold = 40 if state["score"] < 50 else 25
            spawn_timer += 1
            if spawn_timer > spawn_threshold:
                spawn_enemy()
                spawn_timer = 0

            for enemy in state["enemies"][:]:
                enemy.top += state["speed"]

                # Смерть (если игрок не в прыжке)
                if not state["is_moving"]:
                    player_top = GAME_HEIGHT - state["p_y"] - PLAYER_SIZE
                    # Проверка коллизии
                    if abs(enemy.top - player_top) < PLAYER_SIZE - 10:
                        if abs(enemy.left - state["p_x"]) < PLAYER_SIZE - 10:
                            game_over()
                            return

                # Удаление улетевших
                if enemy.top > GAME_HEIGHT:
                    if enemy in state["enemies"]: state["enemies"].remove(enemy)
                    if enemy in game_area.controls: game_area.controls.remove(enemy)
                    state["score"] += 1
                    score_text.value = str(state["score"])
                    if state["score"] % 20 == 0: state["speed"] += 0.5

            page.update()
            await asyncio.sleep(0.02)

    # --- УПРАВЛЕНИЕ (ТЕПЕРЬ ПОЛНОСТЬЮ ПРОЗРАЧНОЕ) ---

    controls_layer = ft.Column(
        controls=[
            # ВЕРХНИЙ РЯД (Прыжок/Атака по диагонали)
            ft.Row([
                ft.Container(expand=1, bgcolor="#00000000", on_click=lambda e: handle_input(-1, 1)),  # Влево-Вверх
                ft.Container(expand=1, bgcolor="#00000000", on_click=lambda e: handle_input(1, 1)),  # Вправо-Вверх
            ], expand=1, spacing=0),

            # НИЖНИЙ РЯД (Обычный шаг/Отступление)
            ft.Row([
                ft.Container(expand=1, bgcolor="#00000000", on_click=lambda e: handle_input(-1, -1)),  # Влево-Вниз
                ft.Container(expand=1, bgcolor="#00000000", on_click=lambda e: handle_input(1, -1)),  # Вправо-Вниз
            ], expand=1, spacing=0),
        ],
        spacing=0, width=GAME_WIDTH, height=GAME_HEIGHT,
    )

    layout = ft.Container(
        content=ft.Stack([game_area, game_over_screen, controls_layer]),
        alignment=ft.alignment.Alignment(0, 0),
        bgcolor="#111111",
        width=GAME_WIDTH, height=GAME_HEIGHT,
        border=ft.Border.all(2, "#333333"),
        border_radius=15,
        clip_behavior=ft.ClipBehavior.HARD_EDGE
    )

    page.add(ft.Container(content=layout, alignment=ft.alignment.Alignment(0, 0), expand=True))
    restart_game()


if __name__ == "__main__":
    ft.run(main)
