import aiogram
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
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
    await message.answer(
        "👋 Welcome to Tic-Tac-Toe Bot!\n\n"
        "🎮 Play against other players or try your luck against the bot!\n\n"
        "Available commands:\n"
        "/play - Join regular game lobby\n"
        "/play_bot - Play against bot\n"
        "/premium_lobby - Join premium lobby (premium only)\n"
        "/rating - Check your rating\n"
        "/top - View top players\n"
        "/donate - Get premium status\n"
        "/help - Show all commands"
    )

@dp.message(Command("lobby"))
async def lobby_command(message: types.Message):
    if message.from_user.id in lobby or message.from_user.id in premium_lobby:
        await message.answer("You are already in the lobby.")
        return
        
    for i in list(games.keys()) + list(premium_games.keys()):
        if message.from_user.id in i:
            await message.answer("You are already in a game.")
            return
            
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

    # Check both regular and premium games
    for pair, game in {**games, **premium_games}.items():
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
                # Remove from appropriate games dictionary
                if pair in premium_games:
                    del premium_games[pair]
                else:
                    del games[pair]
            return
    await message.answer("You are not in an active game. Use /lobby to join a game.")

@dp.message(Command("cancel"))
async def cancel_command(message: types.Message):
    user_id = message.from_user.id
    
    if user_id in lobby:
        lobby.remove(user_id)
        await message.answer("🚪 You have left the lobby.")
        return
        
    if user_id in premium_lobby:
        premium_lobby.remove(user_id)
        await message.answer("🚪 You have left the premium lobby.")
        return
        
    if user_id in bot_games:
        del bot_games[user_id]
        await message.answer("🚪 You have left the game with bot.")
        return
        
    for game_dict in [games, premium_games]:
        for players, game_data in list(game_dict.items()):
            if user_id in players:
                opponent_id = players[1] if user_id == players[0] else players[0]
                del game_dict[players]
                await message.answer("🚪 You have left the game.")
                try:
                    await bot.send_message(opponent_id, "❌ Your opponent has left the game.")
                except:
                    pass
                return
                
    await message.answer("❓ You are not in any lobby or game.")

@dp.message(Command("rating"))
async def rating_command(message: types.Message):
    user_id = message.from_user.id
    rating = ratings.get(user_id, 0)
    status = "🌟 Premium" if user_id in premium_users else "👤 Regular"
    
    await message.answer(
        f"Your Status: {status}\n"
        f"Current Rating: {rating} points"
    )

@dp.message(Command("top"))
async def top_command(message: types.Message):
    if not ratings:
        await message.answer("🎮 No games have been played yet!")
        return
        
    sorted_ratings = sorted(ratings.items(), key=lambda x: x[1], reverse=True)
    top_10 = sorted_ratings[:10]
    
    response = "🏆 Top Players:\n\n"
    medals = ["🥇", "🥈", "🥉"]
    
    for i, (player_id, rating) in enumerate(top_10):
        try:
            user = await bot.get_chat(player_id)
            name = user.first_name
            medal = medals[i] if i < 3 else "👤"
            premium = "🌟" if player_id in premium_users else ""
            response += f"{medal} {name} {premium}: {rating} points\n"
        except:
            continue
            
    await message.answer(response)

@dp.message(Command("premium_lobby"))
async def premium_lobby_command(message: types.Message):
    if message.from_user.id not in premium_users:
        await message.answer("This command is only available for premium users!")
        return
        
    if message.from_user.id in premium_lobby or message.from_user.id in lobby:
        await message.answer("You are already in a lobby.")
        return
        
    for i in list(games.keys()) + list(premium_games.keys()):
        if message.from_user.id in i:
            await message.answer("You are already in a game.")
            return
            
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
                "- Increased rating gain (+7 instead of +5)\n"
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
    is_premium = message.from_user.id in premium_users
    
    basic_commands = (
        "📋 Basic Commands:\n"
        "/play - Join regular game lobby\n"
        "/play_bot - Play against bot\n"
        "/cancel - Leave current game or lobby\n"
        "/rating - Check your rating\n"
        "/top - View top players\n"
        "/donate - Get premium status\n"
    )
    
    premium_commands = (
        "\n🌟 Premium Commands:\n"
        "/premium_lobby - Join premium lobby\n"
    ) if is_premium else "\n🔒 Get premium status to access more features!"
    
    await message.answer(basic_commands + premium_commands)

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
    try:
        data_parts = callback_query.data.split('_')
        if len(data_parts) != 5:
            await callback_query.answer("Invalid game data!", show_alert=True)
            return
            
        _, game_type, game_id, row, col = data_parts
        row, col = int(row), int(col)
        
        if row < 0 or row > 2 or col < 0 or col > 2:
            await callback_query.answer("Invalid move coordinates!", show_alert=True)
            return
            
        # Handle bot game
        if game_type == "bot":
            game = bot_games.get(callback_query.from_user.id)
            if not game:
                await callback_query.answer("Game not found!", show_alert=True)
                return
                
            board = game['board']
            if board[row][col] != " ":
                await callback_query.answer("This cell is already occupied!", show_alert=True)
                return
                
            # Player's move
            board[row][col] = "X"
            game['board'] = board
            
            # Check for player win
            winner = check_win(board)
            if winner == "X":
                await update_bot_game_state(
                    callback_query.from_user.id, 
                    board, 
                    format_game_over_message("bot", "win")
                )
                del bot_games[callback_query.from_user.id]
                return
                
            if winner == "Draw":
                await update_bot_game_state(
                    callback_query.from_user.id, 
                    board, 
                    format_game_over_message("bot", "draw")
                )
                del bot_games[callback_query.from_user.id]
                return
                
            # Bot's move
            bot_move = await make_bot_move(board)
            if bot_move:
                bot_row, bot_col = bot_move
                board[bot_row][bot_col] = "O"
                game['board'] = board
                
                # Check for bot win
                winner = check_win(board)
                if winner == "O":
                    await update_bot_game_state(
                        callback_query.from_user.id, 
                        board, 
                        format_game_over_message("bot", "lose")
                    )
                    del bot_games[callback_query.from_user.id]
                    return
                    
                if winner == "Draw":
                    await update_bot_game_state(
                        callback_query.from_user.id, 
                        board, 
                        format_game_over_message("bot", "draw")
                    )
                    del bot_games[callback_query.from_user.id]
                    return
                    
                await update_bot_game_state(
                    callback_query.from_user.id, 
                    board, 
                    format_board_message("bot", "X", is_bot_game=True)
                )
            return
            
        # Handle regular and premium games
        current_games = premium_games if game_type == "premium" else games
        
        try:
            game_id_tuple = eval(game_id)
            if not isinstance(game_id_tuple, tuple) or len(game_id_tuple) != 2:
                raise ValueError("Invalid game ID format")
        except Exception as e:
            print(f"Error parsing game ID: {e}")
            await callback_query.answer("Invalid game data!", show_alert=True)
            return
            
        game = current_games.get(game_id_tuple)
        if not game:
            await callback_query.answer("Game not found!", show_alert=True)
            return
            
        board, current_player, msg_ids = game
        
        if callback_query.from_user.id not in game_id_tuple:
            await callback_query.answer("You are not a participant in this game!", show_alert=True)
            return
            
        if (callback_query.from_user.id == game_id_tuple[0] and current_player != "X") or \
           (callback_query.from_user.id == game_id_tuple[1] and current_player != "O"):
            await callback_query.answer("It's not your turn!", show_alert=True)
            return

        if board[row][col] != " ":
            await callback_query.answer("This cell is already occupied!", show_alert=True)
            return

        board[row][col] = current_player
        next_player = "O" if current_player == "X" else "X"
        game[1] = next_player

        try:
            await callback_query.message.edit_text(
                format_board_message(game_type, next_player, callback_query.from_user.first_name),
                reply_markup=create_game_keyboard(board, next_player, game_type, game_id)
            )

            opponent_id = game_id_tuple[1] if callback_query.from_user.id == game_id_tuple[0] else game_id_tuple[0]
            opponent_message_id = msg_ids.get(opponent_id)
            
            if opponent_message_id:
                try:
                    await bot.edit_message_text(
                        format_board_message(game_type, next_player, callback_query.from_user.first_name),
                        chat_id=opponent_id,
                        message_id=opponent_message_id,
                        reply_markup=create_game_keyboard(board, next_player, game_type, game_id)
                    )
                except Exception as e:
                    print(f"Error updating opponent's message: {e}")

            winner = check_win(board)
            if winner:
                player1_id = game_id_tuple[0]
                player2_id = game_id_tuple[1]
                
                ratings.setdefault(player1_id, 0)
                ratings.setdefault(player2_id, 0)
                
                if winner == "Draw":
                    draw_points = 2 if game_type == "premium" else 1
                    ratings[player1_id] += draw_points
                    ratings[player2_id] += draw_points
                    
                    await callback_query.message.edit_text(
                        format_game_over_message(game_type, "draw", draw_points),
                        reply_markup=create_game_keyboard(board, next_player, game_type, game_id)
                    )
                    
                    if opponent_message_id:
                        await bot.edit_message_text(
                            format_game_over_message(game_type, "draw", draw_points),
                            chat_id=opponent_id,
                            message_id=opponent_message_id,
                            reply_markup=create_game_keyboard(board, next_player, game_type, game_id)
                        )
                else:
                    winner_id = game_id_tuple[0] if winner == "X" else game_id_tuple[1]
                    loser_id = game_id_tuple[1] if winner == "X" else game_id_tuple[0]
                    
                    win_points = 7 if winner_id in premium_users else 5
                    lose_points = 3 if loser_id in premium_users else 5
                    
                    if game_type == "premium":
                        win_points += 2
                    
                    ratings[winner_id] += win_points
                    ratings[loser_id] = max(0, ratings[loser_id] - lose_points)
                    
                    if callback_query.from_user.id == winner_id:
                        await callback_query.message.edit_text(
                            format_game_over_message(game_type, "win", win_points),
                            reply_markup=create_game_keyboard(board, next_player, game_type, game_id)
                        )
                        if opponent_message_id:
                            await bot.edit_message_text(
                                format_game_over_message(game_type, "lose", -lose_points),
                                chat_id=opponent_id,
                                message_id=opponent_message_id,
                                reply_markup=create_game_keyboard(board, next_player, game_type, game_id)
                            )
                    else:
                        await callback_query.message.edit_text(
                            format_game_over_message(game_type, "lose", -lose_points),
                            reply_markup=create_game_keyboard(board, next_player, game_type, game_id)
                        )
                        if opponent_message_id:
                            await bot.edit_message_text(
                                format_game_over_message(game_type, "win", win_points),
                                chat_id=opponent_id,
                                message_id=opponent_message_id,
                                reply_markup=create_game_keyboard(board, next_player, game_type, game_id)
                            )
                
                del current_games[game_id_tuple]
                
        except Exception as e:
            print(f"Error updating game state: {e}")
            await callback_query.answer("Error updating game state. Please try again.", show_alert=True)
            return

    except Exception as e:
        print(f"Error processing callback: {e}")
        await callback_query.answer("An error occurred. Please try again.", show_alert=True)

@dp.callback_query(lambda c: c.data == "occupied")
async def occupied_cell_callback(callback_query: types.CallbackQuery):
    await callback_query.answer("This cell is already occupied!", show_alert=True)

async def start_game(player1, player2, first_player, is_premium_game):
    try:
        # Basic validation
        if None in (player1, player2) or player1 == player2:
            print("Cannot start game with same player")
            return
            
        if is_premium_game and (player1 not in premium_users or player2 not in premium_users):
            print("Non-premium user in premium game")
            return
            
        # Check if players are already in a game
        for players in list(games.keys()) + list(premium_games.keys()):
            if player1 in players or player2 in players:
                print(f"Player already in game: {player1} or {player2}")
                if is_premium_game:
                    premium_lobby.extend([player1, player2])
                else:
                    lobby.extend([player1, player2])
                return
                
        player1_name = await get_user_info(player1)
        player2_name = await get_user_info(player2)
        
        initial_board = [[" ", " ", " "], [" ", " ", " "], [" ", " ", " "]]
        game_id = str((player1, player2))
        game_type = "premium" if is_premium_game else "regular"
        
        first_player_id = player1 if first_player == "X" else player2
        second_player_id = player2 if first_player == "X" else player1
        first_player_name = player1_name if first_player == "X" else player2_name
        second_player_name = player2_name if first_player == "X" else player1_name
        
        game_title = "🌟 Premium game" if is_premium_game else "Game"
        
        try:
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
            
            game_data = [initial_board, first_player, {
                first_player_id: msg1.message_id,
                second_player_id: msg2.message_id
            }]
            
            if is_premium_game:
                premium_games[(player1, player2)] = game_data
            else:
                games[(player1, player2)] = game_data
                
        except Exception as e:
            print(f"Error starting game: {e}")
            # Return players to appropriate lobby
            if is_premium_game:
                premium_lobby.extend([player1, player2])
            else:
                lobby.extend([player1, player2])
            raise
            
    except Exception as e:
        print(f"Error in game setup: {e}")
        # Return players to appropriate lobby
        if is_premium_game:
            premium_lobby.extend([player1, player2])
        else:
            lobby.extend([player1, player2])

@dp.message(Command("donate"))
async def donate_command(message: types.Message):
    if message.from_user.id in premium_users:
        await message.answer(
            "🌟 You already have premium status!\n\n"
            "Your benefits:\n"
            "✨ Reduced rating loss (-3 instead of -5)\n"
            "✨ Increased rating gain (+7 instead of +5)\n"
            "✨ Access to premium lobby (/premium_lobby)\n"
            "✨ Additional +2 rating points in premium games!"
        )
        return
        
    await message.answer(
        "🌟 Get Premium Status!\n\n"
        "Benefits:\n"
        "✨ Reduced rating loss (-3 instead of -5)\n"
        "✨ Increased rating gain (+7 instead of +5)\n"
        "✨ Access to premium lobby (/premium_lobby)\n"
        "✨ Additional +2 rating points in premium games!\n\n"
        "💳 Payment Information:\n"
        "Price: $5/month\n"
        "Contact @admin for details"
    )

@dp.message(Command("play_bot"))
async def play_bot_command(message: types.Message):
    try:
        # Check if user is already in a game
        if message.from_user.id in bot_games:
            await message.answer("You are already in a game with the bot!")
            return
            
        # Create new bot game
        initial_board = [[" ", " ", " "], [" ", " ", " "], [" ", " ", " "]]
        game_id = str(message.from_user.id)
        
        try:
            msg = await bot.send_message(
                message.from_user.id,
                "Game with bot started!\nYou are X. Your turn!",
                reply_markup=create_game_keyboard(initial_board, "X", "bot", game_id)
            )
            
            bot_games[message.from_user.id] = {
                'board': initial_board,
                'current_player': "X",
                'message_id': msg.message_id
            }
            
        except Exception as e:
            print(f"Error starting bot game: {e}")
            await message.answer("Error starting game. Please try again.")
            
    except Exception as e:
        print(f"Error in play_bot_command: {e}")
        await message.answer("An error occurred. Please try again.")

async def make_bot_move(board):
    # Improved bot logic with priority:
    # 1. Win if possible
    # 2. Block opponent's win
    # 3. Take center
    # 4. Take corner
    # 5. Take any available cell
    
    # Check for win
    for i in range(3):
        for j in range(3):
            if board[i][j] == " ":
                board[i][j] = "O"
                if check_win(board) == "O":
                    board[i][j] = " "
                    return i, j
                board[i][j] = " "
                
    # Block opponent's win
    for i in range(3):
        for j in range(3):
            if board[i][j] == " ":
                board[i][j] = "X"
                if check_win(board) == "X":
                    board[i][j] = " "
                    return i, j
                board[i][j] = " "
    
    # Take center
    if board[1][1] == " ":
        return 1, 1
        
    # Take corner
    corners = [(0,0), (0,2), (2,0), (2,2)]
    random.shuffle(corners)
    for i, j in corners:
        if board[i][j] == " ":
            return i, j
            
    # Take any available cell
    for i in range(3):
        for j in range(3):
            if board[i][j] == " ":
                return i, j
                
    return None

async def update_bot_game_state(user_id, board, message):
    try:
        game = bot_games.get(user_id)
        if not game:
            return
            
        await bot.edit_message_text(
            f"🤖 {message}",
            chat_id=user_id,
            message_id=game['message_id'],
            reply_markup=create_game_keyboard(board, "X", "bot", str(user_id))
        )
    except Exception as e:
        print(f"Error updating bot game state: {e}")

async def lobby_random():
    while True:
        try:
            # Check premium lobby
            if len(premium_lobby) >= 2:
                players = premium_lobby[:2]
                if all(player in premium_users for player in players):
                    player1 = premium_lobby.pop(0)
                    player2 = premium_lobby.pop(0)
                    first_player = "X" if random.randint(0, 1) == 0 else "O"
                    await start_game(player1, player2, first_player, True)
            
            # Check regular lobby
            if len(lobby) >= 2:
                player1 = lobby.pop(0)
                player2 = lobby.pop(0)
                first_player = "X" if random.randint(0, 1) == 0 else "O"
                await start_game(player1, player2, first_player, False)
                
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
