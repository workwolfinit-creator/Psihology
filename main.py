import flet as ft
import asyncio
import random
import os
from functools import partial

# --- ЖЕЛЕЗОБЕТОННЫЙ ПУТЬ К ПАПКЕ ASSETS ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(SCRIPT_DIR, "assets")

async def main(page: ft.Page):
    # --- НАСТРОЙКИ ОКНА ---
    page.title = "PsychoTuner | Метод Люшера"
    page.bgcolor = "#0A0A0A"
    page.theme_mode = "dark"
    page.padding = 10  # Уменьшили отступы для телефона
    # Включаем прокрутку ВСЕГО приложения (спасение для маленьких экранов)
    page.scroll = "auto" 
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"
    
    page.update()

    colors_data = [
        {"id": 1, "hex": "#003399"}, 
        {"id": 2, "hex": "#006633"}, 
        {"id": 3, "hex": "#E50000"}, 
        {"id": 4, "hex": "#FFCC00"}, 
        {"id": 5, "hex": "#660099"}, 
        {"id": 6, "hex": "#996633"}, 
        {"id": 7, "hex": "#000000"}, 
        {"id": 0, "hex": "#808080"} 
    ]

    interpretations = {
        1: "Потребность в глубоком покое, эмоциональном комфорте.",
        2: "Стремление к самоутверждению, контроль ситуации.",
        3: "Жажда жизни, стремление к успеху, активность.",
        4: "Оптимизм, потребность в перспективе и свободе.",
        5: "Эмоциональная восприимчивость, мир фантазий.",
        6: "Потребность в физическом комфорте и безопасности.",
        7: "Протест против текущей ситуации, негативизм.",
        0: "Желание отгородиться от влияний, 'уйти в тень'."
    }

    relax_tips = [
        "• Глубокий вдох носом (4 сек) — медленный выдох ртом.",
        "• Опустите плечи вниз и расслабьте челюсть.",
        "• Сожмите кулаки на 5 сек, затем резко расслабьте.",
        "• Дышите животом: рука на животе должна подниматься.",
        "• Медленно считайте до 10, представляя цифры."
    ]

    def generate_recommendations(anxiety, vk_score, risks):
        recs = []
        if vk_score < 0.51:
            recs.append({
                "text": "⚡ ЭНЕРГИЯ (Истощение)\nНужно восстановление.\n• Информационный детокс перед сном.\n• Сон 8–9 часов.\n• Йога-нидра вместо кардио.",
                "audio_url": "spotify:track:LINK1"
            })
        elif vk_score > 1.9:
            recs.append({
                "text": "⚡ ЭНЕРГИЯ (Перевозбуждение)\nСимпатика перегружена.\n• Исключить кофеин.\n• Дыхание «по квадрату» (4-4-4-4).",
                "audio_url": "spotify:track:LINK2"
            })
        else:
            recs.append({
                "text": "⚡ ЭНЕРГИЯ: Баланс в норме\nПоддерживайте текущий режим.",
                "audio_url": "spotify:track:LINK3"
            })

        if anxiety >= 3:
            recs.append({
                "text": "🧠 ТРЕВОЖНОСТЬ (Высокая)\n• Техника заземления 5-4-3-2-1.\n• Снизьте требования к себе на пару дней.",
                "audio_url": "spotify:track:LINK4"
            })
        elif anxiety > 0:
            recs.append({
                "text": "🧠 ТРЕВОЖНОСТЬ (Фоновая)\n• Прогулки, уборка (физика).\n• Дыхание 4-7-8.",
                "audio_url": "spotify:track:LINK5"
            })

        if risks and "не выявлено" not in risks[0]:
            recs.append({
                "text": "🩺 ТЕЛО\n• Прогрессивная релаксация.\n• Самомассаж шеи.",
                "audio_url": "spotify:track:LINK6"
            })
        return recs

    def calculate_metrics(t2_choice):
        anxiety = 0
        for basic_color in [1, 2, 3, 4]:
            pos = t2_choice.index(basic_color) + 1
            if pos == 6: anxiety += 1
            elif pos == 7: anxiety += 2
            elif pos == 8: anxiety += 3
        
        compensation = 0
        if anxiety > 0:
            for extra_color in [0, 6, 7]:
                pos = t2_choice.index(extra_color) + 1
                if pos == 3: compensation += 1
                elif pos == 2: compensation += 2
                elif pos == 1: compensation += 3
        
        norm = [3, 4, 2, 5, 1, 6, 0, 7]
        so_score = sum(abs((t2_choice.index(c) + 1) - (norm.index(c) + 1)) for c in [item["id"] for item in colors_data])
        so_text = "Норма" if so_score <= 10 else "Стресс"
        
        p3, p4 = t2_choice.index(3) + 1, t2_choice.index(4) + 1
        p1, p2 = t2_choice.index(1) + 1, t2_choice.index(2) + 1
        vk_score = round((18 - (p3 + p4)) / (18 - (p1 + p2)), 2)
        vk_text = "Норма"
        if vk_score < 0.51: vk_text = "Истощение"
        elif vk_score > 1.9: vk_text = "Перевозбуждение"
        
        risks = []
        if (t2_choice.index(3)+1) <= 3 and (t2_choice.index(2)+1) <= 3: risks.append("Риск гипертонии")
        if not risks: risks.append("Рисков не выявлено")
            
        return anxiety, compensation, so_score, so_text, vk_score, vk_text, risks

    def show_paid_report(t2_choice):
        page.controls.clear()
        anxiety, _, _, _, vk_score, _, risks = calculate_metrics(t2_choice)
        recommendations = generate_recommendations(anxiety, vk_score, risks)

        title = ft.Text("План Восстановления", size=24, weight="bold", color="#00FFFF", text_align="center")
        recs_ui = ft.Column(spacing=15, scroll="auto") # Тут скролл уже был, ок

        for rec in recommendations:
            recs_ui.controls.append(ft.Container(
                content=ft.Column([
                    ft.Text(rec["text"], size=15, color="#E0E0E0"),
                    ft.ElevatedButton("🎧 Spotify", style=ft.ButtonStyle(bgcolor="#1DB954", color="white"), on_click=lambda _, u=rec["audio_url"]: page.launch_url(u))
                ]),
                bgcolor="#2A2A2A", padding=15, border_radius=10
            ))

        page.add(ft.Container(
            content=ft.Column([title, ft.Container(height=20), recs_ui, ft.Container(height=40), 
                             ft.ElevatedButton("ЗАВЕРШИТЬ", on_click=lambda _: show_intro())], 
                             horizontal_alignment="center", scroll="auto"), # Добавил скролл
            bgcolor="#1A1A1A", padding=20, border_radius=20, width=380
        ))
        page.update()

    def show_clinical_metrics_and_paywall(t1_choice, t2_choice):
        page.controls.clear()
        anxiety, compensation, so_score, so_text, vk_score, vk_text, risks = calculate_metrics(t2_choice)
        
        results_col = ft.Column([
            ft.Text(f"Тревожность: {anxiety}", size=14),
            ft.Text(f"Вегетативный баланс: {vk_score}", size=14),
            ft.Text(f"Риски: {risks[0]}", size=14, color="red" if "Риск" in risks[0] else "green"),
        ], spacing=5)
        
        page.add(ft.Container(
            content=ft.Column([
                ft.Text("Клинический Анализ", size=22, weight="bold", color="#00FFFF"),
                ft.Container(height=15),
                results_col,
                ft.Container(height=30),
                ft.Text("🔓 Полный протокол", size=18, weight="bold"),
                ft.ElevatedButton("ОПЛАТИТЬ РАЗБОР", style=ft.ButtonStyle(bgcolor="#0088cc", color="white"), width=280, on_click=lambda _: page.launch_url("https://t.me/YOUR_BOT")),
                ft.TextButton("Пропустить оплату", on_click=lambda _: show_paid_report(t2_choice))
            ], horizontal_alignment="center", scroll="auto"), # Добавил скролл
            bgcolor="#1A1A1A", padding=20, border_radius=20, width=380
        ))
        page.update()

    def show_test_t2(t1_choice):
        page.controls.clear()
        t2_choice = []
        
        def color_clicked(e, cid, btn):
            t2_choice.append(cid)
            btn.visible = False
            page.update()
            if len(t2_choice) == 8: show_clinical_metrics_and_paywall(t1_choice, t2_choice)
        
        shuffled = colors_data[:]
        random.shuffle(shuffled)
        grid = ft.Row(wrap=True, width=260, spacing=10)
        for c in shuffled:
            btn = ft.Container(bgcolor=c["hex"], width=80, height=80, border_radius=15) # Чуть меньше кнопки
            btn.on_click = partial(color_clicked, cid=c["id"], btn=btn)
            grid.controls.append(btn)
            
        page.add(ft.Container(content=ft.Column([ft.Text("ВТОРОЙ ЭТАП", size=18), ft.Container(height=20), grid], horizontal_alignment="center", scroll="auto"), bgcolor="#1A1A1A", padding=20, border_radius=20, width=380))
        page.update()

    def show_t1_result(t1_choice):
        page.controls.clear()
        
        countdown = ft.Text("120", size=40, color="#00FFFF")
        btn_next = ft.ElevatedButton("ПРОДОЛЖИТЬ (ЭТАП 2)", visible=False, 
                                     style=ft.ButtonStyle(bgcolor="#1565C0", color="white"),
                                     on_click=lambda _: show_test_t2(t1_choice))
        
        # --- ИСПРАВЛЕНИЕ ЗДЕСЬ: Добавил scroll="auto" ---
        page.add(ft.Container(content=ft.Column([
            ft.Text("Текущее состояние", size=20, weight="bold"),
            ft.Container(height=10),
            ft.Text(f"1. {interpretations[t1_choice[0]]}", size=14),
            ft.Text(f"2. {interpretations[t1_choice[1]]}", size=14),
            ft.Container(height=20),
            
            # Блок паузы
            ft.Container(
                content=ft.Column([
                    ft.Text("Пауза 2 минуты", size=18, weight="bold", color="#00FFFF"),
                    ft.Text("Отвлекитесь и расслабьтесь:", size=13, color="grey"),
                    ft.Text(random.choice(relax_tips), size=14, text_align="center"),
                    ft.Container(height=10),
                    countdown,
                    ft.Container(height=10),
                    btn_next
                ], horizontal_alignment="center"),
                bgcolor="#262626", padding=20, border_radius=15
            )
        ], horizontal_alignment="center", scroll="auto"), # <-- ВОТ ЭТО СПАСЕТ СИТУАЦИЮ
        bgcolor="#1A1A1A", padding=20, border_radius=20, width=380))
        
        page.update()
        
        async def timer():
            for i in range(120, 0, -1):
                countdown.value = str(i)
                page.update()
                await asyncio.sleep(1) 
            btn_next.visible = True
            page.update()
        
        asyncio.create_task(timer())

    def show_test_t1():
        page.controls.clear()
        t1_choice = []
        
        def color_clicked(e, cid, btn):
            t1_choice.append(cid)
            btn.visible = False
            page.update()
            if len(t1_choice) == 8: show_t1_result(t1_choice)
        
        shuffled = colors_data[:]
        random.shuffle(shuffled)
        grid = ft.Row(wrap=True, width=260, spacing=10)
        for c in shuffled:
            btn = ft.Container(bgcolor=c["hex"], width=80, height=80, border_radius=15)
            btn.on_click = partial(color_clicked, cid=c["id"], btn=btn)
            grid.controls.append(btn)
            
        page.add(ft.Container(content=ft.Column([ft.Text("ЭТАП 1", size=18), ft.Container(height=20), grid], horizontal_alignment="center", scroll="auto"), bgcolor="#1A1A1A", padding=20, border_radius=20, width=380))
        page.update()

    def show_instructions():
        page.controls.clear()
        page.add(ft.Container(
            content=ft.Column([
                ft.Text("Инструкция", size=24, weight="bold"),
                ft.Text("1. Выберите приятный цвет.\n2. Не ассоциируйте с одеждой."),
                ft.Container(height=20),
                ft.ElevatedButton("НАЧАТЬ ТЕСТ", on_click=lambda _: show_test_t1())
            ], horizontal_alignment="center", scroll="auto"), bgcolor="#1A1A1A", padding=40, border_radius=20, width=380
        ))
        page.update()

    def show_intro():
        page.controls.clear()
        strips = ft.Row([ft.Container(bgcolor=c["hex"], width=30, height=5) for c in colors_data], alignment="center")
        page.add(ft.Container(
            content=ft.Column([
                strips,
                ft.Text("Цветовая Диагностика", size=24, weight="bold"),
                ft.Text("Метод Макса Люшера", color="grey"),
                ft.Container(height=20),
                ft.ElevatedButton("НАЧАТЬ", on_click=lambda _: show_instructions())
            ], horizontal_alignment="center", scroll="auto"), bgcolor="#1A1A1A", padding=40, border_radius=20, width=380
        ))
        page.update()

    # --- ЗАСТАВКА ---
    async def show_splash():
        page.controls.clear()
        
        intro_gif = ft.Image(
            src="intro.gif", 
            width=350,
            height=350,
            fit="contain",
            error_content=ft.Text("Ошибка загрузки intro.gif", color="red")
        )
        
        page.add(ft.Container(
            content=ft.Column([
                intro_gif,
                ft.Text("N O X A E   L A B", size=24, weight="bold", color="#B266FF")
            ], alignment="center", horizontal_alignment="center"),
            bgcolor="#0A0A0A",
            expand=True,
            alignment=ft.alignment.Alignment(0, 0)
        ))
        page.update()
        
        await asyncio.sleep(6.5)
        show_intro()

    # ЗАПУСК
    await show_splash()

if __name__ == "__main__":
    print(f"✅ Запуск из папки: {ASSETS_DIR}")
    ft.run(main, assets_dir=ASSETS_DIR)
