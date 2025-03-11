import aiogram
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import random
import uuid

def check_win(board):
    # Check horizontal lines
    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2] != " ":
            return board[i][0]
            
    # Check vertical lines
    for i in range(3):
        if board[0][i] == board[1][i] == board[2][i] != " ":
            return board[0][i]
            
    # Check diagonals
    if board[0][0] == board[1][1] == board[2][2] != " ":
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != " ":
        return board[0][2]
        
    # Check for draw
    is_full = True
    for row in board:
        if " " in row:
            is_full = False
            break
            
    if is_full:
        return "Draw"
        
    return None

dp = Dispatcher()
bot = Bot(token="7866062846:AAF8YkrXnbUkTcSUW6MeacclMcLgEdM1qkY")
lobby = []
premium_lobby = []  # Lobby for premium players
games = {}  # (player1, player2): [board, current_player, message_ids]
premium_games = {}  # Separate dictionary for premium games
message_ids = {}  # user_id: message_id
ratings = {}  # user_id: rating
premium_users = set()  # Set of premium user IDs
ADMIN_ID = 5635916497  # Admin ID
bot_games = {}  # user_id: {board, current_player, message_id}
user_languages = {}  # user_id: language_code
LANGUAGES = {
    'en': 'English 🇬🇧',
    'ru': 'Русский 🇷🇺',
    'uk': 'Українська 🇺🇦'
}

TRANSLATIONS = {
    'en': {
        'already_in_lobby': "You are already in the lobby.",
        'already_in_game': "You are already in a game.",
        'joined_lobby': "You have joined the lobby. Waiting for another player...",
        'joined_premium_lobby': "You have joined the premium lobby. Waiting for another premium player...",
        'invalid_coordinates': "Invalid coordinates. Please enter two numbers between 1 and 3 separated by a space.",
        'invalid_format': "Invalid format. Please use: /move <row> <column>",
        'not_your_turn': "It's not your turn!",
        'cell_occupied': "This cell is already occupied!",
        'your_move': "Your move:",
        'opponent_move': "Opponent's move:",
        'game_draw': "It's a draw!",
        'you_won': "Congratulations! You won!",
        'you_lost': "You lost!",
        'not_in_game': "You are not in an active game. Use /lobby to join a game.",
        'left_lobby': "🚪 You have left the lobby.",
        'left_premium_lobby': "🚪 You have left the premium lobby.",
        'left_bot_game': "🚪 You have left the game with bot.",
        'left_game': "🚪 You have left the game.\nRating penalty: -{penalty} points 📉",
        'opponent_left': "🏆 Your opponent has left the game!\nYou win! Rating: +{points} points 📈",
        'not_in_lobby_game': "❓ You are not in any lobby or game.",
        'status_rating': "Your Status: {status}\nCurrent Rating: {rating} points",
        'no_games_played': "🎮 No games have been played yet!",
        'premium_only': "This command is only available for premium users!",
        'no_permission': "You don't have permission to use this command!",
        'premium_granted': "Premium status granted to {name}!",
        'premium_removed': "Premium status removed from {name}",
        'premium_deactivated': "Your premium status has been deactivated.",
        'usage_give_premium': "Usage: /give_premium user_id",
        'usage_remove_premium': "Usage: /remove_premium user_id",
        'game_with_bot': "🤖 Game with bot started!\nYou play as X. Your turn!",
        'already_in_bot_game': "You are already in a game with the bot!",
        'left_lobby_joined_bot': "🚪You have left the lobby.",
        'error_starting_game': "Error starting game. Please try again.",
        'error_occurred': "An error occurred. Please try again.",
        'game_started': "{game_type} started!\nYou have been matched with {opponent}. You are {symbol}. {turn_text}!{bonus}",
        'your_turn': "Your turn",
        'wait_turn': "Wait for your turn",
        'premium_bonus': " (Premium bonus: +2 rating for win!)",
        'select_language': "Select your language / Выберите язык",
        'language_set': "Language set to English!",
        'premium_active': "You already have premium status!",
        'premium_benefits': "Your benefits:\n✨ Reduced rating loss (-3 instead of -5)\n✨ Increased rating gain (+7 instead of +5)\n✨ Access to premium lobby (/premium_lobby)\n✨ Additional +2 rating points in premium games!",
        'premium_offer': "Get Premium Status!",
        'payment_info': "Payment Information:\nCard: 5168 7451 6813 4952\nPrice: USD 5 for lifetime\nContact @neco_12 for details",
        'basic_commands': "📋 Basic Commands:\n/lobby - Join regular game lobby\n/play_bot - Play against bot\n/cancel - Leave current game or lobby\n/rating - Check your rating\n/top - View top players\n/donate - Get premium status",
        'premium_commands': "\n🌟 Premium Commands:\n/premium_lobby - Join premium lobby",
        'premium_locked': "\n🔒 Get premium status to access more features!",
        'premium_game': "🌟 Premium game",
        'regular_game': "🎮 Regular game",
        'welcome_message': """👋 Welcome to Tic-Tac-Toe Bot!

🎮 Play against other players or try your luck against the bot!

Available commands:
/lobby - Join regular game lobby
/play_bot - Play against bot
/premium_lobby - Join premium lobby (premium only)
/rating - Check your rating
/top - View top players
/donate - Get premium status
/language - Change language
/help - Show all commands""",
        'top_players_header': "🏆 Top Players:",
        'top_player_entry': "{medal} {name} {premium}: {rating} points\n",
        'premium_status': "🌟 Premium",
        'regular_status': "👤 Regular",
        'premium_granted_notification': """🌟 Congratulations! You've been granted premium status!

Your benefits:
✨ Reduced rating loss on defeat (-3 instead of -5)
✨ Increased rating gain (+7 instead of +5)
✨ Access to premium lobby (/premium_lobby)
✨ Additional +2 rating points in premium games!""",
        'invalid_game_data': "Invalid game data!",
        'invalid_move_coordinates': "Invalid move coordinates!",
        'game_not_found': "Game not found!",
        'not_participant': "You are not a participant in this game!",
        'error_updating_game': "Error updating game state. Please try again.",
        'bot_game_state': "🤖 Game with Bot:\n{current_player}'s turn",
        'game_state': "{game_type} Game state:\n{player_name}'s turn",
        'game_over': "{game_type} Game {result}!\nRating: {points:+d} points",
        'bot_game_over_win': "🎉 Congratulations! You won against the bot!",
        'bot_game_over_lose': "💔 Game Over! The bot won!",
        'bot_game_over_draw': "🤝 It's a draw with the bot!",
        'bot_thinking': "Bot is thinking...",
    },
    'ru': {
        'already_in_lobby': "Вы уже в лобби.",
        'already_in_game': "Вы уже в игре.",
        'joined_lobby': "Вы присоединились к лобби. Ожидание другого игрока...",
        'joined_premium_lobby': "Вы присоединились к премиум лобби. Ожидание другого премиум игрока...",
        'invalid_coordinates': "Неверные координаты. Пожалуйста, введите два числа от 1 до 3, разделенные пробелом.",
        'invalid_format': "Неверный формат. Используйте: /move <строка> <столбец>",
        'not_your_turn': "Сейчас не ваш ход!",
        'cell_occupied': "Эта клетка уже занята!",
        'your_move': "Ваш ход:",
        'opponent_move': "Ход противника:",
        'game_draw': "Ничья!",
        'you_won': "Поздравляем! Вы победили!",
        'you_lost': "Вы проиграли!",
        'not_in_game': "Вы не в активной игре. Используйте /lobby чтобы присоединиться к игре.",
        'left_lobby': "🚪 Вы покинули лобби.",
        'left_premium_lobby': "🚪 Вы покинули премиум лобби.",
        'left_bot_game': "🚪 Вы покинули игру с ботом.",
        'left_game': "🚪 Вы покинули игру.\nШтраф рейтинга: -{penalty} очков 📉",
        'opponent_left': "🏆 Ваш противник покинул игру!\nВы победили! Рейтинг: +{points} очков 📈",
        'not_in_lobby_game': "❓ Вы не в лобби и не в игре.",
        'status_rating': "Ваш статус: {status}\nТекущий рейтинг: {rating} очков",
        'no_games_played': "🎮 Игр еще не было!",
        'premium_only': "Эта команда доступна только для премиум пользователей!",
        'no_permission': "У вас нет прав для использования этой команды!",
        'premium_granted': "Премиум статус выдан {name}!",
        'premium_removed': "Премиум статус удален у {name}",
        'premium_deactivated': "Ваш премиум статус деактивирован.",
        'usage_give_premium': "Использование: /give_premium user_id",
        'usage_remove_premium': "Использование: /remove_premium user_id",
        'game_with_bot': "🤖 Игра с ботом начата!\nВы играете за X. Ваш ход!",
        'already_in_bot_game': "Вы уже в игре с ботом!",
        'left_lobby_joined_bot': "🚪Вы покинули лобби.",
        'error_starting_game': "Ошибка при запуске игры. Попробуйте еще раз.",
        'error_occurred': "Произошла ошибка. Попробуйте еще раз.",
        'game_started': "{game_type} начата!\nВы играете против {opponent}. Вы играете за {symbol}. {turn_text}!{bonus}",
        'your_turn': "Ваш ход",
        'wait_turn': "Ждите своего хода",
        'premium_bonus': " (Премиум бонус: +2 к рейтингу за победу!)",
        'premium_active': "У вас уже есть премиум статус!",
        'premium_benefits': "Ваши преимущества:\n✨ Уменьшенная потеря рейтинга (-3 вместо -5)\n✨ Увеличенный прирост рейтинга (+7 вместо +5)\n✨ Доступ к премиум лобби (/premium_lobby)\n✨ Дополнительные +2 очка рейтинга в премиум играх!",
        'premium_offer': "Получите Премиум Статус!",
        'payment_info': "Информация об оплате:\nКарта: 5168 7451 6813 4952\nЦена: 5 USD навсегда\nСвяжитесь с @neco_12 для деталей",
        'basic_commands': "📋 Основные команды:\n/lobby - Присоединиться к обычному лобби\n/play_bot - Играть против бота\n/cancel - Покинуть текущую игру или лобби\n/rating - Проверить свой рейтинг\n/top - Посмотреть топ игроков\n/donate - Получить премиум статус",
        'premium_commands': "\n🌟 Премиум команды:\n/premium_lobby - Присоединиться к премиум лобби",
        'premium_locked': "\n🔒 Получите премиум статус для доступа к дополнительным функциям!",
        'premium_game': "🌟 Премиум игра",
        'regular_game': "🎮 Обычная игра",
        'welcome_message': """👋 Добро пожаловать в игру Крестики-нолики!

🎮 Играйте против других игроков или попробуйте сыграть против бота!

Доступные команды:
/lobby - Присоединиться к обычному лобби
/play_bot - Играть против бота
/premium_lobby - Присоединиться к премиум лобби
/rating - Проверить свой рейтинг
/top - Посмотреть топ игроков
/donate - Получить премиум статус
/language - Изменить язык
/help - Показать все команды""",
        'top_players_header': "🏆 Лучшие игроки:",
        'top_player_entry': "{medal} {name} {premium}: {rating} очков\n",
        'premium_status': "🌟 Премиум",
        'regular_status': "👤 Regular",
        'premium_granted_notification': """🌟 Поздравляем! Вам выдан премиум статус!

Ваши преимущества:
✨ Уменьшенная потеря рейтинга при поражении (-3 вместо -5)
✨ Увеличенный прирост рейтинга (+7 вместо +5)
✨ Доступ к премиум лобби (/premium_lobby)
✨ Дополнительные +2 очка рейтинга в премиум играх!""",
        'invalid_game_data': "Неверные данные игры!",
        'invalid_move_coordinates': "Неверные координаты хода!",
        'game_not_found': "Игра не найдена!",
        'not_participant': "Вы не участвуете в этой игре!",
        'error_updating_game': "Ошибка при обновлении состояния игры. Попробуйте еще раз.",
        'bot_game_state': "🤖 Игра с ботом:\nХод {current_player}",
        'game_state': "{game_type} Состояние игры:\nХод {player_name}",
        'game_over': "{game_type} Игра {result}!\nРейтинг: {points:+d} очков",
        'bot_game_over_win': "🎉 Поздравляем! Вы победили бота!",
        'bot_game_over_lose': "💔 Игра окончена! Бот победил!",
        'bot_game_over_draw': "🤝 Ничья с ботом!",
        'bot_thinking': "Бот думает...",
        'select_language': "Select your language / Выберите язык",
        'language_set': "Язык изменён на русский!",
    },
    'uk': {
        'already_in_lobby': "Ви вже в лобі.",
        'already_in_game': "Ви вже в грі.",
        'joined_lobby': "Ви приєдналися до лобі. Очікування іншого гравця...",
        'joined_premium_lobby': "Ви приєдналися до преміум лобі. Очікування іншого преміум гравця...",
        'invalid_coordinates': "Неправильні координати. Будь ласка, введіть два числа від 1 до 3, розділені пробілом.",
        'invalid_format': "Неправильний формат. Використовуйте: /move <ряд> <стовпець>",
        'not_your_turn': "Зараз не ваш хід!",
        'cell_occupied': "Ця клітинка вже зайнята!",
        'your_move': "Ваш хід:",
        'opponent_move': "Хід суперника:",
        'game_draw': "Нічия!",
        'you_won': "Вітаємо! Ви перемогли!",
        'you_lost': "Ви програли!",
        'not_in_game': "Ви не в активній грі. Використовуйте /lobby щоб приєднатися до гри.",
        'left_lobby': "🚪 Ви покинули лобі.",
        'left_premium_lobby': "🚪 Ви покинули преміум лобі.",
        'left_bot_game': "🚪 Ви покинули гру з ботом.",
        'left_game': "🚪 Ви покинули гру.\nШтраф рейтингу: -{penalty} очків 📉",
        'opponent_left': "🏆 Ваш суперник покинув гру!\nВи перемогли! Рейтинг: +{points} очків 📈",
        'not_in_lobby_game': "❓ Ви не в лобі і не в грі.",
        'status_rating': "Ваш статус: {status}\nПоточний рейтинг: {rating} очків",
        'no_games_played': "🎮 Ігор ще не було!",
        'premium_only': "Ця команда доступна тільки для преміум користувачів!",
        'no_permission': "У вас немає прав для використання цієї команди!",
        'premium_granted': "Преміум статус надано {name}!",
        'premium_removed': "Преміум статус видалено у {name}",
        'premium_deactivated': "Ваш преміум статус деактивовано.",
        'usage_give_premium': "Використання: /give_premium user_id",
        'usage_remove_premium': "Використання: /remove_premium user_id",
        'game_with_bot': "🤖 Гра з ботом розпочата!\nВи граєте за X. Ваш хід!",
        'already_in_bot_game': "Ви вже в грі з ботом!",
        'left_lobby_joined_bot': "🚪Ви покинули лобі.",
        'error_starting_game': "Помилка при запуску гри. Спробуйте ще раз.",
        'error_occurred': "Сталася помилка. Спробуйте ще раз.",
        'game_started': "{game_type} розпочата!\nВи граєте проти {opponent}. Ви граєте за {symbol}. {turn_text}!{bonus}",
        'your_turn': "Ваш хід",
        'wait_turn': "Чекайте свого ходу",
        'premium_bonus': " (Преміум бонус: +2 до рейтингу за перемогу!)",
        'premium_active': "У вас вже є преміум статус!",
        'premium_benefits': "Ваші переваги:\n✨ Зменшена втрата рейтингу (-3 замість -5)\n✨ Збільшений приріст рейтингу (+7 замість +5)\n✨ Доступ до преміум лобі (/premium_lobby)\n✨ Додаткові +2 очки рейтингу в преміум іграх!",
        'premium_offer': "Отримайте Преміум Статус!",
        'payment_info': "Інформація про оплату:\nКарта: 5168 7451 6813 4952\nЦіна: 5 USD назавжди\nЗв'яжіться з @neco_12 для деталей",
        'basic_commands': "📋 Основні команди:\n/lobby - Приєднатися до звичайного лобі\n/play_bot - Грати проти бота\n/cancel - Покинути поточну гру або лобі\n/rating - Перевірити свій рейтинг\n/top - Переглянути топ гравців\n/donate - Отримати преміум статус",
        'premium_commands': "\n🌟 Преміум команди:\n/premium_lobby - Приєднатися до преміум лобі",
        'premium_locked': "\n🔒 Отримайте преміум статус для доступу до додаткових функцій!",
        'premium_game': "🌟 Преміум гра",
        'regular_game': "🎮 Звичайна гра",
        'welcome_message': """👋 Ласкаво просимо до гри Хрестики-нулики!

🎮 Грайте проти інших гравців або спробуйте зіграти проти бота!

Доступні команди:
/lobby - Приєднатися до звичайного лобі
/play_bot - Грати проти бота
/premium_lobby - Приєднатися до преміум лобі
/rating - Перевірити свій рейтинг
/top - Переглянути топ гравців
/donate - Отримати преміум статус
/language - Змінити мову
/help - Показати всі команди""",
        'top_players_header': "🏆 Кращі гравці:",
        'top_player_entry': "{medal} {name} {premium}: {rating} очків\n",
        'premium_status': "🌟 Преміум",
        'regular_status': "👤 Звичайний",
        'premium_granted_notification': """🌟 Вітаємо! Вам надано преміум статус!

Ваші переваги:
✨ Зменшена втрата рейтингу при поразці (-3 замість -5)
✨ Збільшений приріст рейтингу (+7 замість +5)
✨ Доступ до преміум лобі (/premium_lobby)
✨ Додаткові +2 очки рейтингу в преміум іграх!""",
        'invalid_game_data': "Неправильні дані гри!",
        'invalid_move_coordinates': "Неправильні координати ходу!",
        'game_not_found': "Гра не знайдена!",
        'not_participant': "Ви не є учасником цієї гри!",
        'error_updating_game': "Помилка при оновленні стану гри. Спробуйте ще раз.",
        'bot_game_state': "🤖 Гра з ботом:\nХід {current_player}",
        'game_state': "{game_type} Стан гри:\nХід {player_name}",
        'game_over': "{game_type} Гра {result}!\nРейтинг: {points:+d} очків",
        'bot_game_over_win': "🎉 Вітаємо! Ви перемогли бота!",
        'bot_game_over_lose': "💔 Гра закінчена! Бот переміг!",
        'bot_game_over_draw': "🤝 Нічия з ботом!",
        'bot_thinking': "Бот думає...",
        'select_language': "Select your language / Выберите язык / Виберіть мову",
        'language_set': "Мову змінено на українську!",
    }
}

def get_text(key: str, lang: str = 'en', **kwargs) -> str:
    """Get localized text by key and language with optional format parameters"""
    translations = TRANSLATIONS.get(lang, TRANSLATIONS['en'])
    text = translations.get(key, TRANSLATIONS['en'][key])
    if kwargs:
        try:
            return text.format(**kwargs)
        except KeyError:
            return text
    return text

async def get_user_info(user_id):
    try:
        user = await bot.get_chat(user_id)
        try:
            return user.first_name
        except:
            try:
                return user.username
            except:
                return str(user_id)
    except Exception as e:
        print(f"Error getting user info: {e}")
        return str(user_id)

@dp.message(Command("start"))
async def start_command(message: types.Message):
    lang = user_languages.get(message.from_user.id, 'en')
    await message.answer(get_text('welcome_message', lang=lang))

@dp.message(Command("lobby"))
async def lobby_command(message: types.Message):
    lang = user_languages.get(message.from_user.id, 'en')
    if message.from_user.id in lobby or message.from_user.id in premium_lobby:
        await message.answer(get_text('already_in_lobby', lang=lang))
        return
        
    for i in list(games.keys()) + list(premium_games.keys()):
        if message.from_user.id in i:
            await message.answer(get_text('already_in_game', lang=lang))
            return
            
    if message.from_user.id in bot_games:
        await message.answer(get_text('already_in_game', lang=lang))
        return
            
    lobby.append(message.from_user.id)
    await message.answer(get_text('joined_lobby', lang=lang))

@dp.message(Command("move"))
async def move_command(message: types.Message):
    lang = user_languages.get(message.from_user.id, 'en')
    try:
        coordinates = list(map(int, message.text.split()[1:]))
        if len(coordinates) != 2 or not all(1 <= x <= 3 for x in coordinates):
            await message.answer(get_text('invalid_coordinates', lang=lang))
            return
    except:
        await message.answer(get_text('invalid_format', lang=lang))
        return

    for pair, game in {**games, **premium_games}.items():
        if message.from_user.id in pair:
            board, current_player = game
            if (message.from_user.id == pair[0] and current_player != "X") or \
               (message.from_user.id == pair[1] and current_player != "O"):
                await message.answer(get_text('not_your_turn', lang=lang))
                return

            col, row = coordinates[0] - 1, coordinates[1] - 1
            if board[row][col] != " ":
                await message.answer(get_text('cell_occupied', lang=lang))
                return

            board[row][col] = current_player
            game[1] = "O" if current_player == "X" else "X"

            board_str = "\n".join([
                f"{row[0]} | {row[1]} | {row[2]}"
                for row in board
            ])
            
            await message.answer(f"{get_text('your_move', lang=lang)}\n{board_str}")
            
            opponent_id = pair[1] if message.from_user.id == pair[0] else pair[0]
            opponent_lang = user_languages.get(opponent_id, 'en')
            await bot.send_message(
                opponent_id,
                f"{get_text('opponent_move', lang=opponent_lang)}\n{board_str}"
            )

            winner = check_win(board)
            if winner:
                if winner == "Draw":
                    await message.answer(get_text('game_draw', lang=lang))
                    await bot.send_message(
                        opponent_id,
                        get_text('game_draw', lang=opponent_lang)
                    )
                else:
                    winner_id = pair[0] if winner == "X" else pair[1]
                    if message.from_user.id == winner_id:
                        await message.answer(get_text('you_won', lang=lang))
                        await bot.send_message(
                            opponent_id,
                            get_text('you_lost', lang=opponent_lang)
                        )
                    else:
                        await message.answer(get_text('you_lost', lang=lang))
                        await bot.send_message(
                            pair[0] if message.from_user.id == pair[1] else pair[1],
                            get_text('you_won', lang=opponent_lang)
                        )
                if pair in premium_games:
                    del premium_games[pair]
                else:
                    del games[pair]
            return
    await message.answer(get_text('not_in_game', lang=lang))

@dp.message(Command("cancel"))
async def cancel_command(message: types.Message):
    user_id = message.from_user.id
    lang = user_languages.get(user_id, 'en')
    
    if user_id in lobby:
        lobby.remove(user_id)
        await message.answer(get_text('left_lobby', lang=lang))
        return
        
    if user_id in premium_lobby:
        premium_lobby.remove(user_id)
        await message.answer(get_text('left_premium_lobby', lang=lang))
        return
        
    if user_id in bot_games:
        del bot_games[user_id]
        await message.answer(get_text('left_bot_game', lang=lang))
        return
        
    for game_dict in [games, premium_games]:
        for players, game_data in list(game_dict.items()):
            if user_id in players:
                opponent_id = players[1] if user_id == players[0] else players[0]
                game_type = "premium" if players in premium_games else "regular"
                
                # Update ratings
                ratings.setdefault(user_id, 0)
                ratings.setdefault(opponent_id, 0)
                
                # Calculate points - increased penalty for leaving
                leave_penalty = 5 if user_id in premium_users else 8  # Higher penalty for leaving
                win_points = 7 if opponent_id in premium_users else 5
                
                if game_type == "premium":
                    win_points += 2
                    leave_penalty += 2  # Additional penalty for leaving premium game
                
                # Update ratings
                ratings[user_id] = max(0, ratings[user_id] - leave_penalty)
                ratings[opponent_id] += win_points
                
                # Send messages
                await message.answer(
                    get_text('left_game', lang=lang, penalty=leave_penalty)
                )
                try:
                    opponent_lang = user_languages.get(opponent_id, 'en')
                    await bot.send_message(
                        opponent_id,
                        get_text('opponent_left', lang=opponent_lang, points=win_points)
                    )
                except:
                    pass
                    
                del game_dict[players]
                return
                
    await message.answer(get_text('not_in_lobby_game', lang=lang))

@dp.message(Command("rating"))
async def rating_command(message: types.Message):
    lang = user_languages.get(message.from_user.id, 'en')
    user_id = message.from_user.id
    rating = ratings.get(user_id, 0)
    status = get_text('premium_status', lang=lang) if user_id in premium_users else get_text('regular_status', lang=lang)
    
    await message.answer(get_text('status_rating', lang=lang, status=status, rating=rating))

@dp.message(Command("top"))
async def top_command(message: types.Message):
    lang = user_languages.get(message.from_user.id, 'en')
    if not ratings:
        await message.answer(get_text('no_games_played', lang=lang))
        return
        
    sorted_ratings = sorted(ratings.items(), key=lambda x: x[1], reverse=True)
    top_10 = sorted_ratings[:10]
    
    response = get_text('top_players_header', lang=lang) + "\n\n"
    medals = ["🥇", "🥈", "🥉"]
    
    for i, (player_id, rating) in enumerate(top_10):
        try:
            user = await bot.get_chat(player_id)
            name = user.first_name
            medal = medals[i] if i < 3 else "👤"
            premium = "🌟" if player_id in premium_users else ""
            response += get_text('top_player_entry', lang=lang, 
                               medal=medal, name=name, premium=premium, rating=rating)
        except:
            continue
            
    await message.answer(response)

@dp.message(Command("premium_lobby"))
async def premium_lobby_command(message: types.Message):
    lang = user_languages.get(message.from_user.id, 'en')
    if message.from_user.id not in premium_users:
        await message.answer(get_text('premium_only', lang=lang))
        return
        
    if message.from_user.id in premium_lobby or message.from_user.id in lobby:
        await message.answer(get_text('already_in_lobby', lang=lang))
        return
        
    for i in list(games.keys()) + list(premium_games.keys()):
        if message.from_user.id in i:
            await message.answer(get_text('already_in_game', lang=lang))
            return
            
    if message.from_user.id in bot_games:
        await message.answer(get_text('already_in_game', lang=lang))
        return
            
    premium_lobby.append(message.from_user.id)
    await message.answer(get_text('joined_premium_lobby', lang=lang))

@dp.message(Command("give_premium"))
async def give_premium_command(message: types.Message):
    lang = user_languages.get(message.from_user.id, 'en')
    if message.from_user.id != ADMIN_ID:
        await message.answer(get_text('no_permission', lang=lang))
        return
        
    try:
        user_id = int(message.text.split()[1])
        premium_users.add(user_id)
        user_name = await get_user_info(user_id)
        await message.answer(get_text('premium_granted', lang=lang, name=user_name))
        
        user_lang = user_languages.get(user_id, 'en')
        try:
            await bot.send_message(
                user_id,
                get_text('premium_granted_notification', lang=user_lang)
            )
        except:
            print(f"Failed to send message to user {user_id}")
    except:
        await message.answer(get_text('usage_give_premium', lang=lang))

@dp.message(Command("remove_premium"))
async def remove_premium_command(message: types.Message):
    lang = user_languages.get(message.from_user.id, 'en')
    if message.from_user.id != ADMIN_ID:
        await message.answer(get_text('no_permission', lang=lang))
        return
        
    try:
        user_id = int(message.text.split()[1])
        if user_id in premium_users:
            premium_users.remove(user_id)
            user_name = await get_user_info(user_id)
            await message.answer(get_text('premium_removed', lang=lang, name=user_name))
            
            user_lang = user_languages.get(user_id, 'en')
            try:
                await bot.send_message(user_id, get_text('premium_deactivated', lang=user_lang))
            except:
                print(f"Failed to send message to user {user_id}")
    except:
        await message.answer(get_text('usage_remove_premium', lang=lang))

@dp.message(Command("help"))
async def help_command(message: types.Message):
    lang = user_languages.get(message.from_user.id, 'en')
    is_premium = message.from_user.id in premium_users
    
    basic_commands = get_text('basic_commands', lang=lang)
    premium_commands = get_text('premium_commands', lang=lang) if is_premium else get_text('premium_locked', lang=lang)
    
    await message.answer(basic_commands + "\n" + premium_commands)

@dp.message(Command("language"))
async def language_command(message: types.Message):
    lang = user_languages.get(message.from_user.id, 'en')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=lang_name, callback_data=f"lang_{code}") 
         for code, lang_name in LANGUAGES.items()]
    ])
    await message.answer(get_text('select_language', lang=lang), reply_markup=keyboard)

@dp.callback_query(lambda c: c.data.startswith('lang_'))
async def handle_language_selection(callback_query: types.CallbackQuery):
    lang_code = callback_query.data.split('_')[1]
    user_languages[callback_query.from_user.id] = lang_code
    
    # Отправляем уведомление о смене языка
    await callback_query.answer(
        get_text('language_set', lang=lang_code),
        show_alert=True
    )
    
    # Обновляем сообщение с выбором языка
    await callback_query.message.edit_text(
        get_text('select_language', lang=lang_code),
        reply_markup=None
    )

def create_game_keyboard(board, current_player, game_type, game_id):
    keyboard = []
    for i in range(3):
        row = []
        for j in range(3):
            cell = board[i][j]
            if cell == "X":
                text = "❌"
            elif cell == "O":
                text = "⭕"
            else:
                text = "⬜"
                
            callback_data = f"move_{game_type}_{game_id}_{i}_{j}"
            if len(callback_data) > 64:  # Telegram limit
                callback_data = "occupied"
            row.append(InlineKeyboardButton(
                text=text,
                callback_data=callback_data if cell == " " else "occupied"
            ))
        keyboard.append(row)
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def format_board_message(game_type, current_player, player_name=None, is_bot_game=False):
    prefix = "🌟 Premium" if game_type == "premium" else "🎮"
    if is_bot_game:
        return f"{prefix} Game with Bot:\n{'Your' if current_player == 'X' else 'Bot'}'s turn"
    else:
        return f"{prefix} Game state:\n{player_name}'s turn"

def format_game_over_message(game_type, result, rating_change=None):
    prefix = "🌟 Premium" if game_type == "premium" else "🎮"
    if result == "draw":
        message = f"{prefix} Game Draw! 🤝"
    elif result == "win":
        message = f"{prefix} Victory! 🎉\nCongratulations! You won!"
    elif result == "lose":
        message = f"{prefix} Game Over! 💔\nYou lost!"
    else:
        message = f"{prefix} Game Over!"
        
    if rating_change:
        if rating_change > 0:
            message += f"\nRating: +{rating_change} points 📈"
        else:
            message += f"\nRating: {rating_change} points 📉"
            
    return message

@dp.callback_query(lambda c: c.data.startswith('move_'))
async def process_callback(callback_query: types.CallbackQuery):
    lang = user_languages.get(callback_query.from_user.id, 'en')
    try:
        data_parts = callback_query.data.split('_')
        if len(data_parts) != 5:
            await callback_query.answer(get_text('invalid_game_data', lang=lang), show_alert=True)
            return
            
        _, game_type, game_id, row, col = data_parts
        try:
            row, col = int(row), int(col)
            if not (0 <= row <= 2 and 0 <= col <= 2):
                raise ValueError("Invalid coordinates")
        except ValueError:
            await callback_query.answer(get_text('invalid_move_coordinates', lang=lang), show_alert=True)
            return
            
        # Проверка на активную игру
        if game_type == "bot":
            if callback_query.from_user.id not in bot_games:
                await callback_query.answer(get_text('game_not_found', lang=lang), show_alert=True)
                return
        else:
            try:
                game_id_tuple = eval(game_id)
                if not isinstance(game_id_tuple, tuple) or len(game_id_tuple) != 2:
                    raise ValueError("Invalid game ID")
            except:
                await callback_query.answer(get_text('invalid_game_data', lang=lang), show_alert=True)
                return
                
            current_games = premium_games if game_type == "premium" else games
            if game_id_tuple not in current_games:
                await callback_query.answer(get_text('game_not_found', lang=lang), show_alert=True)
                return
                
        # Обработка игры с ботом
        if game_type == "bot":
            game = bot_games[callback_query.from_user.id]
            board = game['board']
            
            if board[row][col] != " ":
                await callback_query.answer(get_text('cell_occupied', lang=lang), show_alert=True)
                return
                
            # Ход игрока
            board[row][col] = "X"
            
            # Проверка на победу игрока
            winner = check_win(board)
            if winner:
                if winner == "X":
                    await update_bot_game_state(
                        callback_query.from_user.id,
                        board,
                        'bot_game_over_win'
                    )
                elif winner == "Draw":
                    await update_bot_game_state(
                        callback_query.from_user.id,
                        board,
                        'bot_game_over_draw'
                    )
                del bot_games[callback_query.from_user.id]
                return
                
            # Ход бота
            await callback_query.answer(get_text('bot_thinking', lang=lang))
            bot_move = await make_bot_move(board)
            if bot_move:
                bot_row, bot_col = bot_move
                board[bot_row][bot_col] = "O"
                
                winner = check_win(board)
                if winner:
                    if winner == "O":
                        await update_bot_game_state(
                            callback_query.from_user.id,
                            board,
                            'bot_game_over_lose'
                        )
                    elif winner == "Draw":
                        await update_bot_game_state(
                            callback_query.from_user.id,
                            board,
                            'bot_game_over_draw'
                        )
                    del bot_games[callback_query.from_user.id]
                else:
                    await update_bot_game_state(
                        callback_query.from_user.id,
                        board,
                        'bot_game_state',
                        current_player="X"
                    )
            return
            
        # Обработка игры с игроком
        game = current_games[game_id_tuple]
        board, current_player, msg_ids = game
        
        if callback_query.from_user.id not in game_id_tuple:
            await callback_query.answer(get_text('not_participant', lang=lang), show_alert=True)
            return
            
        # Проверка очереди хода
        is_first_player = callback_query.from_user.id == game_id_tuple[0]
        if (is_first_player and current_player != "X") or (not is_first_player and current_player != "O"):
            await callback_query.answer(get_text('not_your_turn', lang=lang), show_alert=True)
            return
            
        if board[row][col] != " ":
            await callback_query.answer(get_text('cell_occupied', lang=lang), show_alert=True)
            return
            
        # Выполнение хода
        board[row][col] = current_player
        next_player = "O" if current_player == "X" else "X"
        game[1] = next_player
        
        # Обновление сообщений
        try:
            game_title = get_text('premium_game' if game_type == "premium" else 'regular_game', lang=lang)
            await callback_query.message.edit_text(
                get_text('game_state', lang=lang,
                    game_type=game_title,
                    player_name=await get_user_info(game_id_tuple[1] if is_first_player else game_id_tuple[0]),
                    current_player=next_player
                ),
                reply_markup=create_game_keyboard(board, next_player, game_type, game_id)
            )
            
            # Обновление сообщения оппонента
            opponent_id = game_id_tuple[1] if is_first_player else game_id_tuple[0]
            opponent_message_id = msg_ids.get(opponent_id)
            if opponent_message_id:
                opponent_lang = user_languages.get(opponent_id, 'en')
                try:
                    await bot.edit_message_text(
                        get_text('game_state', lang=opponent_lang,
                            game_type=game_title,
                            player_name=await get_user_info(callback_query.from_user.id),
                            current_player=next_player
                        ),
                        chat_id=opponent_id,
                        message_id=opponent_message_id,
                        reply_markup=create_game_keyboard(board, next_player, game_type, game_id)
                    )
                except Exception as e:
                    print(f"Error updating opponent's message: {e}")
                    
            # Проверка на окончание игры
            winner = check_win(board)
            if winner:
                await handle_game_end(
                    callback_query,
                    game_id_tuple,
                    winner,
                    board,
                    game_type,
                    current_games,
                    msg_ids
                )
                
        except Exception as e:
            print(f"Error updating game state: {e}")
            await callback_query.answer(get_text('error_updating_game', lang=lang), show_alert=True)
            
    except Exception as e:
        print(f"Error in process_callback: {e}")
        await callback_query.answer(get_text('error_occurred', lang=lang), show_alert=True)

async def handle_game_end(callback_query, game_id_tuple, winner, board, game_type, current_games, msg_ids):
    player1_id, player2_id = game_id_tuple
    is_first_player = callback_query.from_user.id == player1_id
    
    lang = user_languages.get(callback_query.from_user.id, 'en')
    opponent_id = player2_id if is_first_player else player1_id
    opponent_lang = user_languages.get(opponent_id, 'en')
    
    game_title = get_text('premium_game' if game_type == "premium" else 'regular_game', lang=lang)
    
    # Обновление рейтингов
    ratings.setdefault(player1_id, 0)
    ratings.setdefault(player2_id, 0)
    
    if winner == "Draw":
        draw_points = 2 if game_type == "premium" else 1
        ratings[player1_id] += draw_points
        ratings[player2_id] += draw_points
        
        # Отправка сообщений о ничьей
        await callback_query.message.edit_text(
            get_text('game_over', lang=lang,
                game_type=game_title,
                result='draw',
                points=draw_points
            ),
            reply_markup=create_game_keyboard(board, None, game_type, str(game_id_tuple))
        )
        
        if msg_ids.get(opponent_id):
            await bot.edit_message_text(
                get_text('game_over', lang=opponent_lang,
                    game_type=game_title,
                    result='draw',
                    points=draw_points
                ),
                chat_id=opponent_id,
                message_id=msg_ids[opponent_id],
                reply_markup=create_game_keyboard(board, None, game_type, str(game_id_tuple))
            )
    else:
        winner_id = player1_id if winner == "X" else player2_id
        loser_id = player2_id if winner == "X" else player1_id
        
        # Расчет очков
        win_points = 7 if winner_id in premium_users else 5
        lose_points = 3 if loser_id in premium_users else 5
        
        if game_type == "premium":
            win_points += 2
            
        ratings[winner_id] += win_points
        ratings[loser_id] = max(0, ratings[loser_id] - lose_points)
        
        # Отправка сообщений о победе/поражении
        if callback_query.from_user.id == winner_id:
            await callback_query.message.edit_text(
                get_text('game_over', lang=lang,
                    game_type=game_title,
                    result='win',
                    points=win_points
                ),
                reply_markup=create_game_keyboard(board, None, game_type, str(game_id_tuple))
            )
            
            if msg_ids.get(opponent_id):
                await bot.edit_message_text(
                    get_text('game_over', lang=opponent_lang,
                        game_type=game_title,
                        result='lose',
                        points=-lose_points
                    ),
                    chat_id=opponent_id,
                    message_id=msg_ids[opponent_id],
                    reply_markup=create_game_keyboard(board, None, game_type, str(game_id_tuple))
                )
        else:
            await callback_query.message.edit_text(
                get_text('game_over', lang=lang,
                    game_type=game_title,
                    result='lose',
                    points=-lose_points
                ),
                reply_markup=create_game_keyboard(board, None, game_type, str(game_id_tuple))
            )
            
            if msg_ids.get(opponent_id):
                await bot.edit_message_text(
                    get_text('game_over', lang=opponent_lang,
                        game_type=game_title,
                        result='win',
                        points=win_points
                    ),
                    chat_id=opponent_id,
                    message_id=msg_ids[opponent_id],
                    reply_markup=create_game_keyboard(board, None, game_type, str(game_id_tuple))
                )
                
    # Удаление игры
    del current_games[game_id_tuple]

@dp.callback_query(lambda c: c.data == "occupied")
async def occupied_cell_callback(callback_query: types.CallbackQuery):
    lang = user_languages.get(callback_query.from_user.id, 'en')
    await callback_query.answer(get_text('cell_occupied', lang=lang), show_alert=True)

async def start_game(player1, player2, first_player, is_premium_game):
    try:
        # Basic validation
        if None in (player1, player2) or player1 == player2:
            print("Cannot start game with same player")
            return False
            
        if is_premium_game and (player1 not in premium_users or player2 not in premium_users):
            print("Non-premium user in premium game")
            lang1 = user_languages.get(player1, 'en')
            lang2 = user_languages.get(player2, 'en')
            await bot.send_message(player1, get_text('premium_only', lang=lang1))
            await bot.send_message(player2, get_text('premium_only', lang=lang2))
            return False
            
        # Check if players are already in a game
        for players in list(games.keys()) + list(premium_games.keys()):
            if player1 in players or player2 in players:
                print(f"Player already in game: {player1} or {player2}")
                lang1 = user_languages.get(player1, 'en')
                lang2 = user_languages.get(player2, 'en')
                await bot.send_message(player1, get_text('already_in_game', lang=lang1))
                await bot.send_message(player2, get_text('already_in_game', lang=lang2))
                if is_premium_game:
                    if player1 not in players:
                        premium_lobby.append(player1)
                    if player2 not in players:
                        premium_lobby.append(player2)
                else:
                    if player1 not in players:
                        lobby.append(player1)
                    if player2 not in players:
                        lobby.append(player2)
                return False
                
        player1_name = await get_user_info(player1)
        player2_name = await get_user_info(player2)
        
        initial_board = [[" ", " ", " "], [" ", " ", " "], [" ", " ", " "]]
        game_id = str((player1, player2))
        game_type = "premium" if is_premium_game else "regular"
        
        first_player_id = player1 if first_player == "X" else player2
        second_player_id = player2 if first_player == "X" else player1
        first_player_name = player1_name if first_player == "X" else player2_name
        second_player_name = player2_name if first_player == "X" else player1_name
        
        lang1 = user_languages.get(first_player_id, 'en')
        lang2 = user_languages.get(second_player_id, 'en')
        
        game_title = get_text('premium_game' if is_premium_game else 'regular_game', lang=lang1)
        
        try:
            msg1 = await bot.send_message(
                first_player_id,
                get_text('game_started', lang=lang1,
                    game_type=game_title,
                    opponent=second_player_name,
                    symbol=first_player,
                    turn_text=get_text('your_turn', lang=lang1),
                    bonus=get_text('premium_bonus', lang=lang1) if is_premium_game else ''
                ),
                reply_markup=create_game_keyboard(initial_board, first_player, game_type, game_id)
            )
            
            msg2 = await bot.send_message(
                second_player_id,
                get_text('game_started', lang=lang2,
                    game_type=game_title,
                    opponent=first_player_name,
                    symbol='O' if first_player == 'X' else 'X',
                    turn_text=get_text('wait_turn', lang=lang2),
                    bonus=get_text('premium_bonus', lang=lang2) if is_premium_game else ''
                ),
                reply_markup=create_game_keyboard(initial_board, first_player, game_type, game_id)
            )
            
            game_data = [initial_board, first_player, {
                first_player_id: msg1.message_id,
                second_player_id: msg2.message_id
            }]
            
            if is_premium_game:
                premium_games[(player1, player2)] = game_data
            else:
                games[(player1, player2)] = game_data
            return True
                
        except Exception as e:
            print(f"Error starting game: {e}")
            lang1 = user_languages.get(player1, 'en')
            lang2 = user_languages.get(player2, 'en')
            await bot.send_message(player1, get_text('error_starting_game', lang=lang1))
            await bot.send_message(player2, get_text('error_starting_game', lang=lang2))
            # Return players to appropriate lobby
            if is_premium_game:
                premium_lobby.extend([player1, player2])
            else:
                lobby.extend([player1, player2])
            return False
            
    except Exception as e:
        print(f"Error in game setup: {e}")
        # Return players to appropriate lobby
        if is_premium_game:
            premium_lobby.extend([player1, player2])
        else:
            lobby.extend([player1, player2])
        return False

@dp.message(Command("donate"))
async def donate_command(message: types.Message):
    lang = user_languages.get(message.from_user.id, 'en')
    if message.from_user.id in premium_users:
        await message.answer(
            "🌟 " + get_text('premium_active', lang=lang) + "\n\n" +
            get_text('premium_benefits', lang=lang)
        )
        return
        
    await message.answer(
        "🌟 " + get_text('premium_offer', lang=lang) + "\n\n" +
        get_text('premium_benefits', lang=lang) + "\n\n" +
        "💳 " + get_text('payment_info', lang=lang)
    )

@dp.message(Command("play_bot"))
async def play_bot_command(message: types.Message):
    lang = user_languages.get(message.from_user.id, 'en')
    try:
        user_id = message.from_user.id
        
        # Проверка на активные игры
        if user_id in bot_games:
            await message.answer(get_text('already_in_bot_game', lang=lang))
            return
            
        # Проверка на участие в других играх
        for players in list(games.keys()) + list(premium_games.keys()):
            if user_id in players:
                await message.answer(get_text('already_in_game', lang=lang))
                return
                
        # Удаление из лобби при необходимости
        if user_id in lobby:
            lobby.remove(user_id)
            await message.answer(get_text('left_lobby_joined_bot', lang=lang))
        elif user_id in premium_lobby:
            premium_lobby.remove(user_id)
            await message.answer(get_text('left_lobby_joined_bot', lang=lang))
            
        initial_board = [[" ", " ", " "], [" ", " ", " "], [" ", " ", " "]]
        game_id = str(user_id)
        
        try:
            msg = await bot.send_message(
                user_id,
                get_text('game_with_bot', lang=lang),
                reply_markup=create_game_keyboard(initial_board, "X", "bot", game_id)
            )
            
            bot_games[user_id] = {
                'board': initial_board,
                'current_player': "X",
                'message_id': msg.message_id
            }
            
        except Exception as e:
            print(f"Error starting bot game: {e}")
            if user_id in bot_games:
                del bot_games[user_id]
            await message.answer(get_text('error_starting_game', lang=lang))
            
    except Exception as e:
        print(f"Error in play_bot_command: {e}")
        if message.from_user.id in bot_games:
            del bot_games[message.from_user.id]
        await message.answer(get_text('error_occurred', lang=lang))

async def make_bot_move(board):
    def evaluate_board(board):
        if check_win(board) == "O":
            return 10
        if check_win(board) == "X":
            return -10
        return 0

    def minimax(board, depth, is_maximizing):
        score = evaluate_board(board)
        
        if score != 0:
            return score - depth
        if all(cell != " " for row in board for cell in row):
            return 0
            
        if is_maximizing:
            best_score = float('-inf')
            for i in range(3):
                for j in range(3):
                    if board[i][j] == " ":
                        board[i][j] = "O"
                        score = minimax(board, depth + 1, False)
                        board[i][j] = " "
                        best_score = max(score, best_score)
            return best_score
        else:
            best_score = float('inf')
            for i in range(3):
                for j in range(3):
                    if board[i][j] == " ":
                        board[i][j] = "X"
                        score = minimax(board, depth + 1, True)
                        board[i][j] = " "
                        best_score = min(score, best_score)
            return best_score

    best_score = float('-inf')
    best_move = [0, 0]  # Инициализируем значением по умолчанию
    
    for i in range(3):
        for j in range(3):
            if board[i][j] == " ":
                board[i][j] = "O"
                score = minimax(board, 0, False)
                board[i][j] = " "
                
                if score > best_score:
                    best_score = score
                    best_move = [i, j]
                    
    # Добавляем случайность только если есть свободные клетки
    empty_cells = [(i, j) for i in range(3) for j in range(3) if board[i][j] == " "]
    if empty_cells and random.randint(0, 100) < 10:  # Уменьшаем вероятность случайного хода до 10%
        i, j = random.choice(empty_cells)
        return [i, j]
        
    return best_move

async def update_bot_game_state(user_id, board, message_key, **kwargs):
    try:
        game = bot_games.get(user_id)
        if not game:
            return
            
        lang = user_languages.get(user_id, 'en')
        
        # Проверяем валидность доски
        if not isinstance(board, list) or len(board) != 3 or any(len(row) != 3 for row in board):
            print(f"Invalid board state for user {user_id}")
            return
            
        # Специальная обработка для окончания игры
        if message_key == 'game_over':
            result = kwargs.get('result', 'draw')
            if result not in ['win', 'lose', 'draw']:
                print(f"Invalid game result: {result}")
                result = 'draw'
            message = get_text(f'bot_game_over_{result}', lang=lang)
        else:
            try:
                message = get_text(message_key, lang=lang, **kwargs)
            except KeyError as e:
                print(f"Error formatting message: {e}")
                message = get_text('error_occurred', lang=lang)
            
        try:
            await bot.edit_message_text(
                message,
                chat_id=user_id,
                message_id=game['message_id'],
                reply_markup=create_game_keyboard(board, "X", "bot", str(user_id))
            )
        except Exception as e:
            print(f"Error updating bot game message: {e}")
            # Пытаемся отправить новое сообщение, если не удалось отредактировать старое
            try:
                msg = await bot.send_message(
                    user_id,
                    message,
                    reply_markup=create_game_keyboard(board, "X", "bot", str(user_id))
                )
                game['message_id'] = msg.message_id
            except Exception as e:
                print(f"Error sending new bot game message: {e}")
                
    except Exception as e:
        print(f"Error updating bot game state: {e}")

async def lobby_random():
    while True:
        try:
            # Check premium lobby
            if len(premium_lobby) >= 2:
                players = premium_lobby[:2]
                # Проверяем, что игроки не в игре и имеют премиум
                if all(player in premium_users and 
                       player not in bot_games and
                       not any(player in game for game in list(games.keys()) + list(premium_games.keys()))
                       for player in players):
                    player1 = premium_lobby.pop(0)
                    player2 = premium_lobby.pop(0)
                    first_player = "X" if random.randint(0, 1) == 0 else "O"
                    if not await start_game(player1, player2, first_player, True):
                        # Возвращаем игроков в лобби при неудаче
                        if player1 not in premium_lobby and not any(player1 in game for game in list(games.keys()) + list(premium_games.keys())):
                            premium_lobby.append(player1)
                        if player2 not in premium_lobby and not any(player2 in game for game in list(games.keys()) + list(premium_games.keys())):
                            premium_lobby.append(player2)
            
            # Check regular lobby
            if len(lobby) >= 2:
                players = lobby[:2]
                # Проверяем, что игроки не в игре
                if all(player not in bot_games and
                       not any(player in game for game in list(games.keys()) + list(premium_games.keys()))
                       for player in players):
                    player1 = lobby.pop(0)
                    player2 = lobby.pop(0)
                    first_player = "X" if random.randint(0, 1) == 0 else "O"
                    if not await start_game(player1, player2, first_player, False):
                        # Возвращаем игроков в лобби при неудаче
                        if player1 not in lobby and not any(player1 in game for game in list(games.keys()) + list(premium_games.keys())):
                            lobby.append(player1)
                        if player2 not in lobby and not any(player2 in game for game in list(games.keys()) + list(premium_games.keys())):
                            lobby.append(player2)
                
        except Exception as e:
            print(f"Error in lobby_random: {e}")
            
        await asyncio.sleep(1)

if __name__ == "__main__":
    async def main():
        lobby_task = None
        try:
            lobby_task = asyncio.create_task(lobby_random())
            await dp.start_polling(bot)
        except KeyboardInterrupt:
            print("Bot stopped gracefully")
        except Exception as e:
            print(f"Error in main: {e}")
        finally:
            if lobby_task:
                lobby_task.cancel()
                try:
                    await lobby_task
                except asyncio.CancelledError:
                    pass

    import asyncio
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped gracefully")
