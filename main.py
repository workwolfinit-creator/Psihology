import flet as ft
import asyncio
import random
import os
from functools import partial

# --- ЖЕЛЕЗОБЕТОННЫЙ ПУТЬ К ПАПКЕ ASSETS ---
# Определяем, где лежит этот скрипт, и ищем папку assets рядом с ним
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(SCRIPT_DIR, "assets")


async def main(page: ft.Page):
    # --- НАСТРОЙКИ ОКНА ---
    page.title = "PsychoTuner | Метод Люшера"
    page.bgcolor = "#0A0A0A"
    page.theme_mode = "dark"
    page.padding = 0
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"
    page.window_width = 420
    page.window_height = 900

    # Применяем настройки мгновенно
    page.update()

    colors_data = [
        {"id": 1, "hex": "#003399"},  # синий
        {"id": 2, "hex": "#006633"},  # зелёный
        {"id": 3, "hex": "#E50000"},  # красный
        {"id": 4, "hex": "#FFCC00"},  # жёлтый
        {"id": 5, "hex": "#660099"},  # фиолетовый
        {"id": 6, "hex": "#996633"},  # коричневый
        {"id": 7, "hex": "#000000"},  # чёрный
        {"id": 0, "hex": "#808080"}  # серый
    ]

    interpretations = {
        1: "Потребность в глубоком покое, эмоциональном комфорте и гармонии.",
        2: "Стремление к самоутверждению, желание контролировать ситуацию.",
        3: "Жажда жизни, стремление к успеху, активная деятельность.",
        4: "Оптимизм, потребность в перспективе, свободе и новизне.",
        5: "Поиск слияния противоположностей, эмоциональная восприимчивость.",
        6: "Потребность в физическом комфорте, отдыхе и безопасности.",
        7: "Протест против текущей ситуации, негативизм.",
        0: "Желание отгородиться от внешних влияний, 'уйти в тень'."
    }

    # Рандомные подсказки для паузы
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
                "text": "⚡ ЭНЕРГИЯ (Истощение)\n"
                        "Организм работает на резервах. Нужно восстановление.\n\n"
                        "• Информационный детокс: за 1.5 часа до сна — без экранов.\n"
                        "• Увеличьте сон до 8–9 часов.\n"
                        "• Замените кардио на йогу-нидру или лёгкую растяжку.\n"
                        "• Прогрессивная релаксация: напрягите мышцы на 5 сек, затем расслабьте (от ног к голове).\n"
                        "• Добавьте продукты с магнием: орехи, бананы, тёмный шоколад.\n"
                        "• Короткий дневной сон 20–30 минут.",
                "audio_url": "spotify:track:ВАШ_ID_ДЛЯ_ВОССТАНОВЛЕНИЯ"  # Замени на реальный spotify:track:ID
            })
        elif vk_score > 1.9:
            recs.append({
                "text": "⚡ ЭНЕРГИЯ (Перевозбуждение)\n"
                        "Симпатическая система перегружена.\n\n"
                        "• Ограничьте кофеин и энергетики.\n"
                        "• Дыхание «по квадрату»: вдох 4 сек → задержка 4 сек → выдох 4 сек → задержка 4 сек (10 повторений).\n"
                        "• Заземляющие прогулки без телефона 20–30 минут.\n"
                        "• Техника 4-7-8: вдох 4 сек → задержка 7 сек → выдох 8 сек.\n"
                        "• Контрастный душ для сброса адреналина.\n"
                        "• Простая ручная работа (рисование, вязание).",
                "audio_url": "spotify:track:ВАШ_ID_ДЛЯ_СНИЖЕНИЯ"  # Замени
            })
        else:
            recs.append({
                "text": "⚡ ЭНЕРГИЯ: Оптимальный баланс\n"
                        "Поддерживайте текущий режим: полноценный сон, умеренная активность.",
                "audio_url": "spotify:track:ВАШ_ID_ДЛЯ_БАЛАНСА"  # Замени
            })

        if anxiety >= 3:
            recs.append({
                "text": "🧠 ТРЕВОЖНОСТЬ (Высокая)\n"
                        "Вы тратите много ресурсов на компенсацию стресса.\n\n"
                        "• Техника заземления 5-4-3-2-1:\n"
                        "  5 — назовите 5 вещей, которые видите\n"
                        "  4 — 4 вещи, которые можете потрогать\n"
                        "  3 — 3 звука, которые слышите\n"
                        "  2 — 2 запаха\n"
                        "  1 — 1 вкус\n"
                        "• Снизьте планку ожиданий от себя на ближайшие дни.\n"
                        "• Визуализация безопасного места: представьте уютное пространство в деталях.\n"
                        "• Дневник благодарности: запишите 3 вещи, за которые благодарны.\n"
                        "• Телесное сканирование: пройдитесь вниманием по телу, расслабляя каждую часть.",
                "audio_url": "spotify:track:ВАШ_ID_ДЛЯ_ТРЕВОГИ"  # Замени
            })
        elif anxiety > 0:
            recs.append({
                "text": "🧠 ТРЕВОЖНОСТЬ (Фоновая)\n"
                        "Есть внутреннее напряжение.\n\n"
                        "• Рутинная физическая активность: уборка, прогулка, плавание.\n"
                        "• Хобби «ради процесса»: рисование, готовка, вязание.\n"
                        "• Дыхание 4-7-8 для быстрого сброса.\n"
                        "• Назови эмоцию: просто скажите вслух, что чувствуете, без оценки.\n"
                        "• Техника «3-3-3»: назовите 3 вещи, которые видите, 3 звука, 3 части тела.",
                "audio_url": "spotify:track:ВАШ_ID_ДЛЯ_СПОКОЙСТВИЯ"  # Замени
            })

        if risks and "не выявлено" not in risks[0]:
            recs.append({
                "text": "🩺 ТЕЛО (Мышечные блоки)\n"
                        "Стресс проявляется в теле.\n\n"
                        "• Прогрессивная релаксация по Джекобсону (напряжение-расслабление).\n"
                        "• Самомассаж шеи, плеч и челюсти.\n"
                        "• Йога-позы: «ребёнок», «кошка-корова», «скручивание».\n"
                        "• Перенос внимания в тело: 5 минут наблюдать ощущения без оценки.\n"
                        "• Тёплая ванна с солью Эпсома.",
                "audio_url": "spotify:track:ВАШ_ID_ДЛЯ_ТЕЛА"  # Замени
            })

        return recs

    def calculate_metrics(t2_choice):
        anxiety = 0
        for basic_color in [1, 2, 3, 4]:
            pos = t2_choice.index(basic_color) + 1
            if pos == 6:
                anxiety += 1
            elif pos == 7:
                anxiety += 2
            elif pos == 8:
                anxiety += 3
        compensation = 0
        if anxiety > 0:
            for extra_color in [0, 6, 7]:
                pos = t2_choice.index(extra_color) + 1
                if pos == 3:
                    compensation += 1
                elif pos == 2:
                    compensation += 2
                elif pos == 1:
                    compensation += 3
        norm = [3, 4, 2, 5, 1, 6, 0, 7]
        so_score = sum(
            abs((t2_choice.index(c) + 1) - (norm.index(c) + 1)) for c in [item["id"] for item in colors_data])
        if so_score <= 10:
            so_text = "Высокая устойчивость, отсутствие стресса."
        elif so_score <= 19:
            so_text = "Умеренная непродуктивность, рабочее напряжение."
        elif so_score <= 30:
            so_text = "Выраженный дистресс, дезадаптация."
        else:
            so_text = "Критическое состояние, срыв механизмов."
        p1 = t2_choice.index(1) + 1
        p2 = t2_choice.index(2) + 1
        p3 = t2_choice.index(3) + 1
        p4 = t2_choice.index(4) + 1
        vk_score = round((18 - (p3 + p4)) / (18 - (p1 + p2)), 2)
        if vk_score < 0.51:
            vk_text = "Истощение, пассивность (трофотропный тонус)."
        elif vk_score <= 0.91:
            vk_text = "Оптимальный режим (уклон в сохранение сил)."
        elif vk_score <= 1.9:
            vk_text = "Оптимальный режим (эрготропный тонус, активность)."
        else:
            vk_text = "Перевозбуждение, гиперактивность, тревога."
        risks = []
        pos_blue = t2_choice.index(1) + 1
        pos_green = t2_choice.index(2) + 1
        pos_red = t2_choice.index(3) + 1
        pos_gray = t2_choice.index(0) + 1
        if pos_red <= 3 and pos_green <= 3:
            risks.append("Высокий риск гипертонии (перенапряжение, амбиции).")
        if pos_blue >= 6 and pos_green <= 3:
            risks.append("Риск проблем ЖКТ / язвенной болезни.")
        if pos_red >= 6 and pos_gray <= 3:
            risks.append("Риск сердечно-сосудистых проблем (истощение).")
        if not risks:
            risks.append("Специфических психосоматических рисков не выявлено.")
        return anxiety, compensation, so_score, so_text, vk_score, vk_text, risks

    def show_paid_report(t2_choice):
        page.controls.clear()
        anxiety, _, _, _, vk_score, _, risks = calculate_metrics(t2_choice)
        recommendations = generate_recommendations(anxiety, vk_score, risks)

        title = ft.Text("План Восстановления", size=26, weight="bold", color="#00FFFF", text_align="center")
        subtitle = ft.Text("Персональные протоколы саморегуляции:", size=14, color="#CCCCCC", text_align="center")

        recs_ui = ft.Column(spacing=15, scroll="auto")

        for rec in recommendations:
            main_text = ft.Text(rec["text"], size=15, color="#E0E0E0")

            audio_btn = None
            if "audio_url" in rec and rec["audio_url"]:
                audio_btn = ft.ElevatedButton(
                    "🎧 Прослушать в Spotify",
                    style=ft.ButtonStyle(bgcolor="#1DB954", color="white", padding=12),  # Зелёный Spotify
                    width=300,
                    on_click=lambda _, url=rec["audio_url"]: page.launch_url(url)
                )

            rec_container = ft.Container(
                content=ft.Column([main_text, audio_btn] if audio_btn else [main_text], spacing=10,
                                  horizontal_alignment="center"),
                bgcolor="#2A2A2A",
                padding=15,
                border_radius=10,
                border=ft.border.Border.all(1, "#444444")
            )
            recs_ui.controls.append(rec_container)

        card = ft.Container(
            content=ft.Column([title, subtitle, ft.Container(height=20), recs_ui, ft.Container(height=40),
                               ft.ElevatedButton("ЗАВЕРШИТЬ СЕАНС",
                                                 style=ft.ButtonStyle(bgcolor="#1A1A1A", color="white", padding=15),
                                                 elevation=5, width=300, on_click=lambda _: show_intro())],
                              horizontal_alignment="center", scroll="auto"),
            bgcolor="#1A1A1A", padding=30, border_radius=20, width=400, border=ft.border.Border.all(1, "#333333")
        )
        page.add(card)
        page.update()

    def show_clinical_metrics_and_paywall(t1_choice, t2_choice):
        page.controls.clear()
        anxiety, compensation, so_score, so_text, vk_score, vk_text, risks = calculate_metrics(t2_choice)
        disclaimer = ft.Text(
            "⚠️ Это развлекательно-диагностическое приложение. Результаты не являются медицинским заключением. "
            "При наличии симптомов обратитесь к врачу.", size=12, color="#666666", text_align="center", italic=True)
        title = ft.Text("Клинический Анализ", size=26, weight="bold", color="#00FFFF", text_align="center")
        risks_ui = ft.Column([ft.Text(f"• {risk}", size=14, color="#FF6666") for risk in risks])
        results_col = ft.Column([
            ft.Text("ИНДЕКСЫ СТРЕССА", weight="bold", color="#FFCC00"),
            ft.Text(f"Тревожность (A): {anxiety} баллов", size=14),
            ft.Text(f"Компенсация (C): {compensation} баллов", size=14),
            ft.Container(height=10),
            ft.Text("ОТКЛОНЕНИЕ ОТ НОРМЫ", weight="bold", color="#FFCC00"),
            ft.Text(f"СО: {so_score} ({so_text})", size=14),
            ft.Container(height=10),
            ft.Text("ВЕГЕТАТИВНЫЙ БАЛАНС", weight="bold", color="#FFCC00"),
            ft.Text(f"Коэф. Шипоша: {vk_score}", size=14),
            ft.Text(f"{vk_text}", size=13, color="#CCCCCC"),
            ft.Container(height=10),
            ft.Text("ПСИХОСОМАТИЧЕСКИЕ РИСКИ", weight="bold", color="#FFCC00"),
            risks_ui,
            ft.Container(height=15),
            disclaimer
        ], spacing=3)
        paywall_box = ft.Container(
            content=ft.Column([
                ft.Text("🔓 Полный протокол", size=18, weight="bold", color="#00FFFF", text_align="center"),
                ft.Text("Персональные практики для выравнивания показателей.", size=13, color="#A0A0A0",
                        text_align="center"),
                ft.Container(height=15),
                ft.ElevatedButton("ОПЛАТИТЬ РАЗБОР", style=ft.ButtonStyle(bgcolor="#0088cc", color="white", padding=15),
                                  elevation=5, width=300,
                                  on_click=lambda _: page.launch_url("https://t.me/ТВОЙ_БОТ_ДЛЯ_ОПЛАТЫ")),
                ft.Container(height=10),
                ft.TextButton("🔓 Тест: пропустить оплату", on_click=lambda _: show_paid_report(t2_choice),
                              style=ft.ButtonStyle(color="#666666"))
            ], horizontal_alignment="center"),
            bgcolor="#262626", padding=20, border_radius=15, border=ft.border.Border.all(1, "#444444")
        )
        card = ft.Container(
            content=ft.Column([title, ft.Container(height=15), results_col, ft.Container(height=25), paywall_box],
                              horizontal_alignment="center", scroll="auto"),
            bgcolor="#1A1A1A", padding=30, border_radius=20, width=400,
            border=ft.border.Border.all(1, "#333333")
        )
        page.add(card)
        page.update()

    def show_test_t2(t1_choice):
        page.controls.clear()
        t2_choice = []
        instruction = ft.Text("ВТОРОЙ ЭТАП\nВыбирайте так, будто видите цвета впервые.", size=16, weight="bold",
                              text_align="center", color="#FFCC00")

        def color_clicked(e, cid, btn):
            t2_choice.append(cid)
            btn.visible = False
            page.update()
            if len(t2_choice) == 8:
                show_clinical_metrics_and_paywall(t1_choice, t2_choice)

        shuffled_colors = colors_data[:]
        random.shuffle(shuffled_colors)
        color_grid = ft.Row(wrap=True, spacing=12, run_spacing=12, alignment="center")
        for c in shuffled_colors:
            btn = ft.Container(bgcolor=c["hex"], width=100, height=100, border_radius=15)
            btn.on_click = partial(color_clicked, cid=c["id"], btn=btn)
            color_grid.controls.append(btn)
        card = ft.Container(
            content=ft.Column([instruction, ft.Container(height=40), color_grid], horizontal_alignment="center"),
            bgcolor="#1A1A1A", padding=30, border_radius=20, width=400
        )
        page.add(card)
        page.update()

    def show_t1_result(t1_choice):
        page.controls.clear()
        res1 = ft.Text(f"1. {interpretations[t1_choice[0]]}", size=15)
        res2 = ft.Text(f"2. {interpretations[t1_choice[1]]}", size=15)
        countdown_text = ft.Text("120", size=48, color="#00FFFF", weight="bold")
        tip_text = ft.Text(random.choice(relax_tips), size=14, color="#AAAAAA", text_align=ft.TextAlign.CENTER)
        continue_btn = ft.ElevatedButton("ПРОДОЛЖИТЬ (ЭТАП 2)", visible=False,
                                         style=ft.ButtonStyle(bgcolor="#1565C0", color="white"),
                                         elevation=5, on_click=lambda _: show_test_t2(t1_choice))

        async def pause_timer():
            for secs in range(120, 0, -1):
                countdown_text.value = str(secs)
                page.update()
                await asyncio.sleep(1)
            countdown_text.value = "Готово!"
            countdown_text.color = "#00FF00"
            continue_btn.visible = True
            page.update()

        pause_box = ft.Container(
            content=ft.Column([
                ft.Text("Пауза 2 минуты", size=18, weight="bold", color="#00FFFF"),
                ft.Container(height=20),
                ft.Text("Отвлекитесь от экрана и расслабьтесь:", size=14, color="#CCCCCC",
                        text_align=ft.TextAlign.CENTER),
                ft.Container(height=15),
                tip_text,
                ft.Container(height=30),
                countdown_text,
                ft.Container(height=30),
                continue_btn
            ], horizontal_alignment="center"),
            bgcolor="#262626", padding=30, border_radius=15
        )
        card = ft.Container(
            content=ft.Column([
                ft.Text("Текущее состояние", size=24, weight="bold"),
                ft.Container(height=20), res1, ft.Container(height=10), res2,
                ft.Container(height=40), pause_box
            ], horizontal_alignment="center"),
            bgcolor="#1A1A1A", padding=30, border_radius=20, width=400
        )
        page.add(card)
        page.update()
        page.run_task(pause_timer)

    def show_test_t1():
        page.controls.clear()
        t1_choice = []
        instruction = ft.Text("ЭТАП 1\nВыберите цвет, который вам сейчас наиболее приятен", size=18, weight="bold",
                              text_align="center")

        def color_clicked(e, cid, btn):
            t1_choice.append(cid)
            btn.visible = False
            page.update()
            if len(t1_choice) == 8:
                show_t1_result(t1_choice)

        shuffled_colors = colors_data[:]
        random.shuffle(shuffled_colors)
        color_grid = ft.Row(wrap=True, spacing=12, run_spacing=12, alignment="center")
        for c in shuffled_colors:
            btn = ft.Container(bgcolor=c["hex"], width=100, height=100, border_radius=15)
            btn.on_click = partial(color_clicked, cid=c["id"], btn=btn)
            color_grid.controls.append(btn)
        card = ft.Container(
            content=ft.Column([instruction, ft.Container(height=40), color_grid], horizontal_alignment="center"),
            bgcolor="#1A1A1A", padding=30, border_radius=20, width=400
        )
        page.add(card)
        page.update()

    def show_instructions():
        page.controls.clear()
        rules = ft.Column([
            ft.Text("1. Выберите цвет, который приятен вам больше всего именно сейчас.", size=15),
            ft.Text("2. Не ассоциируйте цвета с одеждой или предметами.", size=15, color="#FFCC00", italic=True),
        ], spacing=15)
        card = ft.Container(
            content=ft.Column([
                ft.Text("Инструкция", size=24, weight="bold"),
                ft.Container(height=30), rules, ft.Container(height=50),
                ft.ElevatedButton("НАЧАТЬ ТЕСТ", style=ft.ButtonStyle(bgcolor="#006633", color="white", padding=20),
                                  elevation=5, width=300, on_click=lambda _: show_test_t1())
            ], horizontal_alignment="center"),
            bgcolor="#1A1A1A", padding=40, border_radius=20, width=400
        )
        page.add(card)
        page.update()

    def show_intro():
        page.controls.clear()
        color_strips = ft.Row([
            ft.Container(bgcolor=c["hex"], width=32, height=6, border_radius=3) for c in colors_data
        ], alignment="center", spacing=5)
        card = ft.Container(
            content=ft.Column([
                color_strips, ft.Container(height=20),
                ft.Text("Цветовая Диагностика", size=26, weight="bold"),
                ft.Text("Метод Макса Люшера", size=14, color="#B0B0B0"),
                ft.Container(height=25),
                ft.ElevatedButton("НАЧАТЬ", style=ft.ButtonStyle(bgcolor="#1565C0", color="white", padding=20),
                                  elevation=5, width=300, on_click=lambda _: show_instructions())
            ], horizontal_alignment="center"),
            bgcolor="#1A1A1A", padding=40, border_radius=20, width=400
        )
        page.add(card)
        page.update()

    def show_about_test():
        page.controls.clear()
        title = ft.Text("О методе Макса Люшера", size=22, weight="bold", text_align="center", color="#FFCC00")
        info_text = ft.Text(
            "Цветовой тест представлен в 1947 году. Обходит сознательные фильтры.\n\n"
            "Цветовые предпочтения отражают психофизиологическое состояние и скрытые потребности.\n\n"
            "Современные исследования подтверждают активацию лимбической системы.",
            size=14, text_align="center", color="#CCCCCC"
        )
        btn_next = ft.ElevatedButton("ПРОДОЛЖИТЬ", style=ft.ButtonStyle(bgcolor="#1A1A1A", color="white", padding=15),
                                     elevation=5, width=300, on_click=lambda _: show_intro())
        card = ft.Container(
            content=ft.Column([title, ft.Container(height=20), info_text, ft.Container(height=30), btn_next],
                              horizontal_alignment="center"),
            bgcolor="#262626", padding=40, border_radius=20, width=400,
            border=ft.border.Border.all(1, "#333333")
        )
        page.add(card)
        page.update()

    # --- ИНТЕГРИРОВАННАЯ ЗАСТАВКА (ВИДЕО/ГИФ) ---
    async def show_splash():
        page.controls.clear()

        # Исправлено: fit="contain" (строка, не класс)
        # Путь берется динамически, файл точно будет найден
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
            # Координаты (0,0) = центр
            alignment=ft.alignment.Alignment(0, 0)
        ))
        page.update()

        # Ждем 6.5 секунд, пока играет гифка
        await asyncio.sleep(6.5)

        show_about_test()

    # ЗАПУСК
    await show_splash()


if __name__ == "__main__":
    print(f"✅ Запуск из папки: {ASSETS_DIR}")
    ft.run(main, assets_dir=ASSETS_DIR)