import flet as ft
import asyncio
import random
import os
from functools import partial

# --- ПРАВИЛЬНЫЙ ПУТЬ К ПАПКЕ ASSETS ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(SCRIPT_DIR, "assets")

async def main(page: ft.Page):
    # --- НАСТРОЙКИ ОКНА ---
    page.title = "PsychoTuner | Метод Люшера"
    page.bgcolor = "#0A0A0A"
    page.theme_mode = "dark"
    page.padding = 10
    
    # ВАЖНО: Сначала прокрутка выключена, чтобы заставка была по центру!
    page.scroll = None 
    
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
        1: "Потребность в глубоком покое, эмоциональном комфорте, гармонии и человеческом понимании.",
        2: "Стремление к самоутверждению, упорство, желание контролировать ситуацию и обладать властью.",
        3: "Жажда жизни, стремление к успеху, активная деятельность, желание испытывать сильные эмоции.",
        4: "Оптимизм, потребность в перспективе, свободе, новизне и надежда на лучшее будущее.",
        5: "Поиск слияния противоположностей, повышенная эмоциональная восприимчивость, погружение в мир фантазий.",
        6: "Потребность в физическом комфорте, отдыхе, безопасности и чувственных наслаждениях.",
        7: "Протест против текущей ситуации, негативизм, желание разрушить ограничения, агрессия.",
        0: "Желание отгородиться от внешних влияний, 'уйти в тень', скрыть свои чувства, усталость."
    }

    relax_tips = [
        "• Закройте глаза и сделайте 5 глубоких вдохов через нос, медленных выдохов через рот.\n• Расслабьте плечи — опустите их вниз.\n• Почувствуйте, как напряжение уходит из тела.",
        "• Представьте спокойное место: лес, море или уютную комнату.\n• Погрузитесь в детали этой картинки на минуту.\n• Это быстро снижает уровень стресса.",
        "• Сожмите кулаки сильно на 5 секунд, затем полностью расслабьте.\n• Повторите с плечами, лицом и ногами.\n• Быстрый сброс мышечного напряжения.",
        "• Положите руку на живот и дышите так, чтобы поднимался живот, а не грудь.\n• Это активирует парасимпатическую систему и успокаивает.",
        "• Медленно посчитайте до 10, фокусируясь только на цифрах.\n• Если приходят мысли — мягко возвращайтесь к счёту."
    ]

    def generate_recommendations(anxiety, vk_score, risks):
        recs = []
        if vk_score < 0.51:
            recs.append({
                "text": "⚡ ЭНЕРГИЯ (Истощение)\nОрганизм работает на резервах. Нужно восстановление.\n\n"
                        "• Информационный детокс: за 1.5 часа до сна — без экранов.\n"
                        "• Увеличьте сон до 8–9 часов.\n"
                        "• Замените кардио на йогу-нидру или лёгкую растяжку.\n"
                        "• Добавьте продукты с магнием: орехи, бананы, тёмный шоколад.\n"
                        "• Короткий дневной сон 20–30 минут.",
                "audio_url": "spotify:track:LINK1"
            })
        elif vk_score > 1.9:
            recs.append({
                "text": "⚡ ЭНЕРГИЯ (Перевозбуждение)\nСимпатическая система перегружена.\n\n"
                        "• Ограничьте кофеин и энергетики.\n"
                        "• Дыхание «по квадрату»: вдох 4 сек → задержка 4 сек → выдох 4 сек → задержка 4 сек.\n"
                        "• Заземляющие прогулки без телефона 20–30 минут.\n"
                        "• Техника 4-7-8 для быстрого сброса адреналина.\n"
                        "• Контрастный душ.",
                "audio_url": "spotify:track:LINK2"
            })
        else:
            recs.append({
                "text": "⚡ ЭНЕРГИЯ: Оптимальный баланс\n"
                        "Поддерживайте текущий режим: полноценный сон, умеренная активность.",
                "audio_url": "spotify:track:LINK3"
            })

        if anxiety >= 3:
            recs.append({
                "text": "🧠 ТРЕВОЖНОСТЬ (Высокая)\nВы тратите много ресурсов на компенсацию стресса.\n\n"
                        "• Техника заземления 5-4-3-2-1 (5 вещей вижу, 4 трогаю, 3 слышу...).\n"
                        "• Снизьте планку ожиданий от себя на ближайшие дни.\n"
                        "• Ведение дневника эмоций: выписывайте тревожные мысли на бумагу.",
                "audio_url": "spotify:track:LINK4"
            })
        elif anxiety > 0:
            recs.append({
                "text": "🧠 ТРЕВОЖНОСТЬ (Фоновая)\nЕсть внутреннее напряжение.\n\n"
                        "• Рутинная физическая активность: уборка, прогулка, плавание.\n"
                        "• Хобби «ради процесса», а не результата.\n"
                        "• Дыхание 4-7-8 перед сном.",
                "audio_url": "spotify:track:LINK5"
            })

        if risks and "не выявлено" not in risks[0]:
            recs.append({
                "text": "🩺 ТЕЛО (Психосоматика)\nСтресс начинает проявляться в теле.\n\n"
                        "• Прогрессивная релаксация по Джекобсону.\n"
                        "• Самомассаж шейно-воротниковой зоны.\n"
                        "• Тёплая ванна с солью Эпсома.",
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
        
        if so_score <= 10: so_text = "Высокая устойчивость, отсутствие стресса."
        elif so_score <= 19: so_text = "Умеренная непродуктивность, рабочее напряжение."
        elif so_score <= 30: so_text = "Выраженный дистресс, дезадаптация."
        else: so_text = "Критическое состояние, срыв механизмов адаптации."
        
        p3, p4 = t2_choice.index(3) + 1, t2_choice.index(4) + 1
        p1, p2 = t2_choice.index(1) + 1, t2_choice.index(2) + 1
        vk_score = round((18 - (p3 + p4)) / (18 - (p1 + p2)), 2)
        
        if vk_score < 0.51: vk_text = "Истощение, пассивность (трофотропный тонус)."
        elif vk_score <= 0.91: vk_text = "Оптимальный режим (уклон в сохранение сил)."
        elif vk_score <= 1.9: vk_text = "Оптимальный режим (эрготропный тонус, активность)."
        else: vk_text = "Перевозбуждение, гиперактивность, тревога."
        
        risks = []
        if (t2_choice.index(3)+1) <= 3 and (t2_choice.index(2)+1) <= 3: risks.append("Высокий риск гипертонии (перенапряжение).")
        if (t2_choice.index(1)+1) >= 6 and (t2_choice.index(2)+1) <= 3: risks.append("Риск проблем ЖКТ / язвенной болезни.")
        if not risks: risks.append("Специфических психосоматических рисков не выявлено.")
            
        return anxiety, compensation, so_score, so_text, vk_score, vk_text, risks

    def show_paid_report(t2_choice):
        page.controls.clear()
        # ВКЛЮЧАЕМ прокрутку, так как тут много текста
        page.scroll = "auto"
        page.update()
        
        anxiety, _, _, _, vk_score, _, risks = calculate_metrics(t2_choice)
        recommendations = generate_recommendations(anxiety, vk_score, risks)

        title = ft.Text("План Восстановления", size=24, weight="bold", color="#00FFFF", text_align="center")
        recs_ui = ft.Column(spacing=15)

        for rec in recommendations:
            recs_ui.controls.append(ft.Container(
                content=ft.Column([
                    ft.Text(rec["text"], size=15, color="#E0E0E0"),
                    ft.ElevatedButton("🎧 Слушать в Spotify", style=ft.ButtonStyle(bgcolor="#1DB954", color="white"), on_click=lambda _, u=rec["audio_url"]: page.launch_url(u))
                ]),
                bgcolor="#2A2A2A", padding=15, border_radius=10
            ))

        page.add(ft.Container(
            content=ft.Column([title, ft.Container(height=20), recs_ui, ft.Container(height=40), 
                             ft.ElevatedButton("ЗАВЕРШИТЬ", on_click=lambda _: show_intro())], 
                             horizontal_alignment="center"), 
            bgcolor="#1A1A1A", padding=20, border_radius=20, width=380
        ))
        page.update()

    def show_clinical_metrics_and_paywall(t1_choice, t2_choice):
        page.controls.clear()
        page.scroll = "auto" # Включаем скролл
        page.update()
        
        anxiety, compensation, so_score, so_text, vk_score, vk_text, risks = calculate_metrics(t2_choice)
        
        results_col = ft.Column([
            ft.Text(f"Тревожность (A): {anxiety}", size=14),
            ft.Text(f"Компенсация (C): {compensation}", size=14),
            ft.Text(f"СО: {so_score} ({so_text})", size=14),
            ft.Text(f"Вегетативный баланс: {vk_score}", size=14),
            ft.Text(f"{vk_text}", size=13, color="grey"),
            ft.Text(f"Риски: {risks[0]}", size=14, color="red" if "Риск" in risks[0] else "green"),
        ], spacing=5)
        
        page.add(ft.Container(
            content=ft.Column([
                ft.Text("Клинический Анализ", size=22, weight="bold", color="#00FFFF"),
                ft.Container(height=15),
                results_col,
                ft.Container(height=30),
                ft.Text("🔓 Полный протокол", size=18, weight="bold"),
                ft.Text("Персональные практики для выравнивания показателей.", size=13, color="#A0A0A0", text_align="center"),
                ft.ElevatedButton("ОПЛАТИТЬ РАЗБОР", style=ft.ButtonStyle(bgcolor="#0088cc", color="white"), width=280, on_click=lambda _: page.launch_url("https://t.me/YOUR_BOT")),
                ft.TextButton("Пропустить оплату", on_click=lambda _: show_paid_report(t2_choice))
            ], horizontal_alignment="center"), 
            bgcolor="#1A1A1A", padding=20, border_radius=20, width=380
        ))
        page.update()

    def show_test_t2(t1_choice):
        page.controls.clear()
        page.scroll = "auto"
        page.update()
        
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
            btn = ft.Container(bgcolor=c["hex"], width=80, height=80, border_radius=15) 
            btn.on_click = partial(color_clicked, cid=c["id"], btn=btn)
            grid.controls.append(btn)
            
        page.add(ft.Container(content=ft.Column([ft.Text("ВТОРОЙ ЭТАП", size=18), ft.Container(height=20), grid], horizontal_alignment="center"), bgcolor="#1A1A1A", padding=20, border_radius=20, width=380))
        page.update()

    def show_t1_result(t1_choice):
        page.controls.clear()
        page.scroll = "auto"
        page.update()
        
        countdown = ft.Text("120", size=40, color="#00FFFF")
        btn_next = ft.ElevatedButton("ПРОДОЛЖИТЬ (ЭТАП 2)", visible=False, 
                                     style=ft.ButtonStyle(bgcolor="#1565C0", color="white"),
                                     on_click=lambda _: show_test_t2(t1_choice))
        
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
        ], horizontal_alignment="center"), 
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
        page.scroll = "auto"
        page.update()
        
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
            
        page.add(ft.Container(content=ft.Column([ft.Text("ЭТАП 1", size=18), ft.Container(height=20), grid], horizontal_alignment="center"), bgcolor="#1A1A1A", padding=20, border_radius=20, width=380))
        page.update()

    def show_instructions():
        page.controls.clear()
        # Включаем скролл, чтобы на маленьком экране влезла кнопка
        page.scroll = "auto"
        page.update()
        
        page.add(ft.Container(
            content=ft.Column([
                ft.Text("Инструкция", size=24, weight="bold"),
                ft.Text("1. Выберите цвет, который приятен вам больше всего именно сейчас.", size=15),
                ft.Text("2. Не ассоциируйте цвета с одеждой или предметами.", size=15, color="#FFCC00"),
                ft.Container(height=20),
                ft.ElevatedButton("НАЧАТЬ ТЕСТ", on_click=lambda _: show_test_t1())
            ], horizontal_alignment="center"), bgcolor="#1A1A1A", padding=40, border_radius=20, width=380
        ))
        page.update()

    def show_intro():
        page.controls.clear()
        # Включаем скролл на всякий случай
        page.scroll = "auto"
        page.update()
        
        strips = ft.Row([ft.Container(bgcolor=c["hex"], width=30, height=5) for c in colors_data], alignment="center")
        page.add(ft.Container(
            content=ft.Column([
                strips,
                ft.Text("Цветовая Диагностика", size=24, weight="bold"),
                ft.Text("Метод Макса Люшера", color="grey"),
                ft.Container(height=20),
                ft.ElevatedButton("НАЧАТЬ", on_click=lambda _: show_instructions())
            ], horizontal_alignment="center"), bgcolor="#1A1A1A", padding=40, border_radius=20, width=380
        ))
        page.update()

    # --- ЗАСТАВКА ---
    async def show_splash():
        page.controls.clear()
        
        # ОТКЛЮЧАЕМ СКРОЛЛ НА ЗАСТАВКЕ, ЧТОБЫ БЫЛО ПО ЦЕНТРУ
        page.scroll = None
        page.update()
        
        intro_gif = ft.Image(
            src="intro.gif", 
            width=350,
            height=350,
            fit="contain",
            error_content=ft.Text("Ошибка загрузки intro.gif", color="red")
        )
        
        # Центрируем контент через Container + Column
        page.add(ft.Container(
            content=ft.Column([
                intro_gif,
                ft.Text("N O X A E   L A B", size=24, weight="bold", color="#B266FF")
            ], alignment="center", horizontal_alignment="center"),
            bgcolor="#0A0A0A",
            expand=True,
            alignment=ft.alignment.Alignment(0, 0) # Строгий центр
        ))
        page.update()
        
        await asyncio.sleep(6.5)
        show_intro()

    # ЗАПУСК
    await show_splash()

if __name__ == "__main__":
    print(f"✅ Запуск из папки: {ASSETS_DIR}")
    ft.run(main, assets_dir=ASSETS_DIR)
