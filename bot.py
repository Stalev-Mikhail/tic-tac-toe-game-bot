import aiogram
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def check_win(board):
    # Проверка горизонтальных линий
    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2] != " ":
            return board[i][0]
            
    # Проверка вертикальных линий
    for i in range(3):
        if board[0][i] == board[1][i] == board[2][i] != " ":
            return board[0][i]
            
    # Проверка диагоналей
    if board[0][0] == board[1][1] == board[2][2] != " ":
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != " ":
        return board[0][2]
        
    # Проверка на ничью
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
premium_lobby = []  # Лобби для премиум игроков
games = {}  # (player1, player2): [board, current_player, message_ids]
premium_games = {}  # Отдельный словарь для премиум игр
message_ids = {}  # user_id: message_id
ratings = {}  # user_id: rating
premium_users = set()  # Множество ID премиум пользователей
ADMIN_ID = 5635916497  # ID администратора

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
    await message.answer("Hello! I'm a Tic-Tac-Toe game bot. To start the game, enter the /lobby command.")

@dp.message(Command("lobby"))
async def lobby_command(message: types.Message):
    if message.from_user.id in lobby:
        await message.answer("You are already in the lobby.")
    else:
        for i in list(games.keys()):
            if message.from_user.id in i:
                await message.answer("You are already in a game.")
                break
        else:
            lobby.append(message.from_user.id)
            await message.answer("You have joined the lobby. Waiting for another player...")

@dp.message(Command("move"))
async def move_command(message: types.Message):
    try:
        coordinates = list(map(int, message.text.split()[1:]))
        if len(coordinates) != 2 or not all(1 <= x <= 3 for x in coordinates):
            await message.answer("Invalid coordinates. Please enter two numbers between 1 and 3 separated by a space.")
            return
    except:
        await message.answer("Invalid format. Please use: /move <row> <column>")
        return

    for pair, game in games.items():
        if message.from_user.id in pair:
            board, current_player = game
            if (message.from_user.id == pair[0] and current_player != "X") or \
               (message.from_user.id == pair[1] and current_player != "O"):
                await message.answer("It's not your turn!")
                return

            col, row = coordinates[0] - 1, coordinates[1] - 1
            if board[row][col] != " ":
                await message.answer("This cell is already occupied!")
                return

            board[row][col] = current_player
            game[1] = "O" if current_player == "X" else "X"

            board_str = "\n".join([
                f"{row[0]} | {row[1]} | {row[2]}"
                for row in board
            ])
            
            await message.answer(f"Your move:\n{board_str}")
            await bot.send_message(
                pair[1] if message.from_user.id == pair[0] else pair[0],
                f"Opponent's move:\n{board_str}"
            )

            winner = check_win(board)
            if winner:
                if winner == "Draw":
                    await message.answer("It's a draw!")
                    await bot.send_message(
                        pair[1] if message.from_user.id == pair[0] else pair[0],
                        "It's a draw!"
                    )
                else:
                    winner_id = pair[0] if winner == "X" else pair[1]
                    if message.from_user.id == winner_id:
                        await message.answer("Congratulations! You won!")
                        await bot.send_message(
                            pair[1] if message.from_user.id == pair[0] else pair[0],
                            "You lost!"
                        )
                    else:
                        await message.answer("You lost!")
                        await bot.send_message(
                            pair[0] if message.from_user.id == pair[1] else pair[1],
                            "Congratulations! You won!"
                        )
                del games[pair]
            return
    await message.answer("You are not in an active game. Use /lobby to join a game.")

@dp.message(Command("cancel"))
async def cancel_command(message: types.Message):
    if message.from_user.id in lobby:
        lobby.remove(message.from_user.id)
        await message.answer("You have left the lobby.")
    else:
        if message.from_user.id in premium_lobby:
            premium_lobby.remove(message.from_user.id)
            await message.answer("You have left the premium lobby.")
        else:
            await message.answer("You are not in any lobby.")

@dp.message(Command("rating"))
async def rating_command(message: types.Message):
    user_id = message.from_user.id
    rating = ratings.get(user_id, 0)
    user_name = await get_user_info(user_id)
    await message.answer(f"{user_name}, your rating: {rating}")

@dp.message(Command("top"))
async def top_command(message: types.Message):
    if not ratings:
        await message.answer("No games have been played yet!")
        return
        
    # Sort players by rating
    sorted_players = sorted(ratings.items(), key=lambda x: x[1], reverse=True)
    
    # Form top-3
    response = "🏆 Top Players:\n\n"
    for i, (player_id, rating) in enumerate(sorted_players[:3], 1):
        try:
            player_name = await get_user_info(player_id)
            if i == 1:
                response += f"🥇 {player_name}: {rating}\n"
            elif i == 2:
                response += f"🥈 {player_name}: {rating}\n"
            elif i == 3:
                response += f"🥉 {player_name}: {rating}\n"
        except:
            continue
            
    await message.answer(response)

@dp.message(Command("premium_lobby"))
async def premium_lobby_command(message: types.Message):
    if message.from_user.id not in premium_users:
        await message.answer("This command is only available for premium users!")
        return
        
    if message.from_user.id in premium_lobby:
        await message.answer("You are already in the premium lobby.")
    else:
        for i in list(games.keys()):
            if message.from_user.id in i:
                await message.answer("You are already in a game.")
                break
        else:
            premium_lobby.append(message.from_user.id)
            await message.answer("You have joined the premium lobby. Waiting for another premium player...")

@dp.message(Command("give_premium"))
async def give_premium_command(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("You don't have permission to use this command!")
        return
        
    try:
        # Format: /give_premium user_id
        user_id = int(message.text.split()[1])
        premium_users.add(user_id)
        user_name = await get_user_info(user_id)
        await message.answer(f"Premium status granted to {user_name}!")
        try:
            await bot.send_message(
                user_id, 
                "🌟 Congratulations! You've been granted premium status!\n"
                "Your benefits:\n"
                "- Reduced rating loss on defeat (-3 instead of -5)\n"
                "- Increased rating gain on victory (+7 instead of +5)\n"
                "- Access to premium lobby (/premium_lobby)\n"
                "- Additional +2 rating points in premium games!"
            )
        except:
            print(f"Failed to send message to user {user_id}")
    except:
        await message.answer("Usage: /give_premium user_id")

@dp.message(Command("remove_premium"))
async def remove_premium_command(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("You don't have permission to use this command!")
        return
        
    try:
        user_id = int(message.text.split()[1])
        if user_id in premium_users:
            premium_users.remove(user_id)
            user_name = await get_user_info(user_id)
            await message.answer(f"Premium status removed from {user_name}")
            try:
                await bot.send_message(user_id, "Your premium status has been deactivated.")
            except:
                print(f"Failed to send message to user {user_id}")
    except:
        await message.answer("Usage: /remove_premium user_id")

@dp.message(Command("help"))
async def help_command(message: types.Message):
    base_commands = (
        "Available commands:\n"
        "/lobby - Join the game lobby\n"
        "/cancel - Leave the lobby\n"
        "/rating - Check your rating\n"
        "/top - Show top 3 players"
    )
    
    if message.from_user.id in premium_users:
        premium_commands = "\n\n🌟 Premium commands:\n/premium_lobby - Join premium players lobby"
        await message.answer(base_commands + premium_commands)
    else:
        await message.answer(base_commands)

def create_game_keyboard(board, current_player, game_type, game_id):
    keyboard = []
    for i in range(3):
        row = []
        for j in range(3):
            text = board[i][j] if board[i][j] != " " else "⬜"
            row.append(InlineKeyboardButton(
                text=text,
                callback_data=f"move_{game_type}_{game_id}_{i}_{j}" if board[i][j] == " " else "occupied"
            ))
        keyboard.append(row)
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

@dp.callback_query(lambda c: c.data.startswith('move_'))
async def process_callback(callback_query: types.CallbackQuery):
    try:
        _, game_type, game_id, row, col = callback_query.data.split('_')
        row, col = int(row), int(col)
        
        # Select the appropriate games dictionary
        current_games = premium_games if game_type == "premium" else games
        
        for pair, game in current_games.items():
            if str(pair) == game_id:
                board, current_player, message_ids = game
                if (callback_query.from_user.id == pair[0] and current_player != "X") or \
                   (callback_query.from_user.id == pair[1] and current_player != "O"):
                    await callback_query.answer("It's not your turn!", show_alert=True)
                    return

                if board[row][col] != " ":
                    await callback_query.answer("This cell is already occupied!", show_alert=True)
                    return

                board[row][col] = current_player
                game[1] = "O" if current_player == "X" else "X"

                try:
                    await callback_query.message.edit_text(
                        f"{'🌟 Premium' if game_type == 'premium' else ''} Game state:\n{callback_query.from_user.first_name}'s move",
                        reply_markup=create_game_keyboard(board, current_player, game_type, str(pair))
                    )

                    opponent_id = pair[1] if callback_query.from_user.id == pair[0] else pair[0]
                    opponent_message_id = message_ids.get(opponent_id)
                    if opponent_message_id:
                        try:
                            await bot.edit_message_text(
                                f"{'🌟 Premium' if game_type == 'premium' else ''} Game state:\n{callback_query.from_user.first_name}'s turn",
                                chat_id=opponent_id,
                                message_id=opponent_message_id,
                                reply_markup=create_game_keyboard(board, current_player, game_type, str(pair))
                            )
                        except Exception as e:
                            print(f"Error updating opponent's message: {e}")

                    winner = check_win(board)
                    if winner:
                        player1_id = pair[0]
                        player2_id = pair[1]
                        
                        if player1_id not in ratings:
                            ratings[player1_id] = 0
                        if player2_id not in ratings:
                            ratings[player2_id] = 0
                            
                        if winner == "Draw":
                            # Draw gives +2 points in premium games
                            draw_points = 2 if game_type == "premium" else 1
                            ratings[player1_id] += draw_points
                            ratings[player2_id] += draw_points
                            await callback_query.message.edit_text(
                                f"{'🌟 Premium ' if game_type == 'premium' else ''}Game Draw!\n"
                                f"Your rating: {ratings[player1_id]} (+{draw_points})"
                            )
                            if opponent_message_id:
                                await bot.edit_message_text(
                                    f"{'🌟 Premium ' if game_type == 'premium' else ''}Game Draw!\n"
                                    f"Your rating: {ratings[opponent_id]} (+{draw_points})", 
                                    chat_id=opponent_id, 
                                    message_id=opponent_message_id
                                )
                        else:
                            winner_id = pair[0] if winner == "X" else pair[1]
                            loser_id = pair[1] if winner == "X" else pair[0]
                            
                            # Premium bonuses
                            win_points = 7 if winner_id in premium_users else 5
                            lose_points = 3 if loser_id in premium_users else 5
                            
                            # Additional points for premium game victory
                            if game_type == "premium":
                                win_points += 2
                            
                            ratings[winner_id] += win_points
                            ratings[loser_id] = max(0, ratings[loser_id] - lose_points)
                            
                            if callback_query.from_user.id == winner_id:
                                await callback_query.message.edit_text(
                                    f"{'🌟 Premium ' if game_type == 'premium' else ''}Game Victory!\n"
                                    f"Congratulations! You won!\nYour rating: {ratings[winner_id]} (+{win_points})"
                                )
                                if opponent_message_id:
                                    await bot.edit_message_text(
                                        f"{'🌟 Premium ' if game_type == 'premium' else ''}Game Over!\n"
                                        f"You lost!\nYour rating: {ratings[loser_id]} (-{lose_points})", 
                                        chat_id=opponent_id, 
                                        message_id=opponent_message_id
                                    )
                            else:
                                await callback_query.message.edit_text(
                                    f"{'🌟 Premium ' if game_type == 'premium' else ''}Game Over!\n"
                                    f"You lost!\nYour rating: {ratings[loser_id]} (-{lose_points})"
                                )
                                if opponent_message_id:
                                    await bot.edit_message_text(
                                        f"{'🌟 Premium ' if game_type == 'premium' else ''}Game Victory!\n"
                                        f"Congratulations! You won!\nYour rating: {ratings[winner_id]} (+{win_points})", 
                                        chat_id=opponent_id, 
                                        message_id=opponent_message_id
                                    )
                        del current_games[pair]
                except Exception as e:
                    print(f"Error updating game state: {e}")
                    await callback_query.answer("Error updating game state. Please try again.", show_alert=True)
                return

        await callback_query.answer("Game not found!", show_alert=True)
    except Exception as e:
        print(f"Error processing callback: {e}")
        await callback_query.answer("An error occurred. Please try again.", show_alert=True)

async def lobby_random():
    import random
    while True:
        try:
            # Проверяем премиум лобби
            if len(premium_lobby) >= 2:
                player1 = premium_lobby.pop(0)
                player2 = premium_lobby.pop(0)
                first_player = "X" if random.randint(0, 1) == 0 else "O"
                await start_game(player1, player2, first_player, True)
            
            # Проверяем обычное лобби
            if len(lobby) >= 2:
                player1 = lobby.pop(0)
                player2 = lobby.pop(0)
                first_player = "X" if random.randint(0, 1) == 0 else "O"
                await start_game(player1, player2, first_player, False)
                
            await asyncio.sleep(1)
        except Exception as e:
            print(f"Error in lobby_random: {e}")
            await asyncio.sleep(1)

async def start_game(player1, player2, first_player, is_premium_game):
    try:
        player1_name = await get_user_info(player1)
        player2_name = await get_user_info(player2)
        
        initial_board = [[" ", " ", " "], [" ", " ", " "], [" ", " ", " "]]
        game_id = str((player1, player2))
        game_type = "premium" if is_premium_game else "regular"
        
        try:
            first_player_id = player1 if first_player == "X" else player2
            second_player_id = player2 if first_player == "X" else player1
            first_player_name = player1_name if first_player == "X" else player2_name
            second_player_name = player2_name if first_player == "X" else player1_name
            
            game_title = "🌟 Premium game" if is_premium_game else "Game"
            msg1 = await bot.send_message(
                first_player_id,
                f"{game_title} started!\n"
                f"You have been matched with {second_player_name}. You are {first_player}. Your turn!"
                f"{' (Premium bonus: +2 rating for win!)' if is_premium_game else ''}",
                reply_markup=create_game_keyboard(initial_board, first_player, game_type, game_id)
            )
            
            msg2 = await bot.send_message(
                second_player_id,
                f"{game_title} started!\n"
                f"You have been matched with {first_player_name}. You are {'O' if first_player == 'X' else 'X'}. Wait for your turn!"
                f"{' (Premium bonus: +2 rating for win!)' if is_premium_game else ''}",
                reply_markup=create_game_keyboard(initial_board, first_player, game_type, game_id)
            )
            
            # Сохраняем игру в соответствующий словарь
            game_data = [initial_board, first_player, {
                first_player_id: msg1.message_id,
                second_player_id: msg2.message_id
            }]
            
            if is_premium_game:
                premium_games[(player1, player2)] = game_data
            else:
                games[(player1, player2)] = game_data
            
            print(f"{game_title} started between {first_player_name} and {second_player_name}")
        except Exception as e:
            print(f"Error sending game start messages: {e}")
            if is_premium_game:
                if (player1, player2) in premium_games:
                    del premium_games[(player1, player2)]
                premium_lobby.extend([player1, player2])
            else:
                if (player1, player2) in games:
                    del games[(player1, player2)]
                lobby.extend([player1, player2])
    except Exception as e:
        print(f"Error in game setup: {e}")

if __name__ == "__main__":
    async def main():
        try:
            asyncio.create_task(lobby_random())
            await dp.start_polling(bot)
        except KeyboardInterrupt:
            print("Bot stopped gracefully")
        except Exception as e:
            print(f"Error in main: {e}")

    import asyncio
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped gracefully")
