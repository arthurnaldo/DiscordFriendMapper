import discord
import sqlite3
from discord.ext import commands
import nest_asyncio
from pyvis.network import Network
from dotenv import load_dotenv
import os

# Allow nested event loops for Flask + Discord bot combo
nest_asyncio.apply()

# Load environment variables from .env file
load_dotenv()

# Load Discord token from an environment variable (safer than hardcoding)
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
print("TOKEN loaded:", TOKEN)  # Debug line to check token loading

# Set up Discord bot intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

# Initialize the bot with a command prefix and the intents
bot = commands.Bot(command_prefix='!', intents=intents)

# SQLite database setup
def setup_db():
    """Set up the SQLite database with necessary tables."""
    conn = sqlite3.connect('interactions.db')
    c = conn.cursor()
    
    # Create messages table if it doesn't exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            message_id INTEGER PRIMARY KEY,
            user_id INTEGER,
            user_name TEXT,
            content TEXT,
            channel_name TEXT,
            server_name TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create interactions table if it doesn't exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS interactions (
            interaction_id INTEGER PRIMARY KEY,
            message_id INTEGER,
            reply_to_message_id INTEGER,
            FOREIGN KEY (message_id) REFERENCES messages(message_id),
            FOREIGN KEY (reply_to_message_id) REFERENCES messages(message_id)
        )
    ''')
    
    conn.commit()
    conn.close()

setup_db()

def insert_user_if_not_exists(user):
    """Insert user into the messages table if they do not exist already."""
    conn = sqlite3.connect('interactions.db')
    c = conn.cursor()
    
    c.execute('SELECT 1 FROM messages WHERE user_id = ?', (user.id,))
    result = c.fetchone()
    
    if not result:
        # User does not exist, insert them
        c.execute('''
            INSERT INTO messages (user_id, user_name)
            VALUES (?, ?)
        ''', (user.id, user.name))
        conn.commit()
    
    conn.close()

def insert_message(message):
    """Insert message into the database."""
    conn = sqlite3.connect('interactions.db')
    c = conn.cursor()
    
    insert_user_if_not_exists(message.author)  # Ensure user exists before inserting message
    
    c.execute('''
        INSERT INTO messages (message_id, user_id, user_name, content, channel_name, server_name)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (message.id, message.author.id, message.author.name, message.content, message.channel.name, message.guild.name))
    
    conn.commit()
    conn.close()

def insert_interaction(message, reply_to_message):
    """Insert interaction between messages into the database."""
    conn = sqlite3.connect('interactions.db')
    c = conn.cursor()
    
    insert_user_if_not_exists(message.author)  # Ensure user exists before inserting interaction
    insert_user_if_not_exists(reply_to_message.author)  # Ensure replied-to user exists
    
    c.execute('''
        INSERT INTO interactions (message_id, reply_to_message_id)
        VALUES (?, ?)
    ''', (message.id, reply_to_message.id))
    
    conn.commit()
    conn.close()

def create_interactive_graph_from_sql(server_name):
    """Create an interactive graph of message interactions from the database."""
    conn = sqlite3.connect('interactions.db')
    c = conn.cursor()

    net = Network()

    # Filter messages by server name
    c.execute('SELECT user_name, message_id FROM messages WHERE server_name = ?', (server_name,))
    messages = c.fetchall()

    message_counts = {}
    for user_name, message_id in messages:
        message_counts[user_name] = message_counts.get(user_name, 0) + 1

    for user_name, count in message_counts.items():
        # Add nodes for each user
        net.add_node(user_name, label=user_name, value=count)

        c.execute('SELECT reply_to_message_id FROM interactions WHERE message_id IN (SELECT message_id FROM messages WHERE user_name = ? AND server_name = ?)', (user_name, server_name))
        replies = c.fetchall()

        interaction_counts = {}
        for reply in replies:
            reply_to_message_id = reply[0]
            c.execute('SELECT user_name FROM messages WHERE message_id = ?', (reply_to_message_id,))
            reply_user_name = c.fetchone()

            if reply_user_name:
                reply_user_name = reply_user_name[0]
                
                # Add reply user as a node if not already added
                if reply_user_name not in net.nodes:
                    net.add_node(reply_user_name, label=reply_user_name, value=0)

                edge_key = tuple(sorted([user_name, reply_user_name]))
                interaction_counts[edge_key] = interaction_counts.get(edge_key, 0) + 1

        # Add edges (interactions) between nodes
        for edge_key, count in interaction_counts.items():
            user_a, user_b = edge_key
            net.add_edge(user_a, user_b, title=f'Interactions: {count}', value=count)

    # Save graph with server-specific name
    graph_filename = f'./static/{server_name}_interaction_graph.html'
    net.save_graph(graph_filename)
    conn.close()

@bot.event
async def on_ready():
    """Notify when the bot is ready."""
    print(f'Logged in as {bot.user}')

@bot.event
async def on_message(message):
    """Handle incoming messages."""
    print(f"Message received: {message.content}") 
    if message.author == bot.user:
        return  # Ignore bot's own messages

    insert_message(message)
    if message.reference:
        referenced_message = await message.channel.fetch_message(message.reference.message_id)
        insert_interaction(message, referenced_message)

    # No longer regenerate the graph here. Instead, trigger via Flask API.
    await bot.process_commands(message)

if __name__ == '__main__':
    bot.run(TOKEN)
