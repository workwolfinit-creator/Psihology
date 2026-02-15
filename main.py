import flet as ft
import asyncio
import random
import math

async def main(page: ft.Page):
    # --- НАСТРОЙКИ ---
    page.title = "Neon Checkers | Hunter Mode"
    page.bgcolor = "#050505"
    page.padding = 0
    page.theme_mode = "dark"
    page.scroll = None

    GAME_WIDTH = 350
    GAME_HEIGHT = 650
    COLS = [35, 105, 175, 245, 315]
    CELL_H = 70
    PLAYER_SIZE = 50

    state = {
        "running": False,
        "score": 0,
        "speed": 3.0,
        "speed_doubled": False,
        "p_col": 2,
        "p_row": 0,
        "enemies": [],
        "is_moving": False,
        "swipe_start": None,
    }

    # --- ВИЗУАЛ ---
    combo_text = ft.Text("", size=40, weight="bold", color="#FFFF00", opacity=0, animate_opacity=True)
    score_text = ft.Text("0", size=100, weight="bold", color="#FFFFFF1A", text_align="center")

    def create_checker(color, glow_color):
        return ft.Container(
            width=PLAYER_SIZE,
            height=PLAYER_SIZE,
            bgcolor=color,
            border_radius=50,
            shadow=ft.BoxShadow(spread_radius=2, blur_radius=15, color=glow_color),
            alignment=ft.Alignment(0, 0),
            content=ft.Container(
                width=PLAYER_SIZE * 0.6,
                height=PLAYER_SIZE * 0.6,
                border=ft.Border.all(3, "#80000000"),
                border_radius=50
            )
        )

    player_content = create_checker("#00FF00", "#00FF00")

    def get_pos(col, row):
        x = COLS[col] - (PLAYER_SIZE / 2)
        y = (row * CELL_H) + 20
        return x, y

    player = ft.Container(
        content=player_content,
        left=get_pos(2, 0)[0],
        bottom=get_pos(2, 0)[1],
        animate_position=True
    )

    player_highlight = ft.Container(
        width=70,
        height=70,
        bgcolor="#00FF0033",
        border_radius=15,
        opacity=0,
        animate_opacity=True
    )

    # --- ДОСКА ---
    stack_controls = []

    for r in range(9):
        for c in range(5):
            color = "#0F0F0F" if (c + r) % 2 == 0 else "#1C1C1C"
            stack_controls.append(
                ft.Container(
                    left=COLS[c] - 35,
                    bottom=r * CELL_H + 20,
                    width=70,
                    height=70,
                    bgcolor=color,
                )
            )

    stack_controls.extend([score_text, combo_text, player_highlight, player])

    game_stack = ft.Stack(controls=stack_controls, width=GAME_WIDTH, height=GAME_HEIGHT)

    # --- СВАЙП-УПРАВЛЕНИЕ ---
    def handle_pan_start(e: ft.DragStartEvent):
        state["swipe_start"] = (e.local_position.x, e.local_position.y)

    def handle_pan_end(e: ft.DragEndEvent):
        if state["swipe_start"] is None or state["is_moving"] or not state["running"]:
            return
        start_x, start_y = state["swipe_start"]
        end_x, end_y = e.local_position.x, e.local_position.y
        state["swipe_start"] = None

        dx = end_x - start_x
        dy = end_y - start_y
        threshold = 40

        if abs(dx) >= threshold and abs(dy) >= threshold:
            dir_x = 1 if dx > 0 else -1
            dir_y = 1 if dy < 0 else -1
            move_player(dir_x, dir_y)

    game_area = ft.GestureDetector(
        content=game_stack,
        on_pan_start=handle_pan_start,
        on_pan_end=handle_pan_end,
        drag_interval=10,
    )

    # --- ТРЯСКА ЭКРАНА ---
    async def shake_screen():
        shakes = [20, -30, 20, -20, 10, -10, 0]
        for offset_x in shakes:
            layout.offset = ft.Offset(offset_x / GAME_WIDTH, 0)
            layout.update()
            await asyncio.sleep(0.05)
        layout.offset = ft.Offset(0, 0)
        layout.update()

    # --- НЕОНОВАЯ ВСПЫШКА (оставлена) + НЕОНОВЫЙ СЧЁТ ОЧКОВ (вместо молний) ---
    async def flash_and_points(x, y, points):
        # Вспышка
        flash = ft.Container(
            width=100,
            height=100,
            left=x - 25,
            top=y - 25,
            bgcolor="#00FFFFFF",
            border_radius=50,
            shadow=ft.BoxShadow(blur_radius=60, spread_radius=15, color="#00FFFF"),
            opacity=0,
            scale=0.3,
            animate_opacity=True,
            animate_scale=True,
        )
        game_area.content.controls.append(flash)
        page.update()

        flash.opacity = 1
        flash.scale = 1.8
        flash.shadow = ft.BoxShadow(blur_radius=100, spread_radius=20, color="#FFFFFF")
        page.update()

        await asyncio.sleep(0.2)

        flash.opacity = 0
        flash.scale = 0.3
        page.update()

        await asyncio.sleep(0.3)
        if flash in game_area.content.controls:
            game_area.content.controls.remove(flash)
        page.update()

        # Неоновый текст очков (+10 или +20)
        points_text = ft.Text(
            f"+{points}",
            size=50,
            weight="bold",
            color="#00FF00",
            opacity=0,
            scale=0.5,
            left=x,
            top=y - 30,
            text_align="center",
            shadow=ft.BoxShadow(blur_radius=20, color="#00FF00", offset=(0, 0)),
            animate_opacity=True,
            animate_scale=True,
            animate_position=True,
        )
        game_area.content.controls.append(points_text)
        page.update()

        points_text.opacity = 1
        points_text.scale = 1.5
        points_text.top -= 60  # поднимается вверх
        page.update()

        await asyncio.sleep(0.6)

        points_text.opacity = 0
        points_text.scale = 0.5
        page.update()

        await asyncio.sleep(0.3)
        if points_text in game_area.content.controls:
            game_area.content.controls.remove(points_text)
        page.update()

    # --- ЛОГИКА ИГРЫ ---
    def game_over():
        state["running"] = False
        game_over_screen.content.controls[2].value = str(state["score"])
        game_over_screen.visible = True
        player_highlight.opacity = 0
        page.update()

    def update_player_highlight():
        c, r = state["p_col"], state["p_row"]
        player_highlight.left = COLS[c] - 35
        player_highlight.bottom = r * CELL_H + 20
        player_highlight.opacity = 0.4
        page.update()

    def get_enemy_at_grid(target_col, target_row):
        target_bottom = (target_row * CELL_H) + 20
        target_top_y = GAME_HEIGHT - target_bottom - PLAYER_SIZE
        for enemy in state["enemies"]:
            enemy_cx = enemy.left + (PLAYER_SIZE / 2)
            grid_cx = COLS[target_col]
            if abs(enemy_cx - grid_cx) < 20 and abs(enemy.top - target_top_y) < 50:
                return enemy
        return None

    async def perform_single_jump_kill(c, r, enemy, combo_text="KILL!"):
        player.content.bgcolor = "#FFFFFF"
        player.content.shadow.color = "#FFFFFF"
        player.content.shadow.blur_radius = 40
        page.update()

        state["p_col"], state["p_row"] = c, r
        player.left, player.bottom = get_pos(c, r)
        update_player_highlight()

        # Вспышка + очки
        flash_x = enemy.left + PLAYER_SIZE / 2 - 50
        flash_y = enemy.top + PLAYER_SIZE / 2 - 50
        bonus = 20 if enemy.data["tag"] == "hunter" else 10
        asyncio.create_task(flash_and_points(flash_x, flash_y, bonus))

        if enemy in state["enemies"]:
            state["enemies"].remove(enemy)
            if enemy in game_area.content.controls:
                game_area.content.controls.remove(enemy)

        state["score"] += bonus
        score_text.value = str(state["score"])

        if combo_text:
            asyncio.create_task(show_combo(enemy.left + 10, enemy.top + 10, combo_text))

        page.update()
        await asyncio.sleep(0.18)
        player.content.bgcolor = "#00FF00"
        player.content.shadow.color = "#00FF00"
        player.content.shadow.blur_radius = 15
        page.update()

    async def chain_kills(initial_c, initial_r, initial_enemy):
        if not state["running"]:
            return
        state["is_moving"] = True
        combo_count = 0
        current_c, current_r = state["p_col"], state["p_row"]
        directions = [(-1, 1), (1, 1), (-1, -1), (1, -1)]

        async def do_jump(jmp_c, jmp_r, enemy, combo_text):
            nonlocal combo_count
            combo_count += 1
            await perform_single_jump_kill(jmp_c, jmp_r, enemy, combo_text)
            extra = 10 * (combo_count - 1)
            state["score"] += extra
            score_text.value = str(state["score"])
            page.update()

            nonlocal current_c, current_r
            current_c, current_r = jmp_c, jmp_r
            state["p_col"], state["p_row"] = current_c, current_r
            update_player_highlight()

        await do_jump(initial_c, initial_r, initial_enemy, "KILL!")

        while state["running"]:
            possible = None
            for dx, dy in directions:
                mid_c = current_c + dx
                mid_r = current_r + dy
                if not (0 <= mid_c <= 4 and 0 <= mid_r <= 7):
                    continue
                enemy = get_enemy_at_grid(mid_c, mid_r)
                if enemy:
                    jmp_c = current_c + 2 * dx
                    jmp_r = current_r + 2 * dy
                    if 0 <= jmp_c <= 4 and 0 <= jmp_r <= 7:
                        possible = (jmp_c, jmp_r, enemy)
                        break
            if not possible:
                break
            jmp_c, jmp_r, enemy = possible
            await do_jump(jmp_c, jmp_r, enemy, f"{combo_count + 1}x KILL!")

        state["is_moving"] = False

    def move_player(dir_x, dir_y):
        if not state["running"] or state["is_moving"]:
            return
        cur_c, cur_r = state["p_col"], state["p_row"]
        tar_c, tar_r = cur_c + dir_x, cur_r + dir_y
        if not (0 <= tar_c <= 4 and 0 <= tar_r <= 7):
            return

        enemy = get_enemy_at_grid(tar_c, tar_r)
        if enemy:
            jmp_c, jmp_r = cur_c + dir_x * 2, cur_r + dir_y * 2
            if 0 <= jmp_c <= 4 and 0 <= jmp_r <= 7:
                asyncio.create_task(chain_kills(jmp_c, jmp_r, enemy))
            else:
                asyncio.create_task(shake_screen())
        else:
            asyncio.create_task(perform_step(tar_c, tar_r))

    async def perform_step(c, r):
        state["is_moving"] = True
        state["p_col"], state["p_row"] = c, r
        player.left, player.bottom = get_pos(c, r)
        update_player_highlight()
        page.update()
        await asyncio.sleep(0.1)
        state["is_moving"] = False

    async def show_combo(x, y, text):
        combo_text.value = text
        combo_text.left = x
        combo_text.top = y
        combo_text.opacity = 1
        page.update()
        await asyncio.sleep(0.4)
        combo_text.opacity = 0
        page.update()

    async def hunter_attack(enemy):
        enemy.content.bgcolor = "#FFFFFF"
        enemy.update()
        enemy.top = GAME_HEIGHT - player.bottom - PLAYER_SIZE
        enemy.left = player.left
        page.update()
        await asyncio.sleep(0.1)
        game_over()

    def spawn_enemy():
        is_hunter = random.random() < 0.35
        col = random.randint(0, 4)
        color = "#FF8800" if is_hunter else "#FF0044"
        tag = "hunter" if is_hunter else "normal"

        enemy = ft.Container(
            content=create_checker(color, color),
            left=COLS[col] - (PLAYER_SIZE / 2),
            top=-60,
            data={"col": col, "tag": tag}
        )
        game_area.content.controls.insert(-1, enemy)
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
                enemy.top += state["speed"]

                if enemy.data["tag"] == "hunter" and not state["is_moving"]:
                    p_top_y = GAME_HEIGHT - player.bottom - PLAYER_SIZE
                    dist_y = p_top_y - enemy.top
                    if 50 < dist_y < 120 and abs(state["p_col"] - enemy.data["col"]) == 1:
                        await hunter_attack(enemy)
                        return

                if not state["is_moving"]:
                    ptop = GAME_HEIGHT - player.bottom - PLAYER_SIZE
                    if abs(enemy.top - ptop) < 40 and abs(enemy.left - player.left) < 20:
                        game_over()
                        return

                if enemy.top > GAME_HEIGHT:
                    state["enemies"].remove(enemy)
                    if enemy in game_area.content.controls:
                        game_area.content.controls.remove(enemy)
                    state["score"] += 1
                    score_text.value = str(state["score"])

                    if state["score"] >= 50 and not state["speed_doubled"]:
                        state["speed"] *= 2
                        state["speed_doubled"] = True

            page.update()
            await asyncio.sleep(0.02)

    def restart_game(e=None):
        state["running"] = True
        state["score"] = 0
        state["speed"] = 3.0
        state["speed_doubled"] = False
        state["p_col"] = 2
        state["p_row"] = 0
        state["is_moving"] = False
        state["swipe_start"] = None

        for enemy in state["enemies"][:]:
            if enemy in game_area.content.controls:
                game_area.content.controls.remove(enemy)
        state["enemies"].clear()

        score_text.value = "0"
        player.left, player.bottom = get_pos(2, 0)
        player.content.bgcolor = "#00FF00"
        player.content.shadow.color = "#00FF00"
        player.content.shadow.blur_radius = 15

        update_player_highlight()
        game_over_screen.visible = False
        page.update()
        asyncio.create_task(game_loop())

    game_over_screen = ft.Container(
        visible=False,
        bgcolor="#E6000000",
        alignment=ft.Alignment(0, 0),
        content=ft.Column([
            ft.Text("GAME OVER", size=26, color="#FF0000", weight="bold"),
            ft.Text("Счет:", size=20, color="white"),
            ft.Text("0", size=50, weight="bold", color="#00FF00"),
            ft.FilledButton("ЗАНОВО", style=ft.ButtonStyle(bgcolor="#00FF00", color="black"), width=200, on_click=restart_game)
        ], horizontal_alignment="center", alignment=ft.MainAxisAlignment.CENTER),
        width=GAME_WIDTH,
        height=GAME_HEIGHT
    )

    layout = ft.Container(
        content=ft.Stack([game_area, game_over_screen]),
        alignment=ft.Alignment(0, 0),
        bgcolor="#050505",
        width=GAME_WIDTH,
        height=GAME_HEIGHT,
        border=ft.Border.all(2, "#333333"),
        border_radius=15,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        offset=ft.Offset(0, 0),
        animate_offset=True,
    )

    page.add(ft.Container(content=layout, alignment=ft.Alignment(0, 0), expand=True))

    restart_game()

if __name__ == "__main__":
    ft.run(main)
