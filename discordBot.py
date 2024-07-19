

import discord
from discord.ext import commands
from discord import app_commands
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import os


#Edit this with your own specifications
bot_token = ""
channel_id = 0  # channel in which bot is listening
spreadsheet_id = ""  # google sheet id


def getToken():
    # If modifying these scopes, delete the file token.json.
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds


bot = commands.Bot(command_prefix='.',intents=discord.Intents.all())

@bot.event
async def on_ready():
    await bot.tree.sync()


@bot.tree.command(name='log', description='Log an expense')
async def log(interaction: discord.Interaction, expense: float, reason: str):
    if interaction.channel.id == channel_id:
        if expense > 0:
            await interaction.response.send_message(content=f"Added expense of ${expense} for {reason}")
        else:
            await interaction.response.send_message(content=f"Added expense of -${expense*-1} for {reason}")
        values = [[str(interaction.created_at.date()),expense,reason]]
        sheet.values().append(
            spreadsheetId=spreadsheet_id,
            range="Sheet1!A:C",
            valueInputOption="RAW",
            body={"values": values}
        ).execute()


@bot.tree.command(name='undo',description='Undo the most recent log')
async def undo(interaction):
    if interaction.channel.id == channel_id:
        await interaction.response.send_message(content="Deleted most recent log")
        #Find bottom row
        result = (
            sheet.values()
            .get(spreadsheetId=spreadsheet_id, range="A:C")
            .execute()
        )
        rows = result.get("values", [])
        bottom_row = len(rows)
        #Delete bottom row
        if bottom_row > 1:
            sheet.values().update(
                spreadsheetId=spreadsheet_id,
                range=f"Sheet1!A{bottom_row}:C{bottom_row}",
                valueInputOption="RAW",
                body={"values": [['','','']]}
            ).execute()




def authenticate_sheets(creds):
    return build('sheets','v4',credentials=creds).spreadsheets()


if __name__ == '__main__':
    creds = getToken()
    sheet = authenticate_sheets(creds)
    bot.run(bot_token)



